import cv2

def show_text(frame, text, pos, color=(0,255,0)):
    cv2.putText(frame, text, pos,
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

def draw_circle(frame, lm, w, h, color=(0,255,255)):
    cx, cy = int(lm.x * w), int(lm.y * h)
    cv2.circle(frame, (cx, cy), 15, color, -1)
