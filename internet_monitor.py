import time
import threading
import sys
from ping3 import ping
import pystray
from pystray import MenuItem as item, Menu
from PIL import Image, ImageDraw

# -----------------------------
# Configuration
# -----------------------------
HOST_TO_PING = "8.8.8.8"     # Google's DNS - the host we'll ping
PING_TIMEOUT = 1            # 1-second ping timeout
CHECK_INTERVAL = 10         # How often (in seconds) to ping
ICON_SIZE = 64              # Size (in pixels) of the generated tray icon

# Define thresholds (in milliseconds)
GOOD_THRESHOLD = 200
MODERATE_THRESHOLD = 500

# Global references
tray_icon = None
stop_event = threading.Event()


def create_image(color):
    """
    Create a simple square image with a colored circle
    to use as a tray icon.
    """
    img = Image.new("RGB", (ICON_SIZE, ICON_SIZE), "white")
    draw = ImageDraw.Draw(img)
    # Draw a colored circle in the center
    circle_radius = ICON_SIZE // 2 - 4
    center = ICON_SIZE // 2
    draw.ellipse(
        (center - circle_radius, center - circle_radius,
         center + circle_radius, center + circle_radius),
        fill=color,
        outline=color
    )
    return img


def ping_and_update():
    """
    Continuously ping the target host and update the tray icon color & tooltip.
    Runs in a background thread until stop_event is set.
    """
    global tray_icon

    while not stop_event.is_set():
        start_time = time.time()
        response_time = ping(HOST_TO_PING, timeout=PING_TIMEOUT)
        end_time = time.time()

        # Convert response_time to milliseconds
        if response_time is not None:
            response_ms = response_time * 1000
        else:
            response_ms = None

        # Decide on color based on thresholds
        if response_ms is None:
            # No response
            color = "red"
            tooltip = "No response (connection lost)"
        else:
            if response_ms <= GOOD_THRESHOLD:
                color = "green"
            elif response_ms <= MODERATE_THRESHOLD:
                color = "orange"
            else:
                color = "red"
            tooltip = f"{response_ms:.0f} ms"

        # Create the tray icon image with the appropriate color
        icon_image = create_image(color)
        
        # Update tray icon with new image and tooltip
        tray_icon.icon = icon_image
        tray_icon.title = f"Ping: {tooltip}"

        # Sleep until next check, minus how long the ping took
        elapsed = end_time - start_time
        time_to_sleep = max(0, CHECK_INTERVAL - elapsed)
        time.sleep(time_to_sleep)


def on_quit(icon, item):
    """
    Handles the Quit menu item, signaling the background thread to stop
    and removing the tray icon.
    """
    stop_event.set()
    icon.stop()


def setup_tray_icon():
    """
    Setup the pystray Icon with an initial image and a menu.
    """
    global tray_icon

    # Placeholder image (will be updated soon by ping_and_update)
    initial_img = create_image("gray")
    
    # Create menu with a Quit option
    menu = Menu(
        item('Quit', on_quit)
    )
    
    # Create the tray icon
    tray_icon = pystray.Icon("Connection Monitor", icon=initial_img, title="Initializing...", menu=menu)


def main():
    setup_tray_icon()

    # Start background thread for pinging
    monitor_thread = threading.Thread(target=ping_and_update, daemon=True)
    monitor_thread.start()

    # Run the icon event loop (blocking call until the user quits)
    tray_icon.run()


if __name__ == "__main__":
    # If you want to hide the console, run as:
    # pythonw.exe script_name.py
    main()
