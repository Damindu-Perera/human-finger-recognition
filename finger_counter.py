import math


class FingerCounter:
    """
    Finger counter supporting MediaPipe landmarks represented as:
        - Objects with .x and .y
        - Dictionaries with "x" and "y"
        - Lists/tuples containing x and y

    MediaPipe landmarks:
        Thumb:  1, 2, 3, 4
        Index:  5, 6, 7, 8
        Middle: 9, 10, 11, 12
        Ring:   13, 14, 15, 16
        Pinky:  17, 18, 19, 20
    """

    def __init__(self):

        self.finger_landmarks = {
            "Index": (5, 6, 7, 8),
            "Middle": (9, 10, 11, 12),
            "Ring": (13, 14, 15, 16),
            "Pinky": (17, 18, 19, 20),
        }

        self.finger_pip_threshold = 155
        self.finger_dip_threshold = 145
        self.finger_distance_ratio = 1.10

        self.thumb_angle_threshold = 145
        self.thumb_distance_ratio = 1.15

        self.last_results = {}
        self.last_count = 0

    # --------------------------------------------------
    # LANDMARK COORDINATE HELPER
    # --------------------------------------------------

    def get_coordinates(self, point):
        """
        Extract x and y from a landmark regardless of format.
        """

        # MediaPipe landmark object
        if hasattr(point, "x") and hasattr(point, "y"):
            return float(point.x), float(point.y)

        # Dictionary landmark
        if isinstance(point, dict):
            if "x" in point and "y" in point:
                return float(point["x"]), float(point["y"])

            # Some detectors may use nested coordinates
            if "landmark" in point:
                return self.get_coordinates(point["landmark"])

        # Tuple or list: [x, y] or [x, y, z]
        if isinstance(point, (list, tuple)) and len(point) >= 2:
            return float(point[0]), float(point[1])

        raise TypeError(
            f"Unsupported landmark format: {type(point)} | Value: {point}"
        )

    # --------------------------------------------------
    # DISTANCE
    # --------------------------------------------------

    def calculate_distance(self, point1, point2):

        x1, y1 = self.get_coordinates(point1)
        x2, y2 = self.get_coordinates(point2)

        dx = x1 - x2
        dy = y1 - y2

        return math.sqrt(dx * dx + dy * dy)

    # --------------------------------------------------
    # ANGLE
    # --------------------------------------------------

    def calculate_angle(self, point1, point2, point3):
        """
        Calculate angle at point2.
        """

        x1, y1 = self.get_coordinates(point1)
        x2, y2 = self.get_coordinates(point2)
        x3, y3 = self.get_coordinates(point3)

        vector1 = (x1 - x2, y1 - y2)
        vector2 = (x3 - x2, y3 - y2)

        dot_product = (
            vector1[0] * vector2[0]
            + vector1[1] * vector2[1]
        )

        magnitude1 = math.sqrt(
            vector1[0] ** 2 + vector1[1] ** 2
        )

        magnitude2 = math.sqrt(
            vector2[0] ** 2 + vector2[1] ** 2
        )

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        cosine_angle = dot_product / (magnitude1 * magnitude2)

        cosine_angle = max(-1.0, min(1.0, cosine_angle))

        return math.degrees(math.acos(cosine_angle))

    # --------------------------------------------------
    # FOUR FINGERS
    # --------------------------------------------------

    def is_finger_extended(self, landmarks, finger_name):

        mcp_index, pip_index, dip_index, tip_index = (
            self.finger_landmarks[finger_name]
        )

        mcp = landmarks[mcp_index]
        pip = landmarks[pip_index]
        dip = landmarks[dip_index]
        tip = landmarks[tip_index]

        pip_angle = self.calculate_angle(mcp, pip, dip)
        dip_angle = self.calculate_angle(pip, dip, tip)

        tip_mcp_distance = self.calculate_distance(tip, mcp)
        pip_mcp_distance = self.calculate_distance(pip, mcp)

        distance_ratio = 0.0

        if pip_mcp_distance > 0:
            distance_ratio = (
                tip_mcp_distance / pip_mcp_distance
            )

        angle_extended = (
            pip_angle >= self.finger_pip_threshold
            and dip_angle >= self.finger_dip_threshold
        )

        distance_extended = (
            distance_ratio >= self.finger_distance_ratio
        )

        is_extended = angle_extended and distance_extended

        return {
            "extended": is_extended,
            "pip_angle": round(pip_angle, 2),
            "dip_angle": round(dip_angle, 2),
            "distance_ratio": round(distance_ratio, 2),
            "angle_extended": angle_extended,
            "distance_extended": distance_extended,
        }

    # --------------------------------------------------
    # THUMB
    # --------------------------------------------------

    def is_thumb_extended(self, landmarks):

        cmc = landmarks[1]
        mcp = landmarks[2]
        ip = landmarks[3]
        tip = landmarks[4]

        index_mcp = landmarks[5]

        thumb_angle = self.calculate_angle(mcp, ip, tip)

        tip_index_distance = self.calculate_distance(
            tip, index_mcp
        )

        ip_index_distance = self.calculate_distance(
            ip, index_mcp
        )

        thumb_mcp_distance = self.calculate_distance(
            tip, mcp
        )

        cmc_mcp_distance = self.calculate_distance(
            cmc, mcp
        )

        distance_ratio = 0.0

        if ip_index_distance > 0:
            distance_ratio = (
                tip_index_distance / ip_index_distance
            )

        thumb_length_ratio = 0.0

        if cmc_mcp_distance > 0:
            thumb_length_ratio = (
                thumb_mcp_distance / cmc_mcp_distance
            )

        angle_extended = (
            thumb_angle >= self.thumb_angle_threshold
        )

        distance_extended = (
            distance_ratio >= self.thumb_distance_ratio
        )

        length_extended = thumb_length_ratio >= 1.0

        is_extended = (
            angle_extended
            and distance_extended
            and length_extended
        )

        return {
            "extended": is_extended,
            "angle": round(thumb_angle, 2),
            "distance_ratio": round(distance_ratio, 2),
            "length_ratio": round(thumb_length_ratio, 2),
            "angle_extended": angle_extended,
            "distance_extended": distance_extended,
            "length_extended": length_extended,
        }

    # --------------------------------------------------
    # COUNT FINGERS
    # --------------------------------------------------

    def count_fingers(self, landmarks):

        finger_results = {}

        finger_results["Thumb"] = self.is_thumb_extended(
            landmarks
        )

        for finger_name in self.finger_landmarks:

            finger_results[finger_name] = (
                self.is_finger_extended(
                    landmarks, finger_name
                )
            )

        total_fingers = sum(
            1
            for result in finger_results.values()
            if result["extended"]
        )

        self.last_results = finger_results
        self.last_count = total_fingers

        return total_fingers, finger_results

    # --------------------------------------------------
    # STATUS
    # --------------------------------------------------

    def get_finger_status(self, finger_results):

        status = {}

        for finger_name, result in finger_results.items():

            status[finger_name] = (
                "Raised"
                if result["extended"]
                else "Folded"
            )

        return status

    # --------------------------------------------------
    # DEBUG SUMMARY
    # --------------------------------------------------

    def get_debug_summary(
        self,
        finger_results=None,
        total_fingers=None
    ):

        if finger_results is None:
            finger_results = self.last_results

        if total_fingers is None:
            total_fingers = self.last_count

        lines = []

        for finger_name, result in finger_results.items():

            status = (
                "RAISED"
                if result["extended"]
                else "FOLDED"
            )

            if finger_name == "Thumb":

                lines.append(
                    f"{finger_name}: {status} | "
                    f"Angle={result.get('angle', 0):.1f} | "
                    f"Distance={result.get('distance_ratio', 0):.2f} | "
                    f"Length={result.get('length_ratio', 0):.2f}"
                )

            else:

                lines.append(
                    f"{finger_name}: {status} | "
                    f"PIP={result.get('pip_angle', 0):.1f} | "
                    f"DIP={result.get('dip_angle', 0):.1f} | "
                    f"Distance={result.get('distance_ratio', 0):.2f}"
                )

        lines.append(f"TOTAL FINGERS: {total_fingers}")

        return lines

    # --------------------------------------------------
    # PRINT DEBUG
    # --------------------------------------------------

    def print_debug_summary(
        self,
        finger_results=None,
        total_fingers=None
    ):

        lines = self.get_debug_summary(
            finger_results,
            total_fingers
        )

        print("\n========== FINGER DEBUG ==========")

        for line in lines:
            print(line)

        print("================================\n")