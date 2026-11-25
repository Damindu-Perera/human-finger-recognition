import time
from collections import deque


class StageProfiler:

    def __init__(self, window_size=30):

        if window_size <= 0:
            raise ValueError("Window size must be positive.")

        self.window_size = window_size

        self.timings = {}

        self.start_times = {}

    def start(self, stage_name):

        self.start_times[stage_name] = time.perf_counter()

    def stop(self, stage_name):

        if stage_name not in self.start_times:
            raise ValueError(
                f"Stage '{stage_name}' was not started."
            )

        elapsed_time = (
            time.perf_counter()
            - self.start_times.pop(stage_name)
        ) * 1000

        self.record(stage_name, elapsed_time)

        return elapsed_time

    def record(self, stage_name, elapsed_time_ms):

        if elapsed_time_ms < 0:
            raise ValueError(
                "Elapsed time cannot be negative."
            )

        if stage_name not in self.timings:

            self.timings[stage_name] = deque(
                maxlen=self.window_size
            )

        self.timings[stage_name].append(
            elapsed_time_ms
        )

    def get_stats(self, stage_name):

        if stage_name not in self.timings:
            return {
                "current": 0.0,
                "average": 0.0,
                "minimum": 0.0,
                "maximum": 0.0,
                "samples": 0
            }

        values = list(self.timings[stage_name])

        return {
            "current": values[-1],
            "average": sum(values) / len(values),
            "minimum": min(values),
            "maximum": max(values),
            "samples": len(values)
        }

    def get_all_stats(self):

        return {
            stage_name: self.get_stats(stage_name)
            for stage_name in self.timings
        }

    def reset(self):

        self.timings.clear()

        self.start_times.clear()