from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, Dict
import threading

from simple_money_lib.errors import CurrencyExistsError

@dataclass(frozen=True, slots=True)
class Currency:
    # ISO-based
    code: str
    numeric: int | None = None
    sub_unit: int | None = 2
    name: str | None = None

    # Class-level registry for unique instances
    _registry: ClassVar[Dict[str, Currency]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()
    strict_mode: ClassVar[bool] = True  # Default to strict behavior

    def __new__(cls, code: str, numeric: str | None = None, sub_unit: int = 2, name: str | None = None):
        with cls._lock:
            if code in cls._registry:
                if cls.strict_mode:
                    raise CurrencyExistsError(code)
                # Relaxed mode: return the existing instance
                return cls._registry[code]

            # Create a new instance and store it in the registry
            instance = object.__new__(cls)
            cls._registry[code] = instance
            return instance

    @classmethod
    def get(cls, code: str) -> Currency | None:
        """Get currency instance or None if not registered"""
        with cls._lock:
            if code not in cls._registry:
                return None
            return cls._registry[code]

    @classmethod
    def all_currencies(cls) -> Dict[str, Currency]:
        """Return a snapshot of all registered currencies."""
        with cls._lock:
            return cls._registry.copy()

    def __str__(self):
        return self.code

    def __repr__(self):
        return f"Currency(code='{self.code}', name='{self.name}', numeric='{self.numeric}')"
