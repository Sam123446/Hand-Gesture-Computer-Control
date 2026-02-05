import time
import pyautogui
from utils import distance
from hud import show_text

# Cooldown timers
last_click_time = 0
last_double_click_time = 0
last_zoom_time = 0
last_screenshot_time = 0

def handle_gestures(lm, w, h, frame, prev_x, prev_y, screen_w, screen_h, dragging):
    global last_click_time, last_double_click_time, last_zoom_time, last_screenshot_time

    index, middle, thumb, wrist = lm[8], lm[12], lm[4], lm[0]

    # Distances
    pinch_dist = distance(index, thumb, w, h)
    double_click_dist = distance(index, middle, w, h)
    zoom_dist = distance(index, thumb, w, h)
    wrist_close_dist = distance(wrist, index, w, h)

    # CLICK
    if pinch_dist < 20 and time.time() - last_click_time > 0.8:
        pyautogui.click()
        show_text(frame, "CLICK", (30, 50), (0,255,0))
        last_click_time = time.time()

    # DOUBLE CLICK
    if double_click_dist < 15 and time.time() - last_double_click_time > 1:
        pyautogui.doubleClick()
        show_text(frame, "DOUBLE CLICK", (30, 90), (255,0,0))
        last_double_click_time = time.time()

    # DRAG
    fingers_folded = (
        lm[8].y > lm[6].y and
        lm[12].y > lm[10].y and
        lm[16].y > lm[14].y and
        lm[20].y > lm[18].y
    )
    if fingers_folded and not dragging:
        pyautogui.mouseDown()
        dragging = True
        show_text(frame, "DRAGGING", (30, 130), (0,0,255))
    if not fingers_folded and dragging:
        pyautogui.mouseUp()
        dragging = False

    # SCREENSHOT
    if wrist_close_dist < 30 and time.time() - last_screenshot_time > 2:
        import time as t
        filename = f"screenshots/screenshot_{t.strftime('%Y%m%d_%H%M%S')}.png"
        pyautogui.screenshot(filename)
        show_text(frame, "SCREENSHOT SAVED", (30, 170), (255,255,0))
        last_screenshot_time = time.time()

    # ZOOM
    if zoom_dist > 60 and time.time() - last_zoom_time > 1:
        pyautogui.hotkey('ctrl', '+')
        show_text(frame, "ZOOM IN", (30, 250), (0,200,200))
        last_zoom_time = time.time()
    elif zoom_dist < 30 and time.time() - last_zoom_time > 1:
        pyautogui.hotkey('ctrl', '-')
        show_text(frame, "ZOOM OUT", (30, 250), (0,200,200))
        last_zoom_time = time.time()

    return dragging
