from simple_money_lib import Currency
from simple_money_lib.currencies.major import *
from simple_money_lib.currencies.brics import *
from simple_money_lib.currencies.all import RUB

print(EUR in major_currencies, EUR in brics_currencies)
print(RUB in major_currencies, RUB in brics_currencies)

eur = Currency(EUR)
print(eur is EUR)