import cv2
import mediapipe as mp
import pyautogui
import screen_brightness_control as sbc

# Initialize webcam
webcam = cv2.VideoCapture(0)

# MediaPipe Hands Model
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Screen Size
screen_width, screen_height = pyautogui.size()

# Initialize Variables
x1 = y1 = x2 = y2 = 0  # Thumb & Index Finger Coordinates (Left Hand)
x3 = y3 = x4 = y4 = 0  # Thumb & Index Finger Coordinates (Right Hand)

while True:
    success, image = webcam.read()
    image = cv2.flip(image, 1)  # Flip image for natural interaction
    frame_height, frame_width, _ = image.shape

    # Convert to RGB
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    output = hands.process(rgb_image)
    hand_landmarks = output.multi_hand_landmarks

    if hand_landmarks:
        for hand in hand_landmarks:
            mp_draw.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS)
            landmarks = hand.landmark

            # Determine which hand (Left or Right)
            hand_type = "Right" if landmarks[0].x > 0.5 else "Left"

            for id, landmark in enumerate(landmarks):
                x = int(landmark.x * frame_width)
                y = int(landmark.y * frame_height)

                if id == 8:  # Index Finger Tip
                    cv2.circle(image, (x, y), 8, (0, 255, 255), -1)
                    if hand_type == "Left":
                        x1, y1 = x, y
                    else:
                        x3, y3 = x, y
                
                if id == 4:  # Thumb Tip
                    cv2.circle(image, (x, y), 8, (0, 0, 255), -1)
                    if hand_type == "Left":
                        x2, y2 = x, y
                    else:
                        x4, y4 = x, y

        # Volume Control (Left Hand)
        volume_dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        if volume_dist > 80:
            pyautogui.press("volumeup")  # Increase Volume
        elif volume_dist < 40:
            pyautogui.press("volumedown")  # Decrease Volume

        # Brightness Control (Right Hand)
        brightness_dist = ((x4 - x3) ** 2 + (y4 - y3) ** 2) ** 0.5
        if brightness_dist > 80:
            sbc.set_brightness(min(sbc.get_brightness()[0] + 10, 100))  # Increase Brightness
        elif brightness_dist < 40:
            sbc.set_brightness(max(sbc.get_brightness()[0] - 10, 0))  # Decrease Brightness

        

        # Scrolling Control (Right Hand - Based on Index Finger Vertical Movement)
        if y3 < frame_height // 3:  # Move Up → Scroll Up
            pyautogui.scroll(15)
        elif y3 > 2 * (frame_height // 3):  # Move Down → Scroll Down
            pyautogui.scroll(-15)

    # Display Output
    cv2.imshow("Gesture-Based Controls", image)

    key = cv2.waitKey(10)
    if key == 27:  # Press ESC to Exit
        break

webcam.release()
cv2.destroyAllWindows()
