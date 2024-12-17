import threading

from simple_money_lib import Currency
from simple_money_lib.currencies.all import XXX
from simple_money_lib.parsers import BaseParser

# TODO: This is not going to work, I need to implement the functionality separately in the Money class for now

class MoneyContext:
    """Base thread-safe context for Money operations."""
    _thread_local = threading.local()

    def __init__(
            self,
            rounding=None,  # Should this be RoundingManager singleton instance?
            parser: BaseParser | None = None,
            default_currency: Currency | str | None = None
    ):
        self.rounding = rounding
        self.parser = parser if parser else BaseParser()
        self.default_currency = Currency(default_currency) if default_currency else XXX
        self.previous_settings = {}

    def __enter__(self):
        # Save current settings
        self.previous_settings = {
            "rounding": getattr(MoneyContext._thread_local, "rounding", None),
            "parser": getattr(MoneyContext._thread_local, "parser", None),
            "default_currency": getattr(MoneyContext._thread_local, "default_currency", None),
        }

        # Apply new settings
        if self.rounding is not None:
            MoneyContext._thread_local.rounding = self.rounding
        if self.parser is not None:
            MoneyContext._thread_local.parser = self.parser
        if self.default_currency is not None:
            MoneyContext._thread_local.default_currency = self.default_currency

    def __exit__(self, exc_type, exc_value, traceback):
        # Restore previous settings
        MoneyContext._thread_local.rounding = self.previous_settings["rounding"]
        MoneyContext._thread_local.parser = self.previous_settings["parser"]
        MoneyContext._thread_local.default_currency = self.previous_settings["default_currency"]

    @staticmethod
    def get_current_rounding():
        return getattr(MoneyContext._thread_local, "rounding", None)

    @staticmethod
    def get_current_parser() -> BaseParser:
        return getattr(MoneyContext._thread_local, "parser", None)

    @staticmethod
    def get_current_default_currency() -> Currency:
        return getattr(MoneyContext._thread_local, "default_currency", None)
