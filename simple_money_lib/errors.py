class CurrencyExistsError(ValueError):
    """Raised when trying to register a currency that already exists."""
    def __init__(self, code: str):
        super().__init__(f"Currency with code '{code}' is already registered.")
        self.code = code

class CurrencyNotRegisteredError(ValueError):
    """Raised when trying to access an unregistered currency."""
    def __init__(self, code: str):
        super().__init__(f"Currency with code '{code}' is not registered.")
        self.code = code
