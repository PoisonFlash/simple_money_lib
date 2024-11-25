# Currency Class Documentation

## **Summary of Features**

### **For Users**
- **Predefined and User-Defined Currencies**:
  - The library supports predefined currencies (e.g., `USD`, `EUR`, `SEK`) that can be imported directly.
  - Dynamically define user-specific currencies, including cryptocurrencies or custom codes.

- **Strict Validation of Currency Codes**:
  - Currency codes must:
    - Be 3 to 8 characters long.
    - Start with a letter.
    - Contain only letters, digits, or underscores.
  - Invalid codes raise a `CurrencyCodeInvalid` exception.

- **Singleton Behavior**:
  - Each currency is a unique object. The same object is returned for a specific code in repeated calls.

- **Thread-Safe Design**:
  - Prevents duplicate instances in multi-threaded environments.

- **Extensible Metadata System**:
  - Metadata for predefined currencies is stored separately from user-defined currencies, which can persist across sessions.

---

### **For Developers**

- **Validation via `_is_valid_code`**:
  - A static method ensures that currency codes follow strict validation rules.

- **Thread-Safe Singleton Enforcement**:
  - Uses `_registry` and `_lock` to ensure no duplicate currency objects are created.

- **Dynamic Registration via `register`**:
  - Dynamically add new currencies with:
    ```python
    Currency.register(code, numeric, sub_unit, name)
    ```

- **Custom Error Handling**:
  - Exceptions include:
    - `CurrencyCodeInvalid`: Raised for invalid currency codes.
    - `CurrencyExistsError`: Raised if attempting to register a duplicate in strict mode.
    - `CurrencyNotFoundError`: Raised when unresolved codes are referenced dynamically.

- **Flexible Import Options**:
  - Predefined currencies can be directly imported:
    ```python
    from currencies.all import USD
    ```
  - Dynamically registered currencies become available after registration.

---

## **How to Use the Library**

### **1. Creating and Using Predefined Currencies**

```python
from simple_money_lib.currency import Currency

usd = Currency("USD")  # Predefined
print(usd)  # Output: Currency(code='USD', name='United States Dollar', ...)
```

---

### **2. Registering a New Currency**

```python
btc = Currency.register("BTC", numeric=1000, sub_unit=8, name="Bitcoin")
print(btc)  # Output: Currency(code='BTC', name='Bitcoin', ...)
```

---

### **3. Handling Validation**

```python
try:
    invalid_currency = Currency("U$D")  # Invalid code
except CurrencyCodeInvalid as e:
    print(e)  # Output: "Invalid currency code: U$D"
```

---

### **4. Dynamic Resolution**

```python
crypto = Currency("BTC")  # Automatically resolves if registered
```

---

### **5. Thread Safety**

```python
# Safe concurrent creation
from threading import Thread

def create_currency(code):
    print(Currency(code))

threads = [Thread(target=create_currency, args=("BTC",)) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

---

## **Technical Implementation Details**

### **Validation Rules (`_is_valid_code`)**
- A currency code must:
  1. Be a string.
  2. Be 3–8 characters long.
  3. Start with a letter.
  4. Contain only letters, digits, and underscores.

Example:

```python
@staticmethod
def _is_valid_code(code) -> bool:
    if not isinstance(code, str):
        return False
    code = code.strip()
    if len(code) < 3 or len(code) > 8:
        return False
    if not code[0].isalpha():
        return False
    if not all(c.isalnum() or c == "_" for c in code):
        return False
    return True
```

---

### **Singleton Design**

- The `_registry` ensures singleton behavior by storing unique currency objects keyed by their code.
- `__new__` enforces the following:
  1. If a currency exists in `_registry`, return the existing instance.
  2. If the code is invalid, raise `CurrencyCodeInvalid`.
  3. Dynamically resolve metadata for new currencies.

---

### **Dynamic Registration**

- Use `register` to define new currencies dynamically:
```python
Currency.register("BTC", numeric=1000, sub_unit=8, name="Bitcoin")
```
- Registered currencies persist in `_user_defined_currencies`, ensuring they remain available across sessions.

---

### **Thread Safety**

- `_lock` ensures atomicity when accessing `_registry` or `_user_defined_currencies`.
- Prevents duplicate currency creation in multi-threaded environments.

---

### **Custom Error Handling**

1. **`CurrencyCodeInvalid`**:
   - Raised for invalid currency codes.
   ```python
   raise CurrencyCodeInvalid("Invalid currency code: U$D")
   ```

2. **`CurrencyExistsError`**:
   - Raised if a duplicate registration is attempted in strict mode.

3. **`CurrencyNotFoundError`**:
   - Raised if a code cannot be resolved dynamically.

---

### **Extensible Metadata**

1. **Predefined Currencies**:
   - Loaded from a JSON file during library initialization.

2. **User-Defined Currencies**:
   - Stored in a separate JSON file for persistence.
   - Updated dynamically via `register`.

---

### **Testing Support**

- Fixtures and mocks ensure a clean state between tests:
  - `_registry` is cleared after each test.
  - Mock `_user_defined_currencies` for isolated test behavior.

Example:
```python
@pytest.fixture(autouse=True)
def reset_currency_registry():
    Currency._registry.clear()
    Currency.strict_mode = False
    _user_defined_currencies.clear()
```

---

This updated documentation reflects all discussed features and recent changes to the `Currency` class. Let me know if further refinements are needed!