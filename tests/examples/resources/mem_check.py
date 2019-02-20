try:
    import psutil
except ImportError:
    import warnings

    warning = UserWarning('psutil could not be imported, memory safety will not tested')

    warnings.filterwarnings('once', str(warning))


    def _show_warning():
        warnings.warn(warning, stacklevel=3)


    def check_memory_deg(*args, **kwargs):
        _show_warning()
        return 0


    class MemoryTracker:
        def __enter__(self):
            return self

        def __call__(self, *args, **kwargs):
            return 0

        def __exit__(self, exc_type, exc_val, exc_tb):
            _show_warning()
            return None

        def __lt__(self, other):
            return True
else:
    import os
    import gc

    proc = psutil.Process(os.getpid())


    def check_memory_deg(func, run_times=100):
        floor = proc.memory_info().rss
        after_alloc = []
        bfa = None
        for _ in range(run_times):
            bfa = func()
            after_alloc.append(proc.memory_info().rss)
            bfa = None
        after_alloc = sum(after_alloc) / len(after_alloc)
        after_free = proc.memory_info().rss - floor
        return after_free / after_alloc


    class MemoryTracker:
        def __init__(self):
            self.floor = None
            self.on_exit = None
            self.ceil = None

        def __enter__(self):
            self.floor = proc.memory_info().rss
            self.ceil = 0
            return self

        def __call__(self):
            rss = proc.memory_info().rss - self.floor
            if rss > self.ceil:
                self.ceil = rss
            return rss

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type:
                return None

            self.on_exit = proc.memory_info().rss - self.floor

        def __lt__(self, other):
            return (self.on_exit / self.ceil) < other
