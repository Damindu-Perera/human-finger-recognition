import unittest

from action_history import ActionHistory

class TestActionHistory(unittest.TestCase):

    def setUp(self):
        self.action_history = ActionHistory(max_history=5)

    def test_add_action(self):
        entry = self.action_history.add_action(
            track_id=1,
            gesture="Peace",
            action="Special mode activated"
        )

        self.assertEqual(entry["track_id"], 1)
        self.assertEqual(entry["gesture"], "Peace")
        self.assertEqual(entry["action"], "Special mode activated")
        self.assertIn("timestamp", entry)

    def test_get_history(self):
        self.action_history.add_action(
            1, "Peace", "Special mode activated"
        )

        self.action_history.add_action(
            2, "Thumbs Up", "Confirmation received"
        )

        history = self.action_history.get_history()

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["gesture"], "Peace")
        self.assertEqual(history[1]["gesture"], "Thumbs Up")

    def test_get_recent_actions(self):
        for i in range(7):
            self.action_history.add_action(
                track_id=1,
                gesture=f"Gesture {i}",
                action=f"Action {i}"
            )

        recent_actions = self.action_history.get_recent_actions(3)

        self.assertEqual(len(recent_actions), 3)
        self.assertEqual(recent_actions[0]["gesture"], "Gesture 4")
        self.assertEqual(recent_actions[2]["gesture"], "Gesture 6")

    def test_get_latest_action(self):
        self.action_history.add_action(
            1, "Peace", "Special mode activated"
        )

        self.action_history.add_action(
            2, "Pointing", "Selection mode activated"
        )

        latest = self.action_history.get_latest_action()

        self.assertEqual(latest["gesture"], "Pointing")

    def test_empty_history(self):
        self.assertEqual(self.action_history.get_history(), [])
        self.assertIsNone(self.action_history.get_latest_action())
        self.assertEqual(self.action_history.get_history_size(), 0)

    def test_history_limit(self):
        for i in range(7):
            self.action_history.add_action(
                track_id=1,
                gesture=f"Gesture {i}",
                action=f"Action {i}"
            )

        history = self.action_history.get_history()

        self.assertEqual(len(history), 5)
        self.assertEqual(history[0]["gesture"], "Gesture 2")
        self.assertEqual(history[-1]["gesture"], "Gesture 6")

    def test_clear_history(self):
        self.action_history.add_action(
            1, "Peace", "Special mode activated"
        )

        self.action_history.add_action(
            2, "Thumbs Up", "Confirmation received"
        )

        self.action_history.clear_history()

        self.assertEqual(self.action_history.get_history(), [])
        self.assertEqual(self.action_history.get_history_size(), 0)

    def test_invalid_max_history(self):
        with self.assertRaises(ValueError):
            ActionHistory(max_history=0)

    def test_invalid_recent_limit(self):
        self.action_history.add_action(
            1, "Peace", "Special mode activated"
        )

        self.assertEqual(
            self.action_history.get_recent_actions(0),
            []
        )

if __name__ == "__main__":
    unittest.main()