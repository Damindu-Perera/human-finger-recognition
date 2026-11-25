import unittest

from system_controls import SystemControls


class TestSystemControls(unittest.TestCase):

    def setUp(self):
        self.controls = SystemControls()

    def test_initial_state(self):
        self.assertTrue(self.controls.is_running())
        self.assertFalse(self.controls.is_paused())
        self.assertTrue(self.controls.should_show_history())

    def test_quit(self):
        result = self.controls.handle_key("q")

        self.assertEqual(result, "quit")
        self.assertFalse(self.controls.is_running())

    def test_quit_uppercase(self):
        result = self.controls.handle_key("Q")

        self.assertEqual(result, "quit")
        self.assertFalse(self.controls.is_running())

    def test_reset_key(self):
        result = self.controls.handle_key("r")

        self.assertEqual(result, "reset")

    def test_clear_history_key(self):
        result = self.controls.handle_key("c")

        self.assertEqual(result, "clear_history")

    def test_pause(self):
        result = self.controls.handle_key("p")

        self.assertEqual(result, "paused")
        self.assertTrue(self.controls.is_paused())

    def test_resume(self):
        self.controls.handle_key("p")

        result = self.controls.handle_key("p")

        self.assertEqual(result, "resumed")
        self.assertFalse(self.controls.is_paused())

    def test_toggle_history_off(self):
        result = self.controls.handle_key("h")

        self.assertEqual(result, "history_hidden")
        self.assertFalse(self.controls.should_show_history())

    def test_toggle_history_on(self):
        self.controls.handle_key("h")

        result = self.controls.handle_key("h")

        self.assertEqual(result, "history_shown")
        self.assertTrue(self.controls.should_show_history())

    def test_unknown_key(self):
        result = self.controls.handle_key("x")

        self.assertIsNone(result)

    def test_none_key(self):
        result = self.controls.handle_key(None)

        self.assertIsNone(result)

    def test_reset_controls(self):
        self.controls.handle_key("p")
        self.controls.handle_key("h")
        self.controls.handle_key("q")

        self.controls.reset()

        self.assertTrue(self.controls.is_running())
        self.assertFalse(self.controls.is_paused())
        self.assertTrue(self.controls.should_show_history())


if __name__ == "__main__":
    unittest.main()