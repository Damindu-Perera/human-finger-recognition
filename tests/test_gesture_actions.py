
# test_gesture_actions.py

from gesture_actions import GestureActions


actions = GestureActions(cooldown=1.5)


print("\nGesture Actions Tests")
print("=" * 45)


# ==========================================
# Test 1: Thumbs Up
# ==========================================

print("\nTest 1: Thumbs Up")

result = actions.execute_action(
    "Thumbs Up",
    current_time=10
)

assert result is not None
assert result["triggered"] is True

print("PASS: Thumbs Up action triggered")


# ==========================================
# Test 2: Cooldown
# ==========================================

print("\nTest 2: Cooldown")

result = actions.execute_action(
    "Thumbs Up",
    current_time=10.5
)

assert result is None

print("PASS: Cooldown prevents repeated action")


# ==========================================
# Test 3: Trigger after cooldown
# ==========================================

print("\nTest 3: Trigger after cooldown")

result = actions.execute_action(
    "Thumbs Up",
    current_time=12
)

assert result is not None

print("PASS: Action triggers after cooldown")


# ==========================================
# Test 4: Peace
# ==========================================

print("\nTest 4: Peace")

result = actions.execute_action(
    "Peace",
    current_time=20
)

assert result is not None
assert result["action"] == "Special mode activated"

print("PASS: Peace action works")


# ==========================================
# Test 5: Unknown gesture
# ==========================================

print("\nTest 5: Unknown gesture")

result = actions.execute_action(
    "Unknown",
    current_time=30
)

assert result is None

print("PASS: Unknown gesture does not trigger action")


# ==========================================
# Test 6: Reset
# ==========================================

print("\nTest 6: Reset")

actions.reset()

assert len(actions.last_trigger_time) == 0

print("PASS: Reset works")


print("\n" + "=" * 45)
print("All gesture action tests completed!")
