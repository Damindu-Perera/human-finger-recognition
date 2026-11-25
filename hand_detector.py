
import cv2
import mediapipe as mp


class HandDetector:

    def __init__(
        self,
        max_hands=2,
        detection_confidence=0.7,
        tracking_confidence=0.7
    ):

        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands

        # Drawing utilities
        self.mp_draw = mp.solutions.drawing_utils

        # Hand landmark drawing styles
        self.landmark_style = self.mp_draw.DrawingSpec(
            color=(0, 255, 0),
            thickness=2,
            circle_radius=3
        )

        self.connection_style = self.mp_draw.DrawingSpec(
            color=(255, 0, 255),
            thickness=2
        )

        # Processing resolution
        # Increased from 256x192 for better landmark accuracy
        self.processing_width = 480
        self.processing_height = 360

        # Initialize MediaPipe Hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            model_complexity=0,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )

    def find_hands(self, image, draw=True):

        # Original image dimensions
        image_height, image_width, _ = image.shape

        # Convert BGR image to RGB
        rgb_image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        # Resize image for MediaPipe processing
        small_rgb_image = cv2.resize(
            rgb_image,
            (
                self.processing_width,
                self.processing_height
            ),
            interpolation=cv2.INTER_AREA
        )

        # Prevent unnecessary image copying during inference
        small_rgb_image.flags.writeable = False

        # Process image
        results = self.hands.process(small_rgb_image)

        # Restore writeability
        small_rgb_image.flags.writeable = True

        detected_hands = []

        # Process detected hands
        if results.multi_hand_landmarks:

            for index, hand_landmarks in enumerate(
                results.multi_hand_landmarks
            ):

                # Draw landmarks on original image
                if draw:

                    self.mp_draw.draw_landmarks(
                        image,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.landmark_style,
                        self.connection_style
                    )

                # Extract landmarks
                landmarks = []

                for landmark_id, landmark in enumerate(
                    hand_landmarks.landmark
                ):

                    x_normalized = landmark.x
                    y_normalized = landmark.y
                    z_normalized = landmark.z

                    # Convert normalized coordinates to original
                    # camera image pixel coordinates
                    x_pixel = int(
                        x_normalized * image_width
                    )

                    y_pixel = int(
                        y_normalized * image_height
                    )

                    landmarks.append({
                        "id": landmark_id,
                        "x": x_normalized,
                        "y": y_normalized,
                        "z": z_normalized,
                        "pixel_x": x_pixel,
                        "pixel_y": y_pixel
                    })

                # Determine handedness
                hand_label = "Unknown"
                hand_confidence = 0.0

                if results.multi_handedness:

                    classification = (
                        results.multi_handedness[index]
                        .classification[0]
                    )

                    hand_label = classification.label
                    hand_confidence = classification.score

                # Calculate bounding box
                x_coordinates = [
                    landmark["pixel_x"]
                    for landmark in landmarks
                ]

                y_coordinates = [
                    landmark["pixel_y"]
                    for landmark in landmarks
                ]

                bounding_box = {
                    "x_min": min(x_coordinates),
                    "y_min": min(y_coordinates),
                    "x_max": max(x_coordinates),
                    "y_max": max(y_coordinates)
                }

                # Store complete hand information
                hand_data = {
                    "label": hand_label,
                    "confidence": hand_confidence,
                    "landmarks": landmarks,
                    "bounding_box": bounding_box
                }

                detected_hands.append(hand_data)

        return image, detected_hands

    def close(self):

        # Release MediaPipe resources
        self.hands.close()
