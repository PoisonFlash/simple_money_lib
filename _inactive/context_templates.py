from abc import ABC, abstractmethod
from _inactive.currency_context import CurrencyContext


class BaseCurrencyContext(ABC):

    @classmethod
    @abstractmethod
    def activate(cls):
        """Activate the currency context for the platform."""
        pass


class DefaultCurrencyContext(BaseCurrencyContext):
    @classmethod
    def activate(cls):
        CurrencyContext.reset()
        CurrencyContext.set_default_currency('XXX')
        print("INFO", "Default currency context activated")


class TraderaCurrencyContext(BaseCurrencyContext):
    @classmethod
    def activate(cls):
        CurrencyContext.set_default_currency('SEK')
        CurrencyContext.set_currency_symbol('kr', 'SEK')
        print("INFO", "Tradera currency context activated")


class DanishCurrencyContext(BaseCurrencyContext):
    @classmethod
    def activate(cls):
        CurrencyContext.set_default_currency('DKK')
        CurrencyContext.set_currency_symbol('kr', 'DKK')


DefaultCurrencyContext.activate()
