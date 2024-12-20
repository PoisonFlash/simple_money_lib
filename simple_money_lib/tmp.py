from simple_money_lib import Currency
from simple_money_lib.errors import CurrencyExistsError

btc = Currency.register(code="BTC", numeric=1000, sub_unit=8, name="Bitcoin")
print(btc)
try:
    btc2 = Currency.register(code="BTC", numeric=10000, sub_unit=8, name="Bitcoin")
except CurrencyExistsError:
    pass
else:
    print("This works when strict mode is off (default)")
print(btc2.numeric)

Currency.strict_mode = True
try:
    btc3 = Currency.register(code="BTC", numeric=1000, sub_unit=8, name="Bitcoin")
except CurrencyExistsError:
    print("If strict mode is on, trying to register a currency again will raise an error")
