# app/utils/timer.py

import time

class Timer:
    def __init__(self):
        self._start_time = None
        self._end_time = None
        self._elapsed = 0.0

    def start(self):
        self._start_time = time.perf_counter()
        self._end_time = None

    def stop(self):
        if self._start_time is None:
            raise RuntimeError("timer não foi iniciado. chame start() primeiro")
        self._end_time = time.perf_counter()
        self._elapsed = self._end_time - self._start_time

    def get_elapsed_time(self):
        if self._start_time is None:
            return 0.0
        if self._end_time is None:
            return time.perf_counter() - self._start_time
        return self._elapsed

    def reset(self):
        self._start_time = None
        self._end_time = None
        self._elapsed = 0.0

    # ===== Context Manager =====
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
