class SystemControls:
    """
    Manages keyboard controls and application states.
    """

    def __init__(self):
        self.paused = False
        self.show_history = True
        self.running = True

    def handle_key(self, key):
        """
        Process a keyboard key.

        Args:
            key: Keyboard character.

        Returns:
            str: Action performed, or None.
        """

        if key is None:
            return None

        key = key.lower()

        # Quit application
        if key == "q":
            self.running = False
            return "quit"

        # Reset system
        elif key == "r":
            return "reset"

        # Clear action history
        elif key == "c":
            return "clear_history"

        # Pause / resume
        elif key == "p":
            self.paused = not self.paused

            if self.paused:
                return "paused"

            return "resumed"

        # Show / hide action history
        elif key == "h":
            self.show_history = not self.show_history

            if self.show_history:
                return "history_shown"

            return "history_hidden"

        return None

    def is_running(self):
        """Check whether the application should continue running."""
        return self.running

    def is_paused(self):
        """Check whether the application is paused."""
        return self.paused

    def should_show_history(self):
        """Check whether the history panel should be displayed."""
        return self.show_history

    def reset_pause(self):
        """Resume the application."""
        self.paused = False

    def reset(self):
        """Reset control states to defaults."""
        self.paused = False
        self.show_history = True
        self.running = True