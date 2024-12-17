import threading
from simple_money_lib.parsers.base_parser import BaseParser

class ParserManager:
    """Manages thread-local and global parsers in a thread-safe manner."""

    _global_lock = threading.Lock()
    _thread_local = threading.local()
    _global_default_parser = BaseParser()  # Default global parser

    def set_default(self, parser: BaseParser):
        """Set the global default parser."""
        with self._global_lock:
            self._global_default_parser = parser

    def get_default(self) -> BaseParser:
        """Get the global default parser."""
        with self._global_lock:
            return self._global_default_parser

    def set(self, parser: BaseParser):
        """Set a thread-local parser."""
        self._thread_local.parser = parser

    def get(self) -> BaseParser:
        """Get the effective parser: thread-local or global default."""
        return getattr(self._thread_local, "parser", None) or self.get_default()

    def reset(self):
        """Reset the thread-local parser to the global default."""
        if hasattr(self._thread_local, "parser"):
            del self._thread_local.parser
