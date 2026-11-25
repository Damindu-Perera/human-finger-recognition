
# gesture_recognition.py


class GestureRecognizer:

    def __init__(self):

        # Define known hand gestures
        self.gestures = {
            "Open Palm": [True, True, True, True, True],
            "Fist": [False, False, False, False, False],
            "Peace": [False, True, True, False, False],
            "Three": [False, True, True, True, False],
            "Four": [False, True, True, True, True],
            "Pointing": [False, True, False, False, False],
            "Rock": [False, True, False, False, True],
            "Thumbs Up": [True, False, False, False, False]
        }

        # Finger order used by our system
        self.finger_order = [
            "Thumb",
            "Index",
            "Middle",
            "Ring",
            "Pinky"
        ]

    def get_finger_pattern(self, finger_results):

        """
        Convert finger detection results into a
        Boolean pattern.

        Example:

        [False, True, True, False, False]

        This means:
        Thumb  = Folded
        Index  = Raised
        Middle = Raised
        Ring   = Folded
        Pinky  = Folded
        """

        pattern = []

        for finger in self.finger_order:

            is_extended = (
                finger_results[finger]["extended"]
            )

            pattern.append(is_extended)

        return pattern

    def recognize_gesture(self, finger_results):

        """
        Identify the hand gesture using the
        detected finger pattern.
        """

        # Get the current finger pattern
        pattern = self.get_finger_pattern(
            finger_results
        )

        # Compare against known gestures
        for gesture_name, gesture_pattern in (
            self.gestures.items()
        ):

            if pattern == gesture_pattern:

                return {
                    "gesture": gesture_name,
                    "pattern": pattern,
                    "recognized": True
                }

        # If no known pattern matches
        return {
            "gesture": "Unknown",
            "pattern": pattern,
            "recognized": False
        }

    def get_gesture_description(self, gesture_name):

        descriptions = {
            "Open Palm": "All five fingers are raised",
            "Fist": "All five fingers are folded",
            "Peace": "Index and middle fingers are raised",
            "Three": "Three fingers are raised",
            "Four": "Four fingers are raised",
            "Pointing": "Only the index finger is raised",
            "Rock": "Index and pinky fingers are raised",
            "Thumbs Up": "Only the thumb is raised",
            "Unknown": "Gesture not recognized"
        }

        return descriptions.get(
            gesture_name,
            "Gesture not recognized"
        )
