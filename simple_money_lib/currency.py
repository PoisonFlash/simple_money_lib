from __future__ import annotations
from typing import Dict
import threading

from simple_money_lib.errors import CurrencyNotFoundError, CurrencyExistsError, CurrencyCodeInvalid
from simple_money_lib.currency_serialize import load_currencies, save_user_currencies

_predefined_currencies, _user_defined_currencies = load_currencies()

class Currency:

    # Class-level registry for unique instances
    _registry: Dict[str, Currency] = {}
    _lock: threading.Lock = threading.Lock()
    strict_mode: bool = False  # Default to non-strict behavior

    def __new__(cls, code: str):
        if not cls._is_valid_code(code):
            raise CurrencyCodeInvalid(code)
        code = code.upper().strip()
        with cls._lock:
            if code in cls._registry:
                return cls._registry[code]

            if metadata := cls._resolve_metadata(code):
                numeric = metadata['numeric']
                sub_unit = metadata['sub_unit']
                name = metadata['name']
            else:
                raise CurrencyNotFoundError(code)

            # Create a new instance and store it in the registry
            instance = super().__new__(cls)
            instance._code = code
            instance._numeric = metadata['numeric']
            instance._sub_unit = metadata['sub_unit']
            instance._name = metadata['name']
            cls._registry[code] = instance
            return instance

    @property
    def code(self):
        return self._code

    @property
    def numeric(self):
        return self._numeric

    @property
    def sub_unit(self):
        return self._sub_unit

    @property
    def name(self):
        return self._name

    @staticmethod
    def _is_valid_code(code) -> bool:
        """
        Validate a currency code.
        - Must be a string.
        - Length must be between 3 and 8 characters (inclusive).
        - Must start with a letter.
        - Can only contain letters, digits, and underscores.
        """
        if not isinstance(code, str):
            return False
        code = code.strip()
        if len(code) < 3 or len(code) > 8:
            return False
        if not code[0].isalpha():
            return False
        if not all(c.isalnum() or c == "_" for c in code):
            return False
        return True

    @classmethod
    def _resolve_metadata(cls, code: str) -> dict | None:
        """
        Resolve metadata for a currency code, checking both predefined and dynamic records.
        It must always be called from within a locked context to maintain thread safety!
        """
        for source in (_predefined_currencies, _user_defined_currencies):
            if code in source:
                return source[code]
        return None

    @classmethod
    def register(cls, code: str, numeric: int | None, sub_unit: int | None, name: str) -> Currency:
        """Register a new currency dynamically by adding metadata and relying on __new__."""
        if not cls._is_valid_code(code):
            raise CurrencyCodeInvalid(code)
        code = code.upper().strip()
        instance = None
        do_save = False
        with cls._lock:
            # Prevent duplicates
            if cls._registry.get(code):
                # Already registered
                if cls.strict_mode:
                    raise CurrencyExistsError(code)
                else:
                    instance = cls._registry.get(code)
            elif cls._resolve_metadata(code) is not None:
                # Not registered, but known
                if cls.strict_mode:
                    raise CurrencyExistsError(code)
            else:
                # Not registered and not found - Add the new currency to the metadata source
                _user_defined_currencies[code] = {
                    'numeric': numeric,
                    'sub_unit': sub_unit,
                    'name': name
                }
                do_save = True


        # Process outside the lock
        if instance is None:
            if do_save:
                # Save updated user_defined currencies
                save_user_currencies(_user_defined_currencies)
            # Create a new currency instance using __new__
            instance = cls(code)

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
        return f"Currency(code='{self.code}', name='{self.name}', numeric='{self.numeric}, sub_unit={self.sub_unit}')"

# Currency.strict_mode = False
# a = Currency.register("USD", numeric=1000, sub_unit=8, name="Bitcoin")
# print('A', repr(a))
# b = Currency.register("BTC", numeric=1000, sub_unit=8, name="Bitcoin")
# print('B', repr(b))
# print(a is b)
# print(a is Currency('USD'))
