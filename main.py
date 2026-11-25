# main.py

import cv2
import time

from config import (
    CAMERA_INDEX,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    MAX_HANDS,
    DETECTION_CONFIDENCE,
    TRACKING_CONFIDENCE,
    WINDOW_NAME,
    DISPLAY_FPS,
    DISPLAY_LANDMARKS,
    DISPLAY_COUNT
)

from hand_detector import HandDetector
from finger_counter import FingerCounter
from count_stabilizer import CountStabilizer
from landmark_quality import LandmarkQualityChecker
from hand_tracker import HandTracker
from gesture_recognition import GestureRecognizer
from gesture_stabilizer import GestureStabilizer
from gesture_actions import GestureActions
from gesture_action_controller import GestureActionController
from action_history import ActionHistory
from system_controls import SystemControls
from performance_monitor import PerformanceMonitor
from stage_profiler import StageProfiler


def draw_action_history(frame, action_history):
    """Draw a persistent panel showing recent triggered gesture actions."""

    recent_actions = action_history.get_recent_actions(5)[::-1]

    panel_width = min(250, max(200, frame.shape[1] - 20))
    panel_x = max(10, frame.shape[1] - panel_width - 10)
    panel_y = 20
    line_height = 34

    # Always show the panel, including before the first action.
    visible_rows = max(1, len(recent_actions))
    panel_height = 48 + visible_rows * line_height
    panel_height = min(panel_height, max(60, frame.shape[0] - panel_y - 10))

    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (panel_x, panel_y),
        (panel_x + panel_width, panel_y + panel_height),
        (30, 30, 30),
        -1
    )
    frame = cv2.addWeighted(overlay, 0.78, frame, 0.22, 0)

    cv2.putText(
        frame,
        f"ACTION HISTORY ({action_history.get_history_size()})",
        (panel_x + 10, panel_y + 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (0, 255, 255),
        2
    )

    if not recent_actions:
        cv2.putText(
            frame,
            "No actions triggered yet",
            (panel_x + 10, panel_y + 52),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (210, 210, 210),
            1
        )
        return frame

    for index, entry in enumerate(recent_actions):
        y = panel_y + 48 + index * line_height
        header = (
            f"{entry['timestamp']} | Hand #{entry['track_id']} | "
            f"{entry['gesture']}"
        )
        action_text = str(entry["action"])

        cv2.putText(
            frame,
            header[:38],
            (panel_x + 10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.34,
            (255, 255, 255),
            1
        )
        cv2.putText(
            frame,
            action_text[:35],
            (panel_x + 10, y + 17),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.32,
            (0, 255, 0),
            1
        )

    return frame



def draw_control_hints(frame, controls):
    """Display keyboard shortcuts and current control states."""
    paused_text = "PAUSED" if controls.is_paused() else "RUNNING"
    state_color = (0, 0, 255) if controls.is_paused() else (0, 255, 0)
    hints = "Q Quit | R Reset | C Clear | P Pause | H History"
    # Dark footer strip keeps controls readable and separated from hand labels.
    footer_y = frame.shape[0] - 34
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, footer_y), (frame.shape[1], frame.shape[0]),
                  (25, 25, 25), -1)
    frame = cv2.addWeighted(overlay, 0.70, frame, 0.30, 0)
    cv2.putText(frame, hints, (10, frame.shape[0] - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1)
    cv2.putText(frame, paused_text, (10, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, state_color, 2)
    return frame



def main():

    # ==========================================
    # Initialize webcam
    # ==========================================

    camera = cv2.VideoCapture(CAMERA_INDEX)

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        CAMERA_WIDTH
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        CAMERA_HEIGHT
    )

    if not camera.isOpened():

        print("Error: Could not open webcam.")
        return

    print("Webcam started successfully.")
    print("Keyboard controls: Q=Quit, R=Reset, C=Clear history, P=Pause/Resume, H=Show/Hide history")

    # ==========================================
    # Initialize detection modules
    # ==========================================

    hand_detector = HandDetector(
        max_hands=MAX_HANDS,
        detection_confidence=DETECTION_CONFIDENCE,
        tracking_confidence=TRACKING_CONFIDENCE
    )

    finger_counter = FingerCounter()

    quality_checker = LandmarkQualityChecker()

    hand_tracker = HandTracker(
        max_distance=180,
        max_missing_frames=8
    )

    gesture_recognizer = GestureRecognizer()

    gesture_actions = GestureActions(
        cooldown=1.5
    )

    # ==========================================
    # Initialize gesture action controller
    # ==========================================

    gesture_action_controller = GestureActionController(
        confirmation_time=0.75
    )

    action_history = ActionHistory(max_history=10)
    system_controls = SystemControls()
    performance_monitor = PerformanceMonitor(window_size=30)
    stage_profiler = StageProfiler(window_size=30)

    # ==========================================
    # Per-hand stabilizers and action messages
    # ==========================================

    hand_stabilizers = {}

    gesture_stabilizers = {}

    last_action_messages = {}


    # ==========================================
    # Main loop
    # ==========================================

    try:

        while system_controls.is_running():

            # ==================================
            # Capture webcam frame
            # ==================================

            success, frame = camera.read()

            if not success:

                print("Error: Could not read frame.")
                break

            # Start timing this frame
            frame_start_time = time.perf_counter()

            # Mirror webcam image
            frame = cv2.flip(frame, 1)

            # ==================================
            # Paused mode: display frame but skip hand processing
            # ==================================

            if system_controls.is_paused():
                cv2.putText(
                    frame, "DETECTION PAUSED - Press P to resume",
                    (max(10, frame.shape[1] // 2 - 260), 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2
                )
                if system_controls.should_show_history():
                    frame = draw_action_history(frame, action_history)
                frame = draw_control_hints(frame, system_controls)
                display_frame = cv2.resize(
                    frame, (960, 720), interpolation=cv2.INTER_LINEAR
                )
                cv2.imshow(WINDOW_NAME, display_frame)
                key = cv2.waitKey(1) & 0xFF
                key_char = chr(key) if key != 255 else None
                control_action = system_controls.handle_key(key_char)
                if control_action == "reset":
                    hand_stabilizers.clear()
                    gesture_stabilizers.clear()
                    last_action_messages.clear()
                    hand_tracker.tracks.clear()
                    gesture_action_controller.reset()
                    print("System states reset.")
                elif control_action == "clear_history":
                    action_history.clear_history()
                    print("Action history cleared.")
                elif control_action == "history_hidden":
                    print("Action history hidden.")
                elif control_action == "history_shown":
                    print("Action history shown.")
                elif control_action == "paused":
                    print("Detection paused.")
                elif control_action == "resumed":
                    print("Detection resumed.")
                elif control_action == "quit":
                    print("Quit requested.")
                continue

            # ==================================
            # Detect hands
            # ==================================

            stage_profiler.start("MediaPipe Detection")
            frame, detected_hands = (
                hand_detector.find_hands(
                    frame,
                    draw=DISPLAY_LANDMARKS
                )
            )
            stage_profiler.stop("MediaPipe Detection")

            # ==================================
            # Track hands
            # ==================================

            stage_profiler.start("Hand Tracking")
            detected_hands = hand_tracker.update(
                detected_hands
            )
            stage_profiler.stop("Hand Tracking")

            # ==================================
            # Remove expired hand data
            # ==================================

            active_track_ids = set(
                hand_tracker.tracks.keys()
            )

            # Remove expired count stabilizers

            expired_track_ids = [
                track_id
                for track_id in hand_stabilizers
                if track_id not in active_track_ids
            ]

            for track_id in expired_track_ids:

                del hand_stabilizers[track_id]

            # Remove expired gesture stabilizers

            expired_gesture_ids = [
                track_id
                for track_id in gesture_stabilizers
                if track_id not in active_track_ids
            ]

            for track_id in expired_gesture_ids:

                del gesture_stabilizers[track_id]

            # Remove expired action controller states

            expired_action_ids = [
                track_id
                for track_id in gesture_action_controller.hand_states
                if track_id not in active_track_ids
            ]

            for track_id in expired_action_ids:

                gesture_action_controller.reset_hand(
                    track_id
                )

            # Remove expired action messages

            expired_message_ids = [
                track_id
                for track_id in last_action_messages
                if track_id not in active_track_ids
            ]

            for track_id in expired_message_ids:

                del last_action_messages[track_id]

            # ==================================
            # Initialize frame statistics
            # ==================================

            raw_total_fingers = 0

            stable_total_fingers = 0

            valid_hands = 0

            # ==================================
            # Process each detected hand
            # ==================================

            for hand in detected_hands:

                # ----------------------------------
                # Extract hand information
                # ----------------------------------

                landmarks = hand["landmarks"]

                hand_label = hand["label"]

                confidence = hand["confidence"]

                track_id = hand["track_id"]

                bounding_box = hand["bounding_box"]

                x_min = bounding_box["x_min"]

                y_min = bounding_box["y_min"]

                x_max = bounding_box["x_max"]

                y_max = bounding_box["y_max"]

                # ----------------------------------
                # Check landmark quality
                # ----------------------------------

                stage_profiler.start("Quality Checking")
                quality_result = (
                    quality_checker.evaluate_hand(
                        hand
                    )
                )
                stage_profiler.stop("Quality Checking")

                is_valid = quality_result["valid"]

                quality_status = (
                    quality_checker.get_quality_status(
                        quality_result
                    )
                )

                # Select bounding-box color

                if is_valid:

                    box_color = (0, 255, 0)

                    valid_hands += 1

                else:

                    box_color = (0, 0, 255)

                # Draw bounding box

                cv2.rectangle(
                    frame,
                    (x_min, y_min),
                    (x_max, y_max),
                    box_color,
                    2
                )

                # ==================================
                # Process valid hand
                # ==================================

                if is_valid:

                    # ----------------------------------
                    # Finger counting
                    # ----------------------------------

                    stage_profiler.start("Finger Counting")
                    finger_count, finger_results = (
                        finger_counter.count_fingers(
                            landmarks
                        )
                    )
                    stage_profiler.stop("Finger Counting")

                    raw_total_fingers += finger_count

                    # ----------------------------------
                    # Finger-count stabilization
                    # ----------------------------------

                    if track_id not in hand_stabilizers:

                        hand_stabilizers[
                            track_id
                        ] = CountStabilizer(
                            window_size=7,
                            minimum_votes=4
                        )

                    stable_hand_count = (
                        hand_stabilizers[
                            track_id
                        ].update(
                            finger_count
                        )
                    )

                    stable_total_fingers += (
                        stable_hand_count
                    )

                    # ----------------------------------
                    # Gesture recognition
                    # ----------------------------------

                    stage_profiler.start("Gesture Processing")
                    gesture_result = (
                        gesture_recognizer
                        .recognize_gesture(
                            finger_results
                        )
                    )

                    raw_gesture = (
                        gesture_result["gesture"]
                    )

                    # ----------------------------------
                    # Gesture stabilization
                    # ----------------------------------

                    if track_id not in gesture_stabilizers:

                        gesture_stabilizers[
                            track_id
                        ] = GestureStabilizer(
                            window_size=7,
                            minimum_votes=4
                        )

                    stable_gesture = (
                        gesture_stabilizers[
                            track_id
                        ].update(
                            raw_gesture
                        )
                    )
                    stage_profiler.stop("Gesture Processing")

                    # ----------------------------------
                    # Gesture action controller
                    # ----------------------------------

                    stage_profiler.start("Action Controller")
                    triggered_gesture = (
                        gesture_action_controller.update(
                            track_id=track_id,
                            stable_gesture=stable_gesture
                        )
                    )

                    # ----------------------------------
                    # Execute confirmed action
                    # ----------------------------------

                    if triggered_gesture is not None:

                        action_result = (
                            gesture_actions.execute_action(
                                triggered_gesture
                            )
                        )

                        if action_result is not None:

                            last_action_messages[
                                track_id
                            ] = action_result["action"]

                            action_history.add_action(
                                track_id=track_id,
                                gesture=triggered_gesture,
                                action=action_result["action"]
                            )

                    stage_profiler.stop("Action Controller")

                    # ----------------------------------
                    # Get action-controller status
                    # ----------------------------------

                    controller_status = (
                        gesture_action_controller
                        .get_status(track_id)
                    )

                    action_status = (
                        controller_status["status"]
                    )

                    action_progress = (
                        controller_status["progress"]
                    )

                    # ----------------------------------
                    # Gesture description
                    # ----------------------------------

                    gesture_description = (
                        gesture_recognizer
                        .get_gesture_description(
                            stable_gesture
                        )
                    )

                    # ----------------------------------
                    # Text information
                    # ----------------------------------

                    hand_text = (
                        f"ID {track_id} | "
                        f"{hand_label}: "
                        f"{finger_count} fingers"
                    )

                    raw_gesture_text = (
                        f"Raw: {raw_gesture}"
                    )

                    stable_gesture_text = (
                        f"Gesture: {stable_gesture}"
                    )

                # ==================================
                # Invalid hand
                # ==================================

                else:

                    stable_hand_count = 0

                    raw_gesture = "Unknown"

                    stable_gesture = "Unknown"

                    gesture_description = (
                        "Gesture not recognized"
                    )

                    hand_text = (
                        f"ID {track_id} | "
                        f"{hand_label}: "
                        f"Counting skipped"
                    )

                    raw_gesture_text = (
                        "Raw: Unknown"
                    )

                    stable_gesture_text = (
                        "Gesture: Unknown"
                    )

                    # Reset action controller state
                    # because the hand quality is invalid.

                    gesture_action_controller.update(
                        track_id=track_id,
                        stable_gesture="Unknown"
                    )

                    controller_status = (
                        gesture_action_controller
                        .get_status(track_id)
                    )

                    action_status = (
                        controller_status["status"]
                    )

                    action_progress = (
                        controller_status["progress"]
                    )

                # ==================================
                # Display hand information
                # ==================================

                cv2.putText(
                    frame,
                    hand_text,
                    (x_min, max(y_min - 15, 30)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    box_color,
                    2
                )

                # ----------------------------------
                # Quality status
                # ----------------------------------

                quality_text = (
                    f"Quality: {quality_status}"
                )

                cv2.putText(
                    frame,
                    quality_text,
                    (x_min, y_max + 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    box_color,
                    2
                )

                # ----------------------------------
                # Detection confidence
                # ----------------------------------

                confidence_text = (
                    f"Confidence: {confidence:.2f}"
                )

                cv2.putText(
                    frame,
                    confidence_text,
                    (x_min, y_max + 45),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    (255, 255, 0),
                    1
                )

                # ==================================
                # Display valid-hand information
                # ==================================

                if is_valid:

                    # Stable finger count

                    stable_text = (
                        f"Stable Count: "
                        f"{stable_hand_count}"
                    )

                    cv2.putText(
                        frame,
                        stable_text,
                        (x_min, y_max + 65),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 255),
                        2
                    )

                    # Raw gesture

                    cv2.putText(
                        frame,
                        raw_gesture_text,
                        (x_min, y_max + 85),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.45,
                        (255, 255, 255),
                        1
                    )

                    # Stable gesture

                    cv2.putText(
                        frame,
                        stable_gesture_text,
                        (x_min, y_max + 105),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.48,
                        (255, 0, 255),
                        2
                    )

                    # ----------------------------------
                    # Display latest action
                    # ----------------------------------

                    if track_id in last_action_messages:

                        action_display_text = (
                            f"Action: "
                            f"{last_action_messages[track_id]}"
                        )

                        cv2.putText(
                            frame,
                            action_display_text,
                            (x_min, y_max + 125),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.45,
                            (0, 255, 0),
                            1
                        )

                    # ----------------------------------
                    # Action-controller status
                    # ----------------------------------

                    if action_status == "Ready":

                        status_color = (255, 200, 0)

                    elif action_status == "Waiting":

                        status_color = (0, 165, 255)

                    elif action_status == "Triggered":

                        status_color = (0, 255, 0)

                    elif action_status == "Locked":

                        status_color = (0, 0, 255)

                    else:

                        status_color = (255, 255, 255)

                    status_text = (
                        f"Action Status: {action_status}"
                    )

                    cv2.putText(
                        frame,
                        status_text,
                        (x_min, y_max + 145),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        status_color,
                        2
                    )

                    # ----------------------------------
                    # Confirmation progress bar
                    # ----------------------------------

                    bar_x = x_min

                    bar_y = y_max + 160

                    bar_width = max(
                        100,
                        min(x_max - x_min, 200)
                    )

                    bar_height = 12

                    # Background

                    cv2.rectangle(
                        frame,
                        (bar_x, bar_y),
                        (bar_x + bar_width, bar_y + bar_height),
                        (60, 60, 60),
                        -1
                    )

                    # Progress fill

                    progress_width = int(
                        bar_width *
                        action_progress / 100
                    )

                    if progress_width > 0:

                        cv2.rectangle(
                            frame,
                            (bar_x, bar_y),
                            (
                                bar_x + progress_width,
                                bar_y + bar_height
                            ),
                            status_color,
                            -1
                        )

                    # Progress border

                    cv2.rectangle(
                        frame,
                        (bar_x, bar_y),
                        (bar_x + bar_width, bar_y + bar_height),
                        (255, 255, 255),
                        1
                    )

                    # Progress percentage

                    progress_text = (
                        f"{int(action_progress)}%"
                    )

                    cv2.putText(
                        frame,
                        progress_text,
                        (bar_x + bar_width + 10, bar_y + 11),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (255, 255, 255),
                        1
                    )

                # ==================================
                # Display quality issue
                # ==================================

                if not is_valid:

                    if quality_result["issues"]:

                        issue_text = (
                            quality_result["issues"][0]
                        )

                        issue_text = issue_text[:45]

                        cv2.putText(
                            frame,
                            issue_text,
                            (x_min, y_max + 65),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.4,
                            (0, 0, 255),
                            1
                        )

            # ======================================
            # Update performance statistics
            # ======================================

            processing_time_ms = (
                time.perf_counter() - frame_start_time
            ) * 1000

            performance_stats = performance_monitor.update(
                processing_time_ms=processing_time_ms
            )

            # ======================================
            # Display totals
            # ======================================

            if DISPLAY_COUNT:

                cv2.rectangle(
                    frame,
                    (20, 20),
                    (285, 145),
                    (50, 50, 50),
                    -1
                )

                cv2.putText(
                    frame,
                    f"Stable Total: {stable_total_fingers}",
                    (32, 48),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.62,
                    (0, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"Raw Total: {raw_total_fingers}",
                    (32, 75),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"Hands Detected: {len(detected_hands)}",
                    (32, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.48,
                    (255, 255, 255),
                    1
                )

                cv2.putText(
                    frame,
                    f"Valid Hands: {valid_hands}",
                    (32, 125),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    1
                )

            # ======================================
            # Display performance statistics
            # ======================================

            if DISPLAY_FPS:

                performance_lines = [
                    f"FPS: {performance_stats['current_fps']:.1f} "
                    f"(Avg: {performance_stats['average_fps']:.1f})",
                    f"Min/Max FPS: {performance_stats['min_fps']:.1f}/"
                    f"{performance_stats['max_fps']:.1f}",
                    f"Processing: {performance_stats['current_processing_time']:.1f} ms "
                    f"(Avg: {performance_stats['average_processing_time']:.1f} ms)",
                    f"Frames: {performance_stats['total_frames']}"
                ]

                perf_panel_y = 155
                perf_panel_height = 104
                perf_overlay = frame.copy()
                cv2.rectangle(
                    perf_overlay,
                    (10, perf_panel_y),
                    (min(frame.shape[1] - 10, 340), perf_panel_y + perf_panel_height),
                    (20, 20, 20),
                    -1
                )
                frame = cv2.addWeighted(perf_overlay, 0.72, frame, 0.28, 0)

                for index, line in enumerate(performance_lines):
                    # Shorten the long processing line for a compact 640x480 display.
                    if index == 2:
                        line = (
                            f"Proc: {performance_stats['current_processing_time']:.0f}ms "
                            f"(avg {performance_stats['average_processing_time']:.0f}ms)"
                        )
                    cv2.putText(
                        frame,
                        line[:42],
                        (20, perf_panel_y + 23 + index * 23),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.43,
                        (255, 80, 80),
                        1
                    )

            # ======================================
            # Display stage profiler statistics
            # ======================================

            profiler_stats = stage_profiler.get_all_stats()
            profiler_lines = []
            for stage_name, stats in profiler_stats.items():
                profiler_lines.append(
                    f"{stage_name}: {stats['average']:.1f} ms avg"
                )

            if profiler_lines:
                panel_x = 10
                panel_y = 270
                line_height = 19
                panel_width = min(320, frame.shape[1] - 20)
                panel_height = 28 + line_height * len(profiler_lines)
                profiler_overlay = frame.copy()
                cv2.rectangle(
                    profiler_overlay,
                    (panel_x, panel_y),
                    (panel_x + panel_width, panel_y + panel_height),
                    (25, 25, 25),
                    -1
                )
                frame = cv2.addWeighted(
                    profiler_overlay, 0.75, frame, 0.25, 0
                )
                cv2.putText(
                    frame, "STAGE PROFILER",
                    (panel_x + 8, panel_y + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42,
                    (0, 255, 255), 1
                )
                for index, line in enumerate(profiler_lines):
                    cv2.putText(
                        frame, line[:40],
                        (panel_x + 8, panel_y + 42 + index * line_height),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.36,
                        (255, 255, 255), 1
                    )

            # ======================================
            # Measure UI rendering stage
            # ======================================

            ui_stage_start = time.perf_counter()

            # ======================================
            # Draw action history (toggle with H)
            # ======================================

            if system_controls.should_show_history():
                frame = draw_action_history(frame, action_history)

            frame = draw_control_hints(frame, system_controls)

            stage_profiler.record(
                "UI Drawing",
                (time.perf_counter() - ui_stage_start) * 1000
            )

            # ======================================
            # Application title
            # ======================================



            # ======================================
            # Display frame
            # ======================================

            display_frame = cv2.resize(
                frame,
                (960, 720),
                interpolation=cv2.INTER_LINEAR
            )
            cv2.imshow(WINDOW_NAME, display_frame)

            # ======================================
            # Keyboard controls
            # ======================================

            key = cv2.waitKey(1) & 0xFF
            key_char = chr(key) if key != 255 else None
            control_action = system_controls.handle_key(key_char)

            if control_action == "reset":
                hand_stabilizers.clear()
                gesture_stabilizers.clear()
                last_action_messages.clear()
                hand_tracker.tracks.clear()
                gesture_action_controller.reset()
                print("System states reset.")

            elif control_action == "clear_history":
                action_history.clear_history()
                print("Action history cleared.")

            elif control_action == "history_hidden":
                print("Action history hidden.")

            elif control_action == "history_shown":
                print("Action history shown.")

            elif control_action == "paused":
                print("Detection paused.")

            elif control_action == "resumed":
                print("Detection resumed.")

            elif control_action == "quit":
                print("Quit requested.")

    finally:

        # ==========================================
        # Release resources
        # ==========================================

        camera.release()

        hand_detector.close()

        cv2.destroyAllWindows()

        print("Camera released.")
        print("Application closed.")


if __name__ == "__main__":

    main()