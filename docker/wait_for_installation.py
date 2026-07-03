#!/usr/bin/env python3
import time
import sys
import pyautogui

ASSETS_DIR = "assets"
TIMEOUT = 300
INTERVAL = 2


def locate_image(image_name, confidence=0.8):
    try:
        return pyautogui.locateCenterOnScreen(
            f"{ASSETS_DIR}/{image_name}", confidence=confidence
        )
    except Exception:
        return None


def wait_for_image(image_name, timeout=TIMEOUT, interval=INTERVAL):
    start = time.time()
    while time.time() - start < timeout:
        pos = locate_image(image_name)
        if pos:
            return pos
        time.sleep(interval)
    return None


def click_image(image_name):
    pos = locate_image(image_name)
    if pos:
        pyautogui.click(pos.x, pos.y)
        return True
    return False


def main():
    print("Checking for img1.png (installing)...")

    if locate_image("img1.png"):
        print("Found img1.png - installing MetaTrader 5...")
        print("Waiting for img2.png (installation complete)...")

        if wait_for_image("img2.png"):
            print("Found img2.png - clicking finish button...")
            click_image("img2.png")
            print("Waiting for img3.png (server connection label)...")

            if wait_for_image("img3.png"):
                print("Found img3.png - ready to connect with server!")
                return 0
            else:
                print("Timeout waiting for img3.png")
                return 1
        else:
            print("Timeout waiting for img2.png")
            return 1
    else:
        print("img1.png not found - installation may already be complete")
        if locate_image("img2.png"):
            print("Found img2.png - clicking finish button...")
            click_image("img2.png")

        if wait_for_image("img3.png"):
            print("Found img3.png - ready to connect with server!")
            return 0
        else:
            print("img3.png not found")
            return 1


if __name__ == "__main__":
    sys.exit(main())
