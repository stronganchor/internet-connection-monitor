import time
import threading
import sys
from ping3 import ping
import pystray
from pystray import MenuItem as item, Menu
from PIL import Image, ImageDraw, ImageFont

# -----------------------------
# Configuration
# -----------------------------
HOST_TO_PING = "8.8.8.8"     # The host we'll ping (Google DNS)
PING_TIMEOUT = 1            # Ping timeout (in seconds)
CHECK_INTERVAL = 10         # How often (in seconds) to ping
ICON_SIZE = 64              # Tray icon dimensions
THRESHOLD = 500             # Threshold in ms for "good" (green) vs. "slow" (red)
FONT_SIZE = 42              # Font size for the text on the tray icon

tray_icon = None
stop_event = threading.Event()

def create_icon_with_text(text, color):
    """
    Create a 64x64 icon (or ICON_SIZE x ICON_SIZE) with a 
    transparent background and draw 'text' in the given 'color'.
    """
    # Create a transparent (RGBA) image
    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Use a larger font for better visibility
    font = ImageFont.truetype("arialbd.ttf", FONT_SIZE)

    # Use textbbox to calculate the size of the text
    bbox = draw.textbbox((0, 0), text, font=font)  # Returns (left, top, right, bottom)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center the text
    x = (ICON_SIZE - text_width) // 2
    y = (ICON_SIZE - text_height) // 2

    # Draw the text
    draw.text((x, y), text, fill=color, font=font)

    return img

def ping_and_update():
    global tray_icon

    while not stop_event.is_set():
        start_time = time.time()

        try:
            response_time = ping(HOST_TO_PING, timeout=PING_TIMEOUT)
        except OSError as e:
            # Handle the error: network unreachable, etc.
            response_time = None
            # You could log the exception if you like:
            # print(f"OSError: {e}", file=sys.stderr)
        except Exception as e:
            # Catch all other exceptions so the thread doesn't die
            response_time = None
            # print(f"Exception: {e}", file=sys.stderr)

        end_time = time.time()

        # Now handle response_time just like before
        if response_time is None:
            text = "X"
            color = "red"
            tooltip = "No response"
        else:
            response_ms = response_time * 1000
            color = "green" if response_ms <= THRESHOLD else "red"
            text = f"{int(response_ms)}"
            tooltip = f"{int(response_ms)} ms"
        
        icon_image = create_icon_with_text(text, color)
        tray_icon.icon = icon_image
        tray_icon.title = tooltip

        elapsed = end_time - start_time
        time.sleep(max(0, CHECK_INTERVAL - elapsed))


def on_quit(icon, item):
    """
    Handle "Quit" from the tray menu. Stops the thread and removes the icon.
    """
    stop_event.set()
    icon.stop()

def setup_tray_icon():
    """
    Initialize the pystray Icon with an initial image and menu.
    """
    global tray_icon
    
    # Temporary initial icon (...) in gray
    initial_image = create_icon_with_text("...", "gray")

    menu = Menu(
        item("Quit", on_quit)
    )

    # Prefix the tray icon's name to sort it to the front
    tray_icon = pystray.Icon(
        "_Connection Monitor",  # Name prefixed with `_` to sort to front
        icon=initial_image,
        title="Initializing...",
        menu=menu
    )

def main():
    setup_tray_icon()

    # Start the background thread that does the ping checks
    monitor_thread = threading.Thread(target=ping_and_update, daemon=True)
    monitor_thread.start()

    # Start the tray icon event loop (blocks until "Quit")
    tray_icon.run()

if __name__ == "__main__":
    # Launch with pythonw.exe to hide the console window:
    #   pythonw.exe internet_monitor.py
    main()
