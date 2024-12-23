
class CurrencySerializationError(Exception):
    """Raised when a serialization operation (save/load) with currencies fails"""
    pass

class CurrencyExistsError(ValueError):
    """Raised when trying to register a currency that already exists."""
    def __init__(self, code: str):
        super().__init__(f"Currency with code '{code}' is already registered.")
        self.code = code

class CurrencyCodeInvalid(ValueError):
    """Raised when an invalid currency code is passed: not a string and less than 3 symbols"""
    def __init__(self, code: str):
        super().__init__(f"Invalid currency code: '{code}'")
        self.code = code

class CurrencyNotFoundError(ValueError):
    """Raised when currency metadata for provided code is not found."""
    def __init__(self, code: str):
        super().__init__(
            f"Currency '{code}' not found."
            f"Ensure it is registered using `Currency.register` or exists in predefined metadata."
        )
        self.code = code

class CurrencyMismatch(TypeError):
    """Raised when trying to conduct operations on different currencies."""
    def __init__(self, message="Currencies must be the same for this operation"):
        super().__init__(message)

class MoneyDivisionIllegal(TypeError):
    """Raised when trying to divide by Money."""
    def __init__(self, message="Cannot divide by a Money instance."):
        super().__init__(message)

class MoneyInvalidOperation(TypeError):
    """Raised when attempting to perform an operation between Money and unsupported type"""
    def __init__(self, operation, type_other):
        super().__init__(f"Unsupported operand type(s) for {operation}: 'Money' and '{type_other}'")