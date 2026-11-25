# hand_tracker.py

import math


class HandTracker:

    def __init__(
        self,
        max_distance=180,
        max_missing_frames=8
    ):

        # Maximum distance allowed between hand centers
        self.max_distance = max_distance

        # How many frames a missing hand can remain tracked
        self.max_missing_frames = max_missing_frames

        # Store active tracks
        self.tracks = {}

        # Tracking ID counter
        self.next_track_id = 1

    # ----------------------------------
    # Calculate bounding-box center
    # ----------------------------------

    def calculate_center(self, hand):

        bounding_box = hand["bounding_box"]

        center_x = (
            bounding_box["x_min"] +
            bounding_box["x_max"]
        ) / 2

        center_y = (
            bounding_box["y_min"] +
            bounding_box["y_max"]
        ) / 2

        return center_x, center_y

    # ----------------------------------
    # Calculate distance between centers
    # ----------------------------------

    def calculate_distance(self, center1, center2):

        dx = center1[0] - center2[0]
        dy = center1[1] - center2[1]

        return math.sqrt(
            dx ** 2 + dy ** 2
        )

    # ----------------------------------
    # Update hand tracking
    # ----------------------------------

    def update(self, detected_hands):

        # Calculate centers of current hands
        current_centers = [
            self.calculate_center(hand)
            for hand in detected_hands
        ]

        # Store possible matching pairs
        possible_matches = []

        # ----------------------------------
        # Find possible track matches
        # ----------------------------------

        for track_id, track in self.tracks.items():

            for hand_index, hand in enumerate(
                detected_hands
            ):

                current_center = (
                    current_centers[hand_index]
                )

                distance = self.calculate_distance(
                    track["center"],
                    current_center
                )

                # Only consider nearby hands
                if distance <= self.max_distance:

                    # Handedness is used as a matching hint
                    label_penalty = 0

                    if (
                        track["label"] != "Unknown" and
                        hand["label"] != "Unknown" and
                        track["label"] != hand["label"]
                    ):

                        label_penalty = 80

                    matching_cost = (
                        distance + label_penalty
                    )

                    possible_matches.append({
                        "track_id": track_id,
                        "hand_index": hand_index,
                        "distance": distance,
                        "cost": matching_cost
                    })

        # ----------------------------------
        # Sort matches by lowest cost
        # ----------------------------------

        possible_matches.sort(
            key=lambda match: match["cost"]
        )

        # Track and hand matching
        matched_track_ids = set()
        matched_hand_indexes = set()

        # ----------------------------------
        # Match existing tracks
        # ----------------------------------

        for match in possible_matches:

            track_id = match["track_id"]
            hand_index = match["hand_index"]

            # Each track and hand can only match once
            if track_id in matched_track_ids:
                continue

            if hand_index in matched_hand_indexes:
                continue

            # Assign tracking ID
            detected_hands[hand_index]["track_id"] = (
                track_id
            )

            # Update track information
            self.tracks[track_id]["center"] = (
                current_centers[hand_index]
            )

            self.tracks[track_id]["label"] = (
                detected_hands[hand_index]["label"]
            )

            self.tracks[track_id]["missing_frames"] = 0

            matched_track_ids.add(track_id)
            matched_hand_indexes.add(hand_index)

        # ----------------------------------
        # Create tracks for new hands
        # ----------------------------------

        for hand_index, hand in enumerate(
            detected_hands
        ):

            if hand_index in matched_hand_indexes:
                continue

            track_id = self.next_track_id

            self.next_track_id += 1

            hand["track_id"] = track_id

            self.tracks[track_id] = {
                "center": current_centers[hand_index],
                "label": hand["label"],
                "missing_frames": 0
            }

            matched_track_ids.add(track_id)
            matched_hand_indexes.add(hand_index)

        # ----------------------------------
        # Update missing frame counters
        # ----------------------------------

        tracks_to_remove = []

        for track_id in list(self.tracks):

            if track_id not in matched_track_ids:

                self.tracks[track_id][
                    "missing_frames"
                ] += 1

                # Remove tracks missing for too long
                if (
                    self.tracks[track_id][
                        "missing_frames"
                    ] > self.max_missing_frames
                ):

                    tracks_to_remove.append(track_id)

        # ----------------------------------
        # Remove expired tracks
        # ----------------------------------

        for track_id in tracks_to_remove:

            del self.tracks[track_id]

        return detected_hands

    # ----------------------------------
    # Reset tracker
    # ----------------------------------

    def reset(self):

        self.tracks.clear()

        self.next_track_id = 1