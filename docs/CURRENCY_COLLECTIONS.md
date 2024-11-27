# CurrencyCollection Class Documentation
## **Overview**

The CurrencyCollection class provides a way to group and manage sets of currencies (Currency objects or valid currency codes). It supports operations such as membership checks, iteration, and grouping currencies under a collection name with an optional description.

This class is particularly useful for categorizing currencies into predefined groups (e.g., major currencies, BRICS currencies) or dynamically creating custom collections.
## Features

- **Initialization with Mixed Inputs**:
  - Accepts a combination of Currency objects and valid currency codes (e.g., "USD", "EUR").
  - Automatically resolves string inputs into Currency objects.

- **Membership Checking**:
  - Allows checking if a Currency object or a valid currency code is part of the collection using the in operator.

- **Iteration**:
  - Supports iteration over the collection, yielding Currency objects.

- **Metadata**:
  - Collections can be assigned an optional name and description.

- **Graceful Handling of Invalid Codes**:
  - During initialization, invalid currency codes raise a CurrencyCodeInvalid exception.
  - Membership checks ("XYZ" in collection) do not raise exceptions but return False for invalid or unregistered currencies.

## Usage Examples
### Initialization

```python
from simple_money_lib.currency import Currency
from simple_money_lib.collections.currency_collections import CurrencyCollection
```

### Create a collection with a mix of valid codes and Currency objects:

```python
collection = CurrencyCollection("USD", "EUR", Currency("RUB"), name="Major Currencies", description="Most used currencies")

print(collection.name)  # Output: Major Currencies
print(collection.description)  # Output: Most used currencies
```

### Membership checks
```python
# Check if a currency is in the collection
assert "USD" in collection
assert Currency("USD") in collection
assert "XYZ" not in collection  # Invalid/unregistered code

# Membership checks do not raise exceptions for invalid codes
assert "123" not in collection
```
### Iteration
```python
# Iterate over the collection
for currency in collection:
    print(currency.code)

# Output:
# USD
# EUR
# RUB
```
### Handling Invalid Codes
```python
from simple_money_lib.errors import CurrencyCodeInvalid

# Raises CurrencyCodeInvalid because '123' is not a valid currency code
try:
    collection = CurrencyCollection("USD", "123", "RUB")
except CurrencyCodeInvalid as e:
    print(e)  # Output: Invalid currency code: '123'
```

## Class API
```python
class CurrencyCollection:
    def __init__(self, *currencies, name=None, description=None):
        """
        Initialize a CurrencyCollection with a set of currencies.

        :param currencies: A mix of Currency objects and valid string codes.
        :param name: Optional name for the collection (e.g., "Major Currencies").
        :param description: Optional description for the collection.
        :raises CurrencyCodeInvalid: If an invalid currency code is used during initialization.
        """
        ...

    def __contains__(self, item):
        """
        Check if a currency is in the collection.

        :param item: A Currency object or a valid string code.
        :return: True if the currency is in the collection, False otherwise.
        """
        ...

    def __iter__(self):
        """
        Iterate over the Currency objects in the collection.

        :return: An iterator over Currency objects.
        """
        ...

    def __repr__(self):
        """
        Return a string representation of the CurrencyCollection.

        :return: A string showing the codes of all currencies in the collection.
        """
        ...
```

## Exceptions
### CurrencyCodeInvalid
Raised during initialization if an invalid currency code (e.g., "123", "@$#", "") is provided.
```python
from simple_money_lib.errors import CurrencyCodeInvalid

try:
    collection = CurrencyCollection("USD", "123", "EUR")
except CurrencyCodeInvalid as e:
    print(e)  # Output: Invalid currency code: '123'
```
### Membership Checks
Invalid or unregistered codes (e.g., "XYZ", "123") return False without raising exceptions during membership checks.
```python
collection = CurrencyCollection("USD", "EUR")
assert "XYZ" not in collection  # Returns False
```

## Key Notes

Strict Validation During Initialization:
- All input currency codes are validated when creating a collection. Invalid codes are not allowed and result in a CurrencyCodeInvalid exception.

Graceful Membership Checks:
- Membership checks handle invalid or unregistered currencies by returning False instead of raising errors.

Extensibility:
- The class can be extended or used with dynamically registered currencies via Currency.register.
