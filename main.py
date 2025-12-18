import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import os
import math

# Disable pyautogui failsafe
pyautogui.FAILSAFE = False

# Screen size
screen_w, screen_h = pyautogui.size()

# MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6  # slightly reduced for speed
)
mp_draw = mp.solutions.drawing_utils

# Webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Smooth mouse movement
prev_x, prev_y = 0, 0
smoothening = 7

# Drag control
dragging = False

# Screenshot cooldown
last_screenshot_time = 0

# Process every nth frame
frame_count = 0
process_every_n = 2

if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

def distance(p1, p2, w, h):
    x1, y1 = int(p1.x * w), int(p1.y * h)
    x2, y2 = int(p2.x * w), int(p2.y * h)
    return math.hypot(x2 - x1, y2 - y1)

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    frame_count += 1

    # Only process every nth frame
    if frame_count % process_every_n != 0:
        cv2.imshow("Hand Controlled Computer", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
        continue

    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0]  # only first hand

        # Draw landmarks (optional, comment for speed)
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        lm = hand_landmarks.landmark

        index = lm[8]
        middle = lm[12]
        thumb = lm[4]
        ring = lm[16]
        pinky = lm[20]
        wrist = lm[0]

        # Cursor movement
        x = int(index.x * w)
        y = int(index.y * h)

        screen_x = np.interp(x, (0, w), (0, screen_w))
        screen_y = np.interp(y, (0, h), (0, screen_h))

        curr_x = prev_x + (screen_x - prev_x) / smoothening
        curr_y = prev_y + (screen_y - prev_y) / smoothening

        # Move mouse only if significant change
        if abs(curr_x - prev_x) > 1 or abs(curr_y - prev_y) > 1:
            pyautogui.moveTo(curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y

        # Distances for gestures
        pinch_dist = distance(index, thumb, w, h)
        double_click_dist = distance(index, middle, w, h)

        # LEFT CLICK (pinch)
        if pinch_dist < 30:
            pyautogui.click()
            cv2.putText(frame, "CLICK", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            time.sleep(0.2)

        # DOUBLE CLICK (index + middle)
        if double_click_dist < 30:
            pyautogui.doubleClick()
            cv2.putText(frame, "DOUBLE CLICK", (30, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            time.sleep(0.3)

        # DRAG (closed fist)
        fingers_folded = (
            lm[8].y > lm[6].y and
            lm[12].y > lm[10].y and
            lm[16].y > lm[14].y and
            lm[20].y > lm[18].y
        )

        if fingers_folded and not dragging:
            pyautogui.mouseDown()
            dragging = True
            cv2.putText(frame, "DRAGGING", (30, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if not fingers_folded and dragging:
            pyautogui.mouseUp()
            dragging = False

        # HAND SHAKE = SCREENSHOT
        shake_speed = abs(wrist.x - index.x) * w
        if shake_speed > 150 and time.time() - last_screenshot_time > 2:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/screenshot_{timestamp}.png"
            pyautogui.screenshot(filename)
            last_screenshot_time = time.time()
            cv2.putText(frame, "SCREENSHOT SAVED", (30, 170),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    # Display frame
    cv2.imshow("Hand Controlled Computer", frame)

    # ESC to exit
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
