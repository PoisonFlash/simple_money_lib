from moneyed import *


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
    _default_currency: Currency = None

    @classmethod
    def set_default_currency(cls, currency: str) -> None:
        """Set the default currency for the current session."""
        cls._default_currency = Currency(currency)

    @classmethod
    def get_default_currency(cls) -> Currency:
        """Get the default currency for the current session."""
        if cls._default_currency is None:
            raise ValueError("No default currency has been set.")
        return cls._default_currency

    @classmethod
    def set_currency_symbol(cls, symbol: str, currency: str) -> None:
        """Set or override symbol / shortcut for a currency."""
        currency_str = str(currency).upper()
        symbol = symbol.upper()
        if currency_str not in CURRENCIES.keys():
            raise ValueError(f"Unknown currency: '{currency}'")
        cls._substitutions[symbol] = Currency(currency_str)

    @classmethod
    def get_currency(cls, currency_symbol: str) -> Currency:
        """Get the currency for the given symbol. Raises ValueError if not found."""
        symbol = currency_symbol.upper()
        if symbol in cls._substitutions.keys():
            return cls._substitutions[symbol]
        elif symbol in CURRENCIES.keys():
            return CURRENCIES[symbol]
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


