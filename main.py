import cv2
import mediapipe as mp
import numpy as np
import time
from config import screen_w, screen_h, smoothening
from gestures import handle_gestures

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1,
                       min_detection_confidence=0.7,
                       min_tracking_confidence=0.6)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

prev_x, prev_y = 0, 0
dragging = False
frame_count = 0
process_every_n = 2
gesture_active = False

try:
    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        frame_count += 1
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('g'):
            gesture_active = not gesture_active
            print("Gesture Control", "ON" if gesture_active else "OFF")
            time.sleep(0.3)
        if key == 27:  # ESC
            break

        if frame_count % process_every_n != 0:
            cv2.imshow("Hand Controlled Computer", frame)
            continue

        if result.multi_hand_landmarks and gesture_active:
            hand_landmarks = result.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            lm = hand_landmarks.landmark

            # Mouse movement
            x, y = int(lm[8].x * w), int(lm[8].y * h)
            screen_x = np.interp(x, (0, w), (0, screen_w))
            screen_y = np.interp(y, (0, h), (0, screen_h))
            curr_x = prev_x + (screen_x - prev_x) / smoothening
            curr_y = prev_y + (screen_y - prev_y) / smoothening

            if abs(curr_x - prev_x) > 1 or abs(curr_y - prev_y) > 1:
                import pyautogui
                pyautogui.moveTo(curr_x, curr_y)
                prev_x, prev_y = curr_x, curr_y

            # Handle gestures
            dragging = handle_gestures(lm, w, h, frame, prev_x, prev_y, screen_w, screen_h, dragging)

        cv2.imshow("Hand Controlled Computer", frame)

except KeyboardInterrupt:
    print("Exited with Ctrl+C")

finally:
    cap.release()
    hands.close()
    cv2.destroyAllWindows()

