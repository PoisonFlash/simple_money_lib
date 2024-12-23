from typing import overload, TypeVar
from decimal import Decimal
import decimal

# Ensure correct type hints for earlier versions of Python (before 3.11)
# Consider switching to Self (from typing import Self) in October 2026
M = TypeVar("M", bound="Money")

from simple_money_lib.currency import Currency
from simple_money_lib.parsers import ParserManager as _ParserManager
from simple_money_lib.utils.rounding import RoundingManager as _RoundingManager
from simple_money_lib.utils.default_currency import DefaultCurrency as _DefaultCurrency

# Constants
_NUMERIC_TYPES = (int, float, Decimal)  # Permitted numeric types for operations

class Money:

    # Class constants
    _ERR_MSG_ADD_SUB = "Cannot add or subtract Money objects with different currencies"
    _ERR_MSG_MULT = "Unsupported operand type(s) for {op}: 'Money' and '{type}'"
    _ERR_MSG_DIV = "Cannot divide by a Money instance."
    _ERR_MSG_EXPN = "Exponentiation is not supported for Money objects."
    _ERR_MSG_COMP = "Cannot compare Money objects with different currencies."

    # Class variables for additional functionality
    rounding = _RoundingManager()
    parser = _ParserManager()
    default_currency = _DefaultCurrency()

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
                self.currency = self.default_currency.get()
                self.amount = self._validate_amount(amount)
                kwargs.pop("amount", None)

            # Case: Named currency only, with default amount
            case (amount,), {"currency": currency}:
                self.currency = self._validate_currency(currency)
                self.amount = self._validate_amount(amount)
                kwargs.pop("currency", None)

            # Case: Single string positional argument (e.g., "100 USD")
            case (money_string, ), {} if isinstance(money_string, str):
                parser = self.parser.get()
                parsed_amount, parsed_currency = parser.parse(money_string)
                self.currency = Currency(parsed_currency) if parsed_currency else self.default_currency.get()
                self.amount = self._validate_amount(parsed_amount)

            # Case: Positional amount only, with default currency
            case (amount, ), {}:
                self.currency = self.default_currency.get()
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
        """Ensure amount is a valid Decimal and format it based on currency subunits."""
        try:
            # Convert all acceptable types to Decimal directly
            if not isinstance(amount, Decimal):
                amount = Decimal(str(amount))
        except (decimal.InvalidOperation, ValueError, TypeError):
            raise ValueError("'amount' must be a Decimal, int, float, or str representing a valid numeric value.")

        return self._quantize_amount(amount)

    def _get_currency_subunit(self) -> int:
        return self.currency.sub_unit if self.currency.sub_unit is not None else Currency.default_sub_unit

    def _quantize_amount(self, amount: Decimal) -> Decimal:
        """Quantize (ensure number of decimal digits) the amount respecting currency subunits and rounding rules"""
        return amount.quantize(
            Decimal("0." + "0" * self._get_currency_subunit()),
            rounding=Money.rounding.get()
        )

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
        # return NotImplemented
        raise TypeError(self._ERR_MSG_ADD_SUB)

    def __radd__(self: M, other: object) -> M:
        """Enable right-hand addition with Money objects"""
        return self.__add__(other)

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
        # return NotImplemented
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
        return NotImplemented

    def __rpow__(self: M, base: object) -> M:
         return NotImplemented

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
        amount = self.amount.quantize(target_precision, rounding=Money.rounding.get())

        # Return a new Money object with the rounded amount
        return self.__class__(amount=amount, currency=self.currency)

    def __lt__(self: M, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise TypeError(self._ERR_MSG_COMP)
        return self.amount < other.amount

    def __le__(self: M, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise TypeError(self._ERR_MSG_COMP)
        return self.amount <= other.amount

    def __gt__(self: M, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise TypeError(self._ERR_MSG_COMP)
        return self.amount > other.amount

    def __ge__(self: M, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise TypeError(self._ERR_MSG_COMP)
        return self.amount >= other.amount

    def __iter__(self):
        """
        Unpack the Money object as a tuple: (amount, currency).
        Example:
            money = Money("100 USD")
            amount, currency = money
            print(amount)              # 100.00
            print(*money)              # 100.00 USD
        """
        return iter((self.amount, self.currency))

    def amount_and_currency_code(self):
        """
        Return the monetary value and the currency code as a tuple.

        This method is useful for integrations with libraries or functions that
        require the amount and currency code in a structured format, such as Babel's
        `format_currency`.

        Note:
            Codes from custom currencies might not be directly recognizable by
            external libraries or systems.

        Returns:
            tuple: A tuple containing the amount (Decimal) and the currency code (str).
        """
        return self.amount, self.currency.code

    def as_dict(self):
        """
        Return a dictionary representation of the Money object.
        """
        return {'amount': self.amount, 'currency': self.currency}

    def __getitem__(self, key):
        """
        Enable dictionary-style access for unpacking.
        Example:
            money = Money("100 USD")
            print(money['currency'])    # USD
        """
        return self.as_dict()[key]

    @staticmethod
    def keys():
        """
        Return a list of keys representing the components of the Money object.
        Keys: ['amount', 'currency']
        """
        return ['amount', 'currency']

    def items(self):
        """
        Return an iterator of (key, value) pairs: ('amount', amount), ('currency', currency).
        """
        return iter([('amount', self.amount), ('currency', self.currency)])

    def __contains__(self, key):
        """
        Check if a key is a valid component of the Money object.
        print 'amount' in Money(100, 'EUR')  # True
        """
        return key in self.keys()
