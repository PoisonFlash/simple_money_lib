
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

# class CurrencyNotRegisteredError(ValueError):
#     """Raised when trying to access an unregistered currency."""
#     def __init__(self, code: str):
#         super().__init__(f"Currency with code '{code}' is not registered.")
#         self.code = code

class CurrencyNotFoundError(ValueError):
    """Raised when currency metadata for provided code is not found."""
    def __init__(self, code: str):
        super().__init__(
            f"Currency '{code}' not found."
            f"Ensure it is registered using `Currency.register` or exists in predefined metadata."
        )
        self.code = code
