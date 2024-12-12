# **Money Class: Extended Functionality**

The `Money` class has been extended to support additional functionality inspired by dictionary-like behavior. This documentation describes the newly added methods and how they enhance the usability of the `Money` class.

---

## **Tuple-Like Behavior**

### **`__iter__`**

The `__iter__` method allows a `Money` object to be unpacked like a tuple, providing access to the `amount` and `currency` attributes.

#### **Example: Tuple Unpacking**
```python
from simple_money_lib import Money, Currency
usd = Currency("USD")
money = Money(100, usd)

amount, currency = money
print(amount)   # 100.00
print(currency) # USD
```

#### **Example: Iteration**
```python
usd = Currency("USD")
money = Money(100, usd)

for item in money:
    print(item)

# Outputs:
# 100.00
# USD
```

---

## **Dictionary-Like Behavior**

### **`as_dict`**

The `as_dict` method returns a dictionary representation of the `Money` object, with `amount` and `currency` as keys.

#### **Example: Dictionary Representation**
```python
usd = Currency("USD")
money = Money(100, usd)

print(money.as_dict())
# {'amount': Decimal('20.00'), 'currency': Currency(code='USD', name='United States dollar', numeric='840, sub_unit=2')}
```

---

### **`__getitem__`**

The `__getitem__` method enables dictionary-style access to the `amount` and `currency` attributes.

#### **Example: Accessing Components**
```python
usd = Currency("USD")
money = Money(100, usd)

print(money['amount'])   # 100.00
print(money['currency']) # USD
```

#### **Invalid Key**
```python
try:
    print(money['invalid_key'])
except KeyError as e:
    print(e)
# Outputs: 'invalid_key'
```

---

### **`keys`**

The `keys` method returns a list of the available keys (`'amount'` and `'currency'`).

#### **Example: Querying Keys**
```python
usd = Currency("USD")
money = Money(100, usd)

print(money.keys())  # ['amount', 'currency']
```

---

### **`__contains__`**

The `__contains__` method allows checking for the presence of a key using the `in` operator.

#### **Example: Key Presence**
```python
usd = Currency("USD")
money = Money(100, usd)

print('amount' in money)      # True
print('currency' in money)    # True
print('invalid_key' in money) # False
```

---

### **`items`**

The `items` method returns an iterator of key-value pairs (`('amount', amount)` and `('currency', currency)`).

#### **Example: Iterating Over Key-Value Pairs**
```python
usd = Currency("USD")
money = Money(100, usd)

for key, value in money.items():
    print(f"{key}: {value}")

# Outputs:
# amount: 100.00
# currency: USD
```

---

## **Summary of Methods**

| **Method**    | **Description**                                                                                 | **Example**                                  |
|---------------|---------------------------------------------------------------------------------------------|------------------------------------------|
| `__iter__`    | Allows unpacking as `(amount, currency)` or iteration over the `Money` object.               | `amount, currency = money`               |
| `as_dict`     | Returns a dictionary representation of the `Money` object.                                   | `money.as_dict()`                        |
| `__getitem__` | Enables dictionary-style access to `amount` and `currency`.                                  | `money['amount']`                        |
| `keys`        | Returns a list of keys (`['amount', 'currency']`).                                           | `money.keys()`                           |
| `__contains__`| Allows checking for keys (`'amount' in money`).                                              | `'amount' in money`                      |
| `items`       | Returns an iterator of key-value pairs (`('amount', amount)` and `('currency', currency)`).  | `for key, value in money.items():`       |

---

## **Notes**
1. The `Money` class remains **immutable**, ensuring that dictionary-style access is read-only.
2. These methods enhance introspection and usability while maintaining compatibility with existing functionality.

---
