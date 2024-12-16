import decimal
import threading


class RoundingManager:
    """Manages thread-local and global rounding modes in a thread-safe manner."""

    _global_lock = threading.Lock()
    _global_default_rounding = decimal.ROUND_DOWN
    _thread_local = threading.local()

    def set_default(self, rounding_mode):
        """Set the global default rounding mode, using decimal module parameters, e.g., decimal.ROUND_DOWN."""
        with self._global_lock:
            self._global_default_rounding = rounding_mode

    def get_default(self):
        """Get the global default rounding mode."""
        with self._global_lock:
            return self._global_default_rounding

    def set(self, rounding_mode=None):
        """Set the thread-local rounding mode, using decimal module parameters, e.g., decimal.ROUND_DOWN."""
        if rounding_mode:
            self._thread_local.rounding = rounding_mode
        else:
            self._thread_local.rounding = self.get_default()

    def get(self):
        """Get the effective rounding mode: thread-local or global default."""
        return getattr(self._thread_local, "rounding", None) or self.get_default()

    def reset(self):
        """Reset the thread-local rounding mode to default."""
        if hasattr(self._thread_local, "rounding"):
            del self._thread_local.rounding

