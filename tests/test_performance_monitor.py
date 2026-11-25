import unittest

from performance_monitor import PerformanceMonitor


class TestPerformanceMonitor(unittest.TestCase):

    def setUp(self):
        self.monitor = PerformanceMonitor(window_size=5)

    def test_initial_state(self):
        stats = self.monitor.get_stats()

        self.assertEqual(stats["current_fps"], 0.0)
        self.assertEqual(stats["average_fps"], 0.0)
        self.assertEqual(stats["min_fps"], 0.0)
        self.assertEqual(stats["max_fps"], 0.0)
        self.assertEqual(stats["current_processing_time"], 0.0)
        self.assertEqual(stats["average_processing_time"], 0.0)
        self.assertEqual(stats["total_frames"], 0)

    def test_first_update(self):
        stats = self.monitor.update(
            processing_time_ms=20,
            current_time=1.0
        )

        self.assertEqual(stats["current_fps"], 0.0)
        self.assertEqual(stats["current_processing_time"], 20)
        self.assertEqual(stats["total_frames"], 1)

    def test_current_fps(self):
        self.monitor.update(current_time=1.0)
        stats = self.monitor.update(current_time=2.0)

        self.assertAlmostEqual(stats["current_fps"], 1.0)

    def test_fps_calculation(self):
        self.monitor.update(current_time=1.0)
        self.monitor.update(current_time=2.0)

        stats = self.monitor.update(current_time=2.5)

        self.assertAlmostEqual(stats["current_fps"], 2.0)

    def test_average_fps(self):
        self.monitor.update(current_time=1.0)
        self.monitor.update(current_time=2.0)
        self.monitor.update(current_time=2.5)

        stats = self.monitor.get_stats()

        # FPS values: 1 FPS and 2 FPS
        self.assertAlmostEqual(stats["average_fps"], 1.5)

    def test_min_max_fps(self):
        self.monitor.update(current_time=1.0)
        self.monitor.update(current_time=2.0)
        self.monitor.update(current_time=2.5)

        stats = self.monitor.get_stats()

        self.assertAlmostEqual(stats["min_fps"], 1.0)
        self.assertAlmostEqual(stats["max_fps"], 2.0)

    def test_processing_time(self):
        stats = self.monitor.update(
            processing_time_ms=25.5,
            current_time=1.0
        )

        self.assertEqual(
            stats["current_processing_time"],
            25.5
        )

    def test_average_processing_time(self):
        self.monitor.update(
            processing_time_ms=10,
            current_time=1.0
        )

        self.monitor.update(
            processing_time_ms=20,
            current_time=2.0
        )

        stats = self.monitor.update(
            processing_time_ms=30,
            current_time=3.0
        )

        self.assertAlmostEqual(
            stats["average_processing_time"],
            20.0
        )

    def test_window_limit(self):
        monitor = PerformanceMonitor(window_size=2)

        monitor.update(current_time=1.0)
        monitor.update(current_time=2.0)
        monitor.update(current_time=2.5)
        monitor.update(current_time=3.5)

        self.assertEqual(len(monitor.frame_times), 2)

    def test_total_frames(self):
        self.monitor.update(current_time=1.0)
        self.monitor.update(current_time=2.0)
        self.monitor.update(current_time=3.0)

        stats = self.monitor.get_stats()

        self.assertEqual(stats["total_frames"], 3)

    def test_reset(self):
        self.monitor.update(
            processing_time_ms=20,
            current_time=1.0
        )

        self.monitor.update(
            processing_time_ms=30,
            current_time=2.0
        )

        self.monitor.reset()

        stats = self.monitor.get_stats()

        self.assertEqual(stats["current_fps"], 0.0)
        self.assertEqual(stats["average_fps"], 0.0)
        self.assertEqual(stats["min_fps"], 0.0)
        self.assertEqual(stats["max_fps"], 0.0)
        self.assertEqual(stats["current_processing_time"], 0.0)
        self.assertEqual(stats["average_processing_time"], 0.0)
        self.assertEqual(stats["total_frames"], 0)

    def test_invalid_window_size(self):
        with self.assertRaises(ValueError):
            PerformanceMonitor(window_size=0)


if __name__ == "__main__":
    unittest.main()
    