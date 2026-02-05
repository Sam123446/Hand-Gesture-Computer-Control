import pyautogui
import os

# PyAutoGUI setup
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

# Screen size
screen_w, screen_h = pyautogui.size()

# Smoothening factor
smoothening = 7

# Screenshot folder
if not os.path.exists("screenshots"):
    os.makedirs("screenshots")
