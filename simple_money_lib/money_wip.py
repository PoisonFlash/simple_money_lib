from typing import overload, TypeVar
from decimal import Decimal
import decimal
import numbers

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

    # Class variables
    rounding = decimal.ROUND_DOWN  # Specifies rounding logic for decimals conversion as per 'decimal' module

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

        # Note: always initialize self.currency first, as amount initialization requires self.currency to be set

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
            rounding=Money.rounding
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
        Divide with adjustment keeps track of remainder amount lost due to quantization.
        Example:
            amount = Money("20 USD")
            result = amount / 7
            adjustment = amount - result * 7
            print(amount, result, adjustment)
            >>> 20 USD, 19.95 USD, 0.05 USD
            In this case, adjustment is 0.05 USD
        """
        # TODO Implement

    def __rtruediv__(self: M, other: object) -> M:
        raise TypeError("Cannot divide by a Money instance.")



a = Money(10, "USD")
b = Money("20 USD")

f = b / 7
print(f, f * 7)