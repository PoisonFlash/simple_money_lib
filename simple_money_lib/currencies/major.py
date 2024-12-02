# Auto-generated module
# CHECKLINE 2024-12-02 17:51:40

from simple_money_lib.currency import Currency as _Currency
from simple_money_lib.currencies.currency_collections import CurrencyCollection as _CurrencyCollection

# Export individual currencies
USD = _Currency("USD")
EUR = _Currency("EUR")
JPY = _Currency("JPY")
GBP = _Currency("GBP")
AUD = _Currency("AUD")
CAD = _Currency("CAD")
CHF = _Currency("CHF")
CNY = _Currency("CNY")
HKD = _Currency("HKD")
NZD = _Currency("NZD")

major_currencies = _CurrencyCollection(
    USD, EUR, JPY, GBP, AUD, CAD, CHF, CNY, HKD, NZD,
    name="major",
    description="10 most used currencies globally"
)

__all__ = ["USD", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "CNY", "HKD", "NZD", "major_currencies"]
