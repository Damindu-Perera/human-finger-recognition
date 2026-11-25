# test_gesture_action_controller.py

from gesture_action_controller import GestureActionController


def test_confirmation_delay():

    controller = GestureActionController(
        confirmation_time=0.75
    )

    # Gesture starts
    result = controller.update(
        1, "Peace", 0.0
    )

    assert result is None

    status = controller.get_status(1)

    assert status["status"] == "Waiting"
    assert status["progress"] == 0.0

    # 0.4 seconds
    result = controller.update(
        1, "Peace", 0.4
    )

    assert result is None

    status = controller.get_status(1)

    assert status["status"] == "Waiting"
    assert status["progress"] > 50

    # 0.8 seconds
    result = controller.update(
        1, "Peace", 0.8
    )

    assert result == "Peace"

    status = controller.get_status(1)

    assert status["status"] == "Triggered"
    assert status["progress"] == 100


def test_no_repeated_trigger():

    controller = GestureActionController(
        confirmation_time=0.75
    )

    controller.update(1, "Peace", 0.0)

    result = controller.update(
        1, "Peace", 0.8
    )

    assert result == "Peace"

    result = controller.update(
        1, "Peace", 1.0
    )

    assert result is None

    status = controller.get_status(1)

    assert status["status"] == "Locked"


def test_neutral_rearms_controller():

    controller = GestureActionController(
        confirmation_time=0.75
    )

    controller.update(1, "Peace", 0.0)

    controller.update(1, "Peace", 0.8)

    # Neutral gesture
    result = controller.update(
        1, "Unknown", 1.0
    )

    assert result is None

    status = controller.get_status(1)

    assert status["status"] == "Ready"
    assert status["progress"] == 0.0

    # New gesture can trigger again
    controller.update(
        1, "Thumbs Up", 2.0
    )

    result = controller.update(
        1, "Thumbs Up", 2.8
    )

    assert result == "Thumbs Up"


def test_different_gesture_requires_rearming():

    controller = GestureActionController(
        confirmation_time=0.75
    )

    controller.update(1, "Peace", 0.0)

    controller.update(1, "Peace", 0.8)

    # Try changing gesture without neutral
    result = controller.update(
        1, "Thumbs Up", 1.0
    )

    assert result is None

    status = controller.get_status(1)

    assert status["status"] == "Locked"


def test_independent_hands():

    controller = GestureActionController(
        confirmation_time=0.75
    )

    # Hand 1
    controller.update(
        1, "Peace", 0.0
    )

    # Hand 2
    controller.update(
        2, "Open Palm", 0.0
    )

    # Hand 1 triggers
    result1 = controller.update(
        1, "Peace", 0.8
    )

    # Hand 2 triggers
    result2 = controller.update(
        2, "Open Palm", 0.8
    )

    assert result1 == "Peace"
    assert result2 == "Open Palm"


def test_reset_hand():

    controller = GestureActionController()

    controller.update(
        1, "Peace", 0.0
    )

    controller.reset_hand(1)

    assert 1 not in controller.hand_states

    status = controller.get_status(1)

    assert status["status"] == "Ready"


def test_reset_all():

    controller = GestureActionController()

    controller.update(
        1, "Peace", 0.0
    )

    controller.update(
        2, "Open Palm", 0.0
    )

    controller.reset()

    assert len(controller.hand_states) == 0


if __name__ == "__main__":

    test_confirmation_delay()
    test_no_repeated_trigger()
    test_neutral_rearms_controller()
    test_different_gesture_requires_rearming()
    test_independent_hands()
    test_reset_hand()
    test_reset_all()

    print("All Gesture Action Controller tests passed!")