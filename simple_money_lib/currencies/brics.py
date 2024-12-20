# Auto-generated module
# CHECKLINE 2024-12-20 12:16:22

from simple_money_lib.currency import Currency as _Currency
from simple_money_lib.currencies.currency_collections import CurrencyCollection as _CurrencyCollection

# Export individual currencies
BRL = _Currency("BRL")
RUB = _Currency("RUB")
INR = _Currency("INR")
CNY = _Currency("CNY")
ZAR = _Currency("ZAR")
IRR = _Currency("IRR")
EGP = _Currency("EGP")
ETB = _Currency("ETB")
AED = _Currency("AED")

brics_currencies = _CurrencyCollection(
    BRL, RUB, INR, CNY, ZAR, IRR, EGP, ETB, AED,
    name="brics",
    description="Currencies of 9 nine BRICS member states"
)

__all__ = ["BRL", "RUB", "INR", "CNY", "ZAR", "IRR", "EGP", "ETB", "AED", "brics_currencies"]
