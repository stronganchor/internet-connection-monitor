import os
import sys
import threading
import time

# -----------------------------
# Hide console window on Windows
# -----------------------------
if os.name == 'nt':
    import ctypes
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        # 0 = SW_HIDE
        ctypes.windll.user32.ShowWindow(whnd, 0)

from ping3 import ping
import pystray
from pystray import MenuItem as item, Menu
from PIL import Image, ImageDraw, ImageFont

# -----------------------------
# Configuration
# -----------------------------
HOST_TO_PING = "8.8.8.8"
PING_TIMEOUT = 1
CHECK_INTERVAL = 10
ICON_SIZE = 64
THRESHOLD = 500
FONT_SIZE = 42

tray_icon = None
stop_event = threading.Event()


def create_icon_with_text(text, color):
    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arialbd.ttf", FONT_SIZE)
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = (ICON_SIZE - w) // 2, (ICON_SIZE - h) // 2
    draw.text((x, y), text, fill=color, font=font)
    return img


def ping_and_update():
    global tray_icon
    while not stop_event.is_set():
        try:
            response = ping(HOST_TO_PING, timeout=PING_TIMEOUT)
        except Exception:
            response = None
        if response is None:
            text, color, tooltip = "X", "red", "No response"
        else:
            ms = int(response * 1000)
            color = "green" if ms <= THRESHOLD else "red"
            text, tooltip = str(ms), f"{ms} ms"
        tray_icon.icon = create_icon_with_text(text, color)
        tray_icon.title = tooltip
        time.sleep(CHECK_INTERVAL)


def on_quit(icon, item):
    stop_event.set()
    icon.stop()


def setup_tray_icon():
    global tray_icon
    init_img = create_icon_with_text("...", "gray")
    menu = Menu(item("Quit", on_quit))
    tray_icon = pystray.Icon("_Connection Monitor", init_img, "Initializing...", menu)


def main():
    setup_tray_icon()
    threading.Thread(target=ping_and_update, daemon=True).start()
    tray_icon.run()


if __name__ == "__main__":
    main()
