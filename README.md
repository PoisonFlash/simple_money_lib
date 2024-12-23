# simple_money_lib

Thread-safe and parsing-friendly Python library for a powerful yet simple operations with moneys and currencies.

## Overview

`simple_money_lib` is a lightweight library designed for working with currencies and monetary values in Python. It is built with a focus on thread safety, flexibility, and ease of use, catering to both simple and advanced financial operations.
The main focus is consistent and precise representation of monetary amounts in different currencies, and ease and intuitiveness of use.

### Key Features

| Feature                         | Description                                                                                                               |
|---------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| **Thread Safety**               | Thread-safe with dedicated managers for parsing and rounding, ensuring consistent behavior in multi-threaded environments. |
| **Dynamic Currency Management** | Supports dynamic registration of currencies, with persistent metadata stored in JSON files.                               |
| **Predefined Currencies**       | Preloaded from `predefined_currencies.json` and extendable via modular design.                                            |
| **Currency Collections**        | Includes `CurrencyCollection` for grouping and managing multiple currencies.                                              |
| **String Parsing**              | Robust monetary string parsing with customizable parsers that support thread-local and global configurations.             |
| **Rounding Management**         | Configurable rounding modes with global and thread-local support for flexible operations.                                 |
| **Custom Exceptions**           | Set of exceptions for validation and error handling                                                                       |
| **Lightweight Design**          | Minimal runtime dependencies.                                                                                             |
| **Modular Architecture**        | Designed for modular extensions, supporting predefined, user-defined, and future modules like cryptocurrencies.           |
| **Python 3.10+ Compatibility**  | Leverages modern Python features, such as `typing`, `dataclasses`, and pattern matching.                                  |

### Highlights
- **Dynamic and Persistent Currencies**: Add new currencies dynamically and save them for future use.
- **Flexible Rounding and Parsing**: Manage rounding and parsing behaviors globally or locally for individual threads.
- **Modern Python Design**: Built with modern Python features for improved readability and performance.
- **Error Handling**: Provides robust validation and error handling for invalid or missing currencies.

### Use Cases
- **Financial Applications**: Suitable for building applications that require accurate handling of monetary values.
- **Parsing**: Suitable for parsing monetary values with inconsistent formatting and currency representations.
- **Custom Currency Support**: Easily add and persist new currencies, such as cryptocurrencies or region-specific ones.
- **Multithreaded Environments**: Designed to perform reliably in multithreaded applications.

### Exclusions
- **Currency conversion**: Not supported. Use a specialized library designed for your specific needs. The reason is that currency conversion requires additional parameters : date, time and the specific converter for accurate and replicable calculations. It would increase complexity and introduce a number of dependencies which might not be needed by many potential users, going against the concept of a **simple** and lightweight money library.
- **Locale formatting**: Not directly supported. Use `babel` or a similar library. There is a helper method to convert Money objects to a suitable format. The reason is to control complexity and minimize dependencies.

### Technical Details
- `Money` objects contain a `Decimal` object with **fixed number of decimal points** and a `Currency` object.
- Number of decimal points as per **ISO 4217** standard, or, for custom currencies, according to registration parameters. Create a custom currency if a different precision is needed (e.g., USD4).
- `Currency` is determined by `code` parameter. All `Currency` objects with the same `code` are pointers to the same instance. 
- Thread safety is accomplished with usage of thread locks and local thread variables.

## Installation

There are no external dependencies. Just clone the repository and install using pip:

```bash
pip install git+https://github.com/PoisonFlash/simple_money_lib.git
```

## Getting Started with `simple_money_lib`

`simple_money_lib` makes it simple to work with currencies and monetary values. Here’s a quick overview of its core features and usage examples.

### 1. Creating Currencies
Define or retrieve a currency using its ISO code:
```python
from simple_money_lib.currency import Currency
from simple_money_lib.errors import CurrencyExistsError

# Import a predefined currency
from simple_money_lib.currencies.all import EUR, USD
print(EUR)  # Output: EUR

# Retrieve a predefined currency
usd = Currency("USD")
print(usd)  # Output: USD
print(usd is USD)  # Output: True - the imported and retrieved currency is the same object

# Dynamically register a new currency
btc = Currency.register(code="BTC", numeric=1000, sub_unit=8, name="Bitcoin")
print(btc)  # Output: BTC
# The registration is persistent
# Try to register again in default mode, with different numeric value
try:
    btc2 = Currency.register(code="BTC", numeric=10000, sub_unit=8, name="Bitcoin")
except CurrencyExistsError:
    pass
else:
    print("This works when strict mode is off (default).")

# The registered currency is not overwritten by subsequent registrations
print(btc2.numeric)  # Output: 1000, not 10000

# Try to register again in strict mode
Currency.strict_mode = True
try:
    btc3 = Currency.register(code="BTC", numeric=1000, sub_unit=8, name="Bitcoin")
except CurrencyExistsError:
    print("If strict mode is on, trying to register a currency again will raise an error")
```

To edit a custom currency, find it in `data/user_currencies.json` and edit manually.

### 2. Creating Money Objects

Work with monetary values by combining an amount and a currency:

```python
from simple_money_lib.money import Money
from simple_money_lib.currencies.all import USD

# Create a money object - option 1
money = Money(100, "USD")
print(money)  # Output: 100.00 USD

# Create a money object - option 2
money = Money(100, USD)
print(money)  # Output: 100.00 USD

# Create a money object - option 3
money = Money('USD 100')  # Or '100 USD'
print(money)  # Output: 100.00 USD

# Default currency is configurable
default_money = Money(50)
print(default_money)  # Output: 50.00 XXX (default currency can be set globally)
```

### 3. Arithmetic Operations

Arithmetic operations can be performed between Money objects with the same Currency and numeric types (int, float, Decimal) as makes sense.

```python
from simple_money_lib.money import Money
import decimal
# Addition and subtraction: between Money objects
money1 = Money(100, "USD")
money2 = Money("50 USD")
print(money1 + money2)       # Output: 150.00 USD
print(money1 - money2)       # Output: 50.00 USD

# Multiplication and division: between Money and numeric types
print(money1 * 2)            # Output: 200.00 USD
print(money1 / 2)            # Output: 50.00 USD
print(Money("5 EUR") // 3)   # Output: 1.00 EUR
print(Money("5 EUR") % 3)    # Output: 2.00 EUR

# Possibility to keep track of amounts lost due to quantization / rounding
result, adjustment = Money("20 USD").divide_with_adjustment(7)
print(result, adjustment)    # Output: 2.85 USD, 0.05 USD
# Explanation: 2.85 * 7 => 19.95, 20.00 - 19.95 = 0.05

# Absolute value
print(abs(Money("-5 EUR")))  # Output: 5.00 EUR
print(abs(Money("5 EUR")))   # Output: 5.00 EUR

# Rounding operations
money = Money("15.25 EUR")
# Pre-set default behaviour is ROUND_DOWN
print(round(money, 1))        # Output: 15.20 EUR
Money.rounding.set_default(decimal.ROUND_HALF_UP)
print(round(money, 1))        # Output: 15.30 EUR
# It is possible to change rounding mode for the current thread independently on global default:
Money.rounding.set_default(decimal.ROUND_UP)
print(round(money, 1))        # Output: 15:30 EUR
Money.rounding.set(decimal.ROUND_DOWN)
print(round(money, 1))        # Output: 15:20 EUR
Money.rounding.reset()        # Local thread rounding reset, default will be used
print(round(money, 1))        # Output: 15:30 EUR
# Rounding to decimal digits greater than allowed subunit results in the same amount
print(round(money, 3))        # Output: 15.25 - only two decimal digits are allowed

# Comparison operations: <, >, ==, !=, >=, <=
money1 = Money("15.25 EUR")
money2 = Money("15 EUR")
print(money2 < money1)        # Output: True
print(money == money1)        # Output: True
```

### 4. Currency Collections

Currencies are grouped into modules and collections for ease of import.

```python
from simple_money_lib.currencies import all_iso_currencies, brics_currencies, major_currencies
from simple_money_lib.currencies.all import XXX, EUR, USD
from simple_money_lib.currencies.brics import BRL
print(XXX in all_iso_currencies)  # True
print(USD in major_currencies)    # True - note that USD is imported from simple_money_lib.currencies.all
print(EUR in brics_currencies)    # True
print(BRL in all_iso_currencies)  # True - note that BRL is imported from simple_money_lib.currencies.brics

# If you want all 'standard' currencies, do the following:
from simple_money_lib.currencies.all import *
# This is primarily useful for readability of auto-generated modules.
```

Custom collections can be created. Custom collections are NOT persistent.

```python
from simple_money_lib.currencies.currency_collections import CurrencyCollection
from simple_money_lib.currencies.all import SEK, NOK, DKK, EUR, USD

scandinavian_currencies = CurrencyCollection(
    'SEK', NOK, DKK, EUR,               # It is ok to mix Currency objects and valid code strings
    name='scandinavian',
    description='Currencies in use in Scandinavia'
)
print(SEK in scandinavian_currencies)   # True
print(USD in scandinavian_currencies)   # False
```

### 5.1. Customizing `Money` behaviour: rounding

`Money` class is handling rounding / quantization internally. It uses rounding modes from `decimal` module. The default rounding mode is `decimal.ROUND_DOWN`.
Manipulating `Money.rounding` parameter allows to customize rounding behaviour.

```python
import decimal
from simple_money_lib.money import Money

money = Money("20.26 USD")

# All-thread rounding defaults
print(f'Global: {Money.rounding.get_default()}')   # Output: Global: ROUND_DOWN
# Rounding to 1 decimal digit
print(round(money, 1))                             # Output: 20.20 USD
Money.rounding.set_default(decimal.ROUND_HALF_UP)  # Change global default in a thread-safe manner
print(round(money, 1))                             # Output: 20.30 USD

# Local thread rounding
# Global default, as no local mode is set yet
print(f'Thread: {Money.rounding.get()}')           # Output: Thread: ROUND_HALF_UP
print(round(money, 1))                             # Output: 20.30 USD

# Global default will be used as no value is provided
Money.rounding.set()
# Local thread has now been set with global value:
print(f'Thread: {Money.rounding.get()}')           # Output: Thread: ROUND_HALF_UP
print(round(money, 1))                             # Output: 20.30 USD

# Change global default
Money.rounding.set_default(decimal.ROUND_DOWN)
print(round(money, 1))                             # Output: 20.30 USD - Local thread is used, not global
print(f'Global: {Money.rounding.get_default()}')   # Output: Global: ROUND_DOWN
print(f'Thread: {Money.rounding.get()}')           # Output: Thread: ROUND_HALF_UP

# Fire rounding in a separate thread to demonstrate difference
def thread_function():
    print(f'[Thread-2] Global: {Money.rounding.get_default()}')  # Output: Global: ROUND_DOWN
    print(f'[Thread-2] Local: {Money.rounding.get()}')           # Output: Local: ROUND_DOWN as no local is set for this thread
    print(round(money, 1))                                       # Output: 20.20 USD - global default used

import threading
thread = threading.Thread(target=thread_function)
thread.start()
thread.join()
```

### 5.2. Customizing `Money` behaviour: default currency

Default currency allows to initialize `Money` with just an amount: `Money(100)`.
By default, currency `XXX` will be used, as defined in **ISO 4217**. Note that number of decimal points for 'XXX' and other currencies without specified sub-units will be 2.
Manipulating `Money.default_currency` parameter allows to customize rounding behaviour. The operations are thread-safe.

Changing default currency can be especially useful when processing numeric data where currency is implied but not specified. As with the most of external data.
Note that the default currency can only be set globally, not per thread. The reason is that setting a default currency is envisaged as a set-once initialization operation. E.g., to set up an accounting currency.
For other scenarios, like processing separate data streams with different unspecified currencies, it is recommended to specify currency explicitly on instance creation, e.g. `Money(amount=data_point, currency=known_currency)`, or set up a custom parser. 

```python
from simple_money_lib.money import Money
from simple_money_lib.currencies.all import XXX, JPY

# Default currency XXX with two decimal points
print(Money(100))                       # Output: 100.00 XXX
assert Money.default_currency.get() is XXX

# Change default currency
Money.default_currency.set("JPY")       # Provide valid code string or Currency instance: imported JPY or "JPY"
assert Money.default_currency.get() == JPY
assert Money.default_currency.get() is JPY
print(Money(100))                       # Output: 100 JPY - Note no decimal points for Japanese Yen
```

### 5.3. Customizing `Money` behaviour: parsers

