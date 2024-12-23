from simple_money_lib.money import Money
from simple_money_lib.currencies.all import XXX, JPY

# Default currency XXX with two decimal points
print(Money(100))               # Output: 100.00 XXX

# Change default currency
Money.default_currency.set("JPY")
assert Money.default_currency.get() == JPY

print(Money(100))               # Output: 100.00 XXX