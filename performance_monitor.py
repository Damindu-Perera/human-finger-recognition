from collections import deque
import time


class PerformanceMonitor:
    """
    Measures FPS and frame-processing performance.
    """

    def __init__(self, window_size=30):
        if window_size <= 0:
            raise ValueError("window_size must be greater than 0")

        self.window_size = window_size

        self.frame_times = deque(maxlen=window_size)
        self.processing_times = deque(maxlen=window_size)

        self.previous_frame_time = None

        self.current_fps = 0.0
        self.average_fps = 0.0
        self.min_fps = 0.0
        self.max_fps = 0.0

        self.current_processing_time = 0.0
        self.average_processing_time = 0.0

        self.total_frames = 0

    def update(self, processing_time_ms=None, current_time=None):
        """
        Update performance statistics.

        Args:
            processing_time_ms (float): Processing time for the frame.
            current_time (float): Optional timestamp for testing.

        Returns:
            dict: Current performance statistics.
        """

        if current_time is None:
            current_time = time.perf_counter()

        # Calculate FPS using the time between frames
        if self.previous_frame_time is not None:

            frame_interval = (
                current_time - self.previous_frame_time
            )

            if frame_interval > 0:
                self.current_fps = 1.0 / frame_interval
                self.frame_times.append(self.current_fps)

        self.previous_frame_time = current_time

        # Processing time
        if processing_time_ms is not None:

            self.current_processing_time = max(
                0.0,
                float(processing_time_ms)
            )

            self.processing_times.append(
                self.current_processing_time
            )

        # Average FPS
        if self.frame_times:

            self.average_fps = (
                sum(self.frame_times) /
                len(self.frame_times)
            )

            self.min_fps = min(self.frame_times)

            self.max_fps = max(self.frame_times)

        # Average processing time
        if self.processing_times:

            self.average_processing_time = (
                sum(self.processing_times) /
                len(self.processing_times)
            )

        self.total_frames += 1

        return self.get_stats()

    def get_stats(self):
        """
        Return performance statistics.
        """

        return {
            "current_fps": self.current_fps,
            "average_fps": self.average_fps,
            "min_fps": self.min_fps,
            "max_fps": self.max_fps,
            "current_processing_time": (
                self.current_processing_time
            ),
            "average_processing_time": (
                self.average_processing_time
            ),
            "total_frames": self.total_frames
        }

    def reset(self):
        """
        Reset all performance statistics.
        """

        self.frame_times.clear()
        self.processing_times.clear()

        self.previous_frame_time = None

        self.current_fps = 0.0
        self.average_fps = 0.0
        self.min_fps = 0.0
        self.max_fps = 0.0

        self.current_processing_time = 0.0
        self.average_processing_time = 0.0

        self.total_frames = 0