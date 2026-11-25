# landmark_quality.py

import math


class LandmarkQualityChecker:

    def __init__(
        self,
        minimum_landmarks=21,
        minimum_hand_width=0.05,
        minimum_hand_height=0.08,
        minimum_hand_area=0.003,
        minimum_handedness_confidence=0.5
    ):

        # Minimum number of landmarks required
        self.minimum_landmarks = minimum_landmarks

        # Minimum normalized hand dimensions
        self.minimum_hand_width = minimum_hand_width
        self.minimum_hand_height = minimum_hand_height

        # Minimum normalized bounding-box area
        self.minimum_hand_area = minimum_hand_area

        # Minimum handedness classification confidence
        self.minimum_handedness_confidence = (
            minimum_handedness_confidence
        )

    # ----------------------------------
    # Check landmark coordinates
    # ----------------------------------

    def check_coordinates(self, landmarks):

        issues = []

        for landmark in landmarks:

            x = landmark.get("x")
            y = landmark.get("y")
            z = landmark.get("z")

            # Check whether coordinates exist
            if x is None or y is None or z is None:

                issues.append(
                    "Missing landmark coordinates"
                )

                continue

            # Check for invalid numerical values
            if not (
                math.isfinite(x) and
                math.isfinite(y) and
                math.isfinite(z)
            ):

                issues.append(
                    "Invalid numerical coordinates"
                )

                continue

            # Check whether landmarks are within reasonable limits
            if not (
                -0.2 <= x <= 1.2 and
                -0.2 <= y <= 1.2
            ):

                issues.append(
                    "Landmarks outside reasonable frame limits"
                )

        return issues

    # ----------------------------------
    # Calculate hand dimensions
    # ----------------------------------

    def calculate_hand_dimensions(self, landmarks):

        x_coordinates = [
            landmark["x"]
            for landmark in landmarks
        ]

        y_coordinates = [
            landmark["y"]
            for landmark in landmarks
        ]

        x_min = min(x_coordinates)
        x_max = max(x_coordinates)

        y_min = min(y_coordinates)
        y_max = max(y_coordinates)

        hand_width = x_max - x_min
        hand_height = y_max - y_min

        hand_area = (
            hand_width * hand_height
        )

        return {
            "width": hand_width,
            "height": hand_height,
            "area": hand_area,
            "x_min": x_min,
            "x_max": x_max,
            "y_min": y_min,
            "y_max": y_max
        }

    # ----------------------------------
    # Evaluate hand quality
    # ----------------------------------

    def evaluate_hand(self, hand_data):

        issues = []

        landmarks = hand_data.get(
            "landmarks",
            []
        )

        handedness_confidence = hand_data.get(
            "confidence",
            0.0
        )

        # ----------------------------------
        # 1. Check landmark count
        # ----------------------------------

        if len(landmarks) != self.minimum_landmarks:

            issues.append(
                f"Expected {self.minimum_landmarks} landmarks, "
                f"received {len(landmarks)}"
            )

        # ----------------------------------
        # 2. Check coordinates
        # ----------------------------------

        coordinate_issues = (
            self.check_coordinates(landmarks)
        )

        issues.extend(coordinate_issues)

        # ----------------------------------
        # 3. Check hand dimensions
        # ----------------------------------

        dimensions = None

        if len(landmarks) >= 1:

            dimensions = (
                self.calculate_hand_dimensions(
                    landmarks
                )
            )

            if dimensions["width"] < (
                self.minimum_hand_width
            ):

                issues.append(
                    "Hand is too narrow or too small"
                )

            if dimensions["height"] < (
                self.minimum_hand_height
            ):

                issues.append(
                    "Hand is too short or too small"
                )

            if dimensions["area"] < (
                self.minimum_hand_area
            ):

                issues.append(
                    "Hand bounding-box area is too small"
                )

        # ----------------------------------
        # 4. Check handedness confidence
        # ----------------------------------

        if handedness_confidence < (
            self.minimum_handedness_confidence
        ):

            issues.append(
                "Low handedness confidence"
            )

        # ----------------------------------
        # 5. Final quality decision
        # ----------------------------------

        is_valid = len(issues) == 0

        return {
            "valid": is_valid,
            "issues": issues,
            "dimensions": dimensions,
            "confidence": handedness_confidence
        }

    # ----------------------------------
    # Get readable quality status
    # ----------------------------------

    def get_quality_status(self, quality_result):

        if quality_result["valid"]:

            return "Good"

        return "Poor"