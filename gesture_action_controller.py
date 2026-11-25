# gesture_action_controller.py

import time


class GestureActionController:

    def __init__(self, confirmation_time=0.75):

        self.confirmation_time = confirmation_time
        self.hand_states = {}

    def create_hand_state(self):

        return {
            "pending_gesture": None,
            "pending_since": None,
            "last_triggered_gesture": None,
            "armed": True,
            "status": "Ready",
            "progress": 0.0
        }

    def update(
        self,
        track_id,
        stable_gesture,
        current_time=None
    ):

        """
        Process a stabilized gesture.

        Returns:
            Gesture name if action should trigger.
            None otherwise.
        """

        if current_time is None:
            current_time = time.time()

        if track_id not in self.hand_states:

            self.hand_states[track_id] = (
                self.create_hand_state()
            )

        state = self.hand_states[track_id]

        # -----------------------------------------
        # Neutral gesture: reset and re-arm
        # -----------------------------------------

        if stable_gesture in [
            "Unknown",
            "Waiting...",
            None
        ]:

            state["pending_gesture"] = None
            state["pending_since"] = None
            state["last_triggered_gesture"] = None
            state["armed"] = True
            state["status"] = "Ready"
            state["progress"] = 0.0

            return None

        # -----------------------------------------
        # Controller is locked after action
        # -----------------------------------------

        if not state["armed"]:

            state["status"] = "Locked"
            state["progress"] = 100.0

            return None

        # -----------------------------------------
        # New gesture detected
        # -----------------------------------------

        if stable_gesture != state["pending_gesture"]:

            state["pending_gesture"] = stable_gesture
            state["pending_since"] = current_time
            state["status"] = "Waiting"
            state["progress"] = 0.0

            return None

        # -----------------------------------------
        # Calculate confirmation progress
        # -----------------------------------------

        elapsed_time = (
            current_time - state["pending_since"]
        )

        progress = (
            elapsed_time / self.confirmation_time
        ) * 100

        progress = max(0.0, min(progress, 100.0))

        state["progress"] = progress
        state["status"] = "Waiting"

        # -----------------------------------------
        # Confirmation time not reached
        # -----------------------------------------

        if elapsed_time < self.confirmation_time:

            return None

        # -----------------------------------------
        # Prevent duplicate triggering
        # -----------------------------------------

        if (
            stable_gesture ==
            state["last_triggered_gesture"]
        ):

            state["status"] = "Locked"

            return None

        # -----------------------------------------
        # Confirm gesture
        # -----------------------------------------

        state["last_triggered_gesture"] = (
            stable_gesture
        )

        state["armed"] = False
        state["status"] = "Triggered"
        state["progress"] = 100.0

        return stable_gesture

    # =============================================
    # Get current status
    # =============================================

    def get_status(self, track_id):

        if track_id not in self.hand_states:

            return {
                "status": "Ready",
                "progress": 0.0,
                "gesture": None
            }

        state = self.hand_states[track_id]

        return {
            "status": state["status"],
            "progress": state["progress"],
            "gesture": state["pending_gesture"]
        }

    # =============================================
    # Reset a specific hand
    # =============================================

    def reset_hand(self, track_id):

        if track_id in self.hand_states:

            del self.hand_states[track_id]

    # =============================================
    # Reset all hands
    # =============================================

    def reset(self):

        self.hand_states.clear()