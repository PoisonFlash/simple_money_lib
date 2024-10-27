from moneyed import Currency

from babel.numbers import get_currency_symbol

for item in ['USD', 'SEK', 'EUR', 'RUB', 'INR']:
    print(item, get_currency_symbol(item))
