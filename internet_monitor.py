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
HOST_TO_PING = "8.8.8.8"     # Google's DNS - the host we'll ping
PING_TIMEOUT = 1            # Ping timeout (in seconds)
CHECK_INTERVAL = 10         # How often (in seconds) to ping
ICON_SIZE = 64              # Size (in pixels) of the tray icon

# Threshold (in milliseconds) to decide green vs red
THRESHOLD = 500  # 500 ms

tray_icon = None
stop_event = threading.Event()

def create_icon_with_text(text, color):
    """
    Create an icon image of size ICON_SIZE x ICON_SIZE with a
    black/transparent background, and draw the given text in 'color'.
    """
    # Create a transparent background (RGBA)
    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Use a built-in default font for portability
    # or you can specify a TTF (e.g. ImageFont.truetype("arial.ttf", 32))
    font = ImageFont.load_default()

    # Measure text size to center it
    text_width, text_height = draw.textsize(text, font=font)
    x = (ICON_SIZE - text_width) // 2
    y = (ICON_SIZE - text_height) // 2

    # Draw the text
    draw.text((x, y), text, fill=color, font=font)

    return img

def ping_and_update():
    """
    Continuously ping the target host and update the tray icon image
    with text showing the ping in ms. The text is green if fast,
    red if slow or no response.
    """
    global tray_icon

    while not stop_event.is_set():
        start_time = time.time()
        response_time = ping(HOST_TO_PING, timeout=PING_TIMEOUT)
        end_time = time.time()

        if response_time is None:
            # No response
            text = "X"  # or "NR" or something to indicate no response
            color = "red"
            tooltip = "No response"
        else:
            # Convert to ms
            response_ms = response_time * 1000
            # If <= threshold => green, else => red
            if response_ms <= THRESHOLD:
                color = "green"
            else:
                color = "red"
            text = f"{int(response_ms)}"
            tooltip = f"{int(response_ms)} ms"

        # Create the tray icon image with text
        icon_image = create_icon_with_text(text, color)

        # Update tray icon
        tray_icon.icon = icon_image
        tray_icon.title = tooltip

        # Adjust sleep time
        elapsed = end_time - start_time
        time_to_sleep = max(0, CHECK_INTERVAL - elapsed)
        time.sleep(time_to_sleep)

def on_quit(icon, item):
    """
    Handle "Quit" from the tray menu.
    """
    stop_event.set()
    icon.stop()

def setup_tray_icon():
    """
    Setup pystray Icon with an initial image and a simple menu.
    """
    global tray_icon
    initial_image = create_icon_with_text("...", "gray")

    menu = Menu(
        item("Quit", on_quit)
    )

    tray_icon = pystray.Icon(
        "Connection Monitor", 
        icon=initial_image, 
        title="Initializing...", 
        menu=menu
    )

def main():
    setup_tray_icon()

    # Start thread that pings continuously
    monitor_thread = threading.Thread(target=ping_and_update, daemon=True)
    monitor_thread.start()

    tray_icon.run()

if __name__ == "__main__":
    # Run this script with pythonw.exe to hide the console:
    #   pythonw.exe your_script.py
    main()
