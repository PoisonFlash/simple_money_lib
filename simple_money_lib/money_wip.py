from typing import overload, TypeVar
from decimal import Decimal
import decimal
import threading

import simple_money_lib.money_parser as _mp
from simple_money_lib.currency import Currency

# Ensure correct type hints for earlier versions of Python (before 3.11)
# Consider switching to Self (from typing import Self) in October 2026
M = TypeVar("M", bound="Money")

# Constants
_NUMERIC_TYPES = (int, float, Decimal)  # Permitted numeric types for operations

class Money:

    # Class constants
    _ERR_MSG_ADD_SUB = "Cannot add or subtract Money objects with different currencies"
    _ERR_MSG_MULT = "Unsupported operand type(s) for {op}: 'Money' and '{type}'"
    _ERR_MSG_DIV = "Cannot divide by a Money instance."
    _ERR_MSG_EXPN = "Exponentiation is not supported for Money objects."

    # Class-level lock for thread-safe global changes
    _global_lock = threading.Lock()
    _thread_local = threading.local()

    # Global default rounding mode
    _global_default_rounding = decimal.ROUND_DOWN

    @classmethod
    def get_rounding(cls):
        """
        Get the rounding mode. Check thread-local first; fallback to global default.
        """
        return getattr(cls._thread_local, "rounding", cls._global_default_rounding)

    @classmethod
    def set_rounding(cls, rounding=None):
        """
        Set the thread-local rounding mode.
        Parameters:
            rounding: A valid rounding mode from the decimal module (e.g., decimal.ROUND_HALF_UP).
        """
        if rounding is None:
            rounding = cls.get_global_rounding()
        cls._thread_local.rounding = rounding

    @classmethod
    def reset_rounding(cls):
        """
        Reset the thread-local rounding mode to use the global default.
        """
        if hasattr(cls._thread_local, "rounding"):
            del cls._thread_local.rounding

    @classmethod
    def set_global_rounding(cls, rounding):
        """
        Set the global default rounding mode in a thread-safe manner.
        Parameters:
            rounding: A valid rounding mode from the decimal module (e.g., ROUND_HALF_UP).
        """
        with cls._global_lock:
            cls._global_default_rounding = rounding

    @classmethod
    def get_global_rounding(cls):
        """
        Get the current global default rounding mode.
        """
        with cls._global_lock:
            return cls._global_default_rounding

    @overload
    def __init__(self, money_string: str) -> None:
        ...

    @overload
    def __init__(self, amount: Decimal | int | float | str, currency: Currency | str) -> None:
        ...

    @overload
    def __init__(self, amount: Decimal | int | float) -> None:
        ...

    def __init__(self, *args, **kwargs):

        # Dev note: always initialize self.currency first, as amount initialization requires self.currency to be set

        match args, kwargs:
            # Case: Positional amount and currency
            case (amount, currency), {}:
                self.currency = self._validate_currency(currency)
                self.amount = self._validate_amount(amount)

            # Case: Named amount and currency
            case (), {"amount": amount, "currency": currency}:
                self.currency = self._validate_currency(currency)
                self.amount = self._validate_amount(amount)
                kwargs.pop("amount", None)
                kwargs.pop("currency", None)

            # Case: Named amount only, with default currency
            case (), {"amount": amount}:
                self.currency = self._get_default_currency()
                self.amount = self._validate_amount(amount)
                kwargs.pop("amount", None)

            # Case: Named currency only, with default amount
            case (amount,), {"currency": currency}:
                self.currency = self._validate_currency(currency)
                self.amount = self._validate_amount(amount)
                kwargs.pop("currency", None)

            # Case: Single string positional argument (e.g., "100 USD")
            case (money_string, ), {} if isinstance(money_string, str):
                parsed_amount, parsed_currency = _mp.MoneyParser().parse(money_string)
                self.currency = Currency(parsed_currency) if parsed_currency else self._get_default_currency()
                self.amount = self._validate_amount(parsed_amount)

            # Case: Positional amount only, with default currency
            case (amount, ), {}:
                self.currency = self._get_default_currency()
                self.amount = self._validate_amount(amount)

            # Error: Too many positional arguments
            case _ if len(args) > 2:
                raise TypeError("Too many positional arguments provided to Money().")

            # Error: Invalid or redundant arguments
            case _:
                raise TypeError(f"Invalid arguments: args={args}, kwargs={kwargs}")

        # Ensure no unexpected keyword arguments are left
        if kwargs:
            raise TypeError(f"Unexpected keyword arguments: {', '.join(kwargs.keys())}")

    @staticmethod
    def _validate_currency(currency: str | Currency):
        """Validate and return a Currency instance."""
        if isinstance(currency, Currency):
            return currency
        elif isinstance(currency, str):
            return Currency(currency)
        else:
            raise TypeError("'currency' must be a Currency instance or a valid currency code string")

    def _validate_amount(self, amount: Decimal | int | float | str) -> Decimal:
        """Ensure that amount is a valid Decimal and formatted with right number of decimal points"""
        if isinstance(amount, Decimal):
            pass
        elif isinstance(amount, (int, float, str)):
            try:
                amount = Decimal(str(amount))
            except (decimal.InvalidOperation, ValueError, TypeError):
                raise ValueError(f"Invalid amount: {amount}")
        else:
            raise TypeError("'amount' must be a Decimal, int, float, or str representing a valid numeric value.")

        return self._quantize_amount(amount)

    def _get_currency_subunit(self) -> int:
        return self.currency.sub_unit if self.currency.sub_unit is not None else Currency.default_sub_unit

    def _quantize_amount(self, amount: Decimal) -> Decimal:
        """Quantize (ensure number of decimal digits) the amount respecting currency subunits and rounding rules"""
        return amount.quantize(
            Decimal("0." + "0" * self._get_currency_subunit()),
            rounding=Money.get_rounding()
        )

    @staticmethod
    def _get_default_currency():
        # TODO: Enable contexts
        return Currency('XXX')

    def __str__(self):
        return f"{self.amount:.{self._get_currency_subunit()}f} {self.currency}"

    def __repr__(self):
        return f"Money(amount={self.amount:.{self._get_currency_subunit()}f}, currency='{self.currency}')"

    def __hash__(self) -> int:
        """
        Make a Money instance hashable to allow Money objects to be used as keys in dictionaries,
        stored in sets, or compared for equality using hashing mechanisms.
        """
        return hash((self.amount, self.currency))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Money):
            return self.amount == other.amount and self.currency is other.currency
        # Allow Money(0, USD) == 0 => True
        if other == 0:
            return self.amount == 0
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        return not result

    def __pos__(self: M) -> M:
        """Enable support for unary positive syntax with ( + )  operator, symmetry for __neg__"""
        return self.__class__(amount=self.amount, currency=self.currency,)

    def __neg__(self: M) -> M:
        """Enable support for unary negative syntax with ( - ) operator"""
        return self.__class__(amount=-self.amount, currency=self.currency,)

    def __add__(self: M, other: object) -> M:
        """Enable additions of Money objects with the same Currency, and additions with 0"""
        # Allow expressions like sum() to work with Money instances
        if other == 0:
            return self
        # Signal a not supported operation
        if not isinstance(other, Money):
            return NotImplemented
        # Currencies must be same
        if self.currency is other.currency:
            return self.__class__(amount=self.amount + other.amount, currency=self.currency)
        raise TypeError(self._ERR_MSG_ADD_SUB)

    __radd__ = __add__

    def __sub__(self: M, other: object) -> M:
        """Enable subtraction of Money objects with the same Currency, and subtraction of 0"""
        if other == 0:
            return self
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency is other.currency:
            return self.__class__(amount=self.amount - other.amount, currency=self.currency)
        raise TypeError(self._ERR_MSG_ADD_SUB)

    def __rsub__(self: M, other: object) -> M:
        """Enable negation through subtraction from zero: 0 - Money => -Money"""
        if other == 0:
            return -self
        return NotImplemented

    def __mul__(self: M, other: object) -> M:

        if isinstance(other, _NUMERIC_TYPES):
            return self.__class__(
                amount=self._quantize_amount(self.amount * Decimal(other)),
                currency=self.currency,
            )
        raise TypeError(self._ERR_MSG_MULT.format(op="*", type=type(other).__name__))

    def __rmul__(self: M, other: object) -> M:
        return self.__mul__(other)

    def __truediv__(self: M, other: object) -> M:
        if isinstance(other, _NUMERIC_TYPES):
            if other == 0:
                raise ZeroDivisionError
            return self.__class__(
                amount=self._quantize_amount(self.amount / Decimal(other)),
                currency=self.currency,
            )
        raise TypeError(self._ERR_MSG_MULT.format(op="/", type=type(other).__name__))

    def divide_with_adjustment(self: M, other: object) -> tuple[M, M]:
        """
        Divide (/) with adjustment keeps track of remainder amount lost due to quantization.
        Useful for high precision transactions where it is important to keep track of remainder amounts, e.g.,
        for accounting purposes.
        Example (assuming default ROUND_DOWN behaviour):
            result, adjustment = Money("20 USD").divide_with_adjustment(7)
            print(result, adjustment) >>> 2.85 USD, 0.05 USD
            Explanation: 2.85 * 7 => 19.95, 20.00 - 19.95 = 0.05
        Note: Use modulo (%) for
        """
        if isinstance(other, _NUMERIC_TYPES):
            if other == 0:
                raise ZeroDivisionError
            div_result = self.__class__(
                amount=self._quantize_amount(self.amount / Decimal(other)),
                currency=self.currency,
            )
            div_adj = self - div_result * other
            return div_result, div_adj
        raise TypeError(self._ERR_MSG_MULT.format(op="/", type=type(other).__name__))

    def __rtruediv__(self: M, other: object) -> M:
        raise TypeError(self._ERR_MSG_DIV)

    def __floordiv__(self: M, other: object) -> M:
        if isinstance(other, _NUMERIC_TYPES):
            if other == 0:
                raise ZeroDivisionError

            # Perform floor division
            result_amount = self.amount // Decimal(other)

            # Return a new Money object
            return self.__class__(amount=self._quantize_amount(result_amount), currency=self.currency)

        raise TypeError(self._ERR_MSG_MULT.format(op="//", type=type(other).__name__))

    def __rfloordiv__(self: M, other: object) -> M:
        raise TypeError(self._ERR_MSG_DIV)

    def __mod__(self: M, other: object) -> M:
        if isinstance(other, _NUMERIC_TYPES):
            if other == 0:
                raise ZeroDivisionError

            # Perform modulo operation
            remainder = self.amount % Decimal(other)

            # Quantize the result
            quantized_remainder = self._quantize_amount(remainder)

            return self.__class__(amount=quantized_remainder, currency=self.currency)

        raise TypeError(self._ERR_MSG_MULT.format(op="%", type=type(other).__name__))

    def __rmod__(self: M, other: object) -> M:
        raise TypeError(self._ERR_MSG_DIV)

    def __pow__(self: M, exponent: object) -> M:
        raise TypeError(self._ERR_MSG_EXPN)

    def __rpow__(self: M, base: object) -> M:
        raise TypeError(self._ERR_MSG_EXPN)

    def __abs__(self: M) -> M:
        return self.__class__(amount=abs(self.amount), currency=self.currency)

    def __round__(self: M, number_of_decimal_digits: int) -> M:
        """
        Round the Money object to the specified number of decimal places,
        respecting the predefined currency subunit and the rounding rules of the class.
        """
        # If the requested precision exceeds the subunit, return the Money object as is
        if number_of_decimal_digits >= self._get_currency_subunit():
            return self

        # Calculate the target precision as a Decimal (e.g., "0.1" for 1 decimal place)
        target_precision = Decimal("1").scaleb(-number_of_decimal_digits)

        # Apply quantization with the current rounding rule
        amount = self.amount.quantize(target_precision, rounding=self.get_rounding())

        # Return a new Money object with the rounded amount
        return self.__class__(amount=amount, currency=self.currency)
