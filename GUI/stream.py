import cv2
import requests
import numpy as np
from io import BytesIO
import mediapipe as mp

# Function to detect and draw landmarks on the hand
def detect_hand_landmarks(image):
    with mp.solutions.hands.Hands() as hands:
        # Convert the BGR image to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image and get hand landmarks
        results = hands.process(image_rgb)

        # Draw landmarks on the image
        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    image, landmarks, mp.solutions.hands.HAND_CONNECTIONS)

# Replace the URL with your actual camera feed URL
url = 'http://172.20.10.3/html/cam_pic.php'

while True:
    # Request the image from the URL
    response = requests.get(url)

    if response.status_code == 200:
        # Read the image from the response content
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        # Detect and draw hand landmarks
        detect_hand_landmarks(img)

        # Display the image
        cv2.imshow('Live Image with Hand Landmarks', img)

    # Exit the loop when the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Close the OpenCV window
cv2.destroyAllWindows()
