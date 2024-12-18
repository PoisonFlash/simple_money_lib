import threading
from simple_money_lib.currency import Currency
from simple_money_lib.currencies.all import XXX

class DefaultCurrency:
    """Manages the global default currency with thread safety."""
    _default_currency = XXX  # Default to ISO 'XXX'
    _lock = threading.Lock()

    @classmethod
    def set(cls, currency: Currency | str = XXX) -> None:
        """
        Set the global default currency in a thread-safe manner.
        Arguments:
            currency: Currency object, or a string with valid currency code. Default is ISO's XXX, representing
                      undefined currency.
        """
        with cls._lock:
            cls._default_currency = Currency(currency)

    @classmethod
    def get(cls) -> Currency:
        """Get the global default currency in a thread-safe manner."""
        with cls._lock:
            return cls._default_currency
