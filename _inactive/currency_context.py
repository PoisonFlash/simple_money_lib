from simple_money_lib.currency import Currency
from simple_money_lib.currencies.all import *

class CurrencyContext:
    _predefined_substitutions: dict = {
        "$": USD,  # United States Dollar
        "€": EUR,  # Euro
        "£": GBP,  # British Pound Sterling
        "¥": CNY,  # Chinese Yuan by default (can be JPY depending on preference)
        "₹": INR,  # Indian Rupee
        "₽": RUB  # Russian Ruble
    }
    _substitutions = _predefined_substitutions.copy()
    _default_currency: Currency | None = None

    @classmethod
    def set_default_currency(cls, currency_code: str) -> None:
        """Set the default currency for the current session."""
        cls._default_currency = Currency.get(currency_code)

    @classmethod
    def get_default_currency(cls) -> Currency:
        """Get the default currency for the current session."""
        if cls._default_currency is None:
            raise ValueError("No default currency has been set.")
        return cls._default_currency

    @classmethod
    def set_currency_symbol(cls, symbol: str, currency_code: str) -> None:
        """Set or override symbol / shortcut for the given currency."""
        currency_code_upper = str(currency_code).upper()
        symbol = symbol.upper()
        if not Currency.get(currency_code_upper):
            raise ValueError(f"Unknown currency: '{currency_code}'")
        cls._substitutions[symbol] = Currency.get(currency_code_upper)

    @classmethod
    def get_currency(cls, currency_symbol: str) -> Currency:
        """Get the currency for the given symbol. Raises ValueError if not found."""
        symbol = currency_symbol.upper()
        if symbol in cls._substitutions.keys():
            return cls._substitutions[symbol]
        elif c := Currency.get(symbol):
            return c
        else:
            raise ValueError(f"Unknown currency: '{currency_symbol}'")

    @classmethod
    def get_all_symbols(cls) -> dict:
        """Returns the full currency substitutions dictionary."""
        return cls._substitutions

    @classmethod
    def reset(cls) -> None:
        cls._default_currency = None
        cls._substitutions = cls._predefined_substitutions.copy()


