from locale import currency
from typing import Optional, overload
from decimal import Decimal, InvalidOperation, ROUND_DOWN

import simple_money_lib.money_parser as _mp
from simple_money_lib.currency import Currency

class Money:

    # Class variables
    rounding = ROUND_DOWN  # Specifies rounding logic for decimals conversion as per 'decimal' module

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
            except (InvalidOperation, ValueError, TypeError):
                raise ValueError(f"Invalid amount: {amount}")
        else:
            raise TypeError("Amount must be a Decimal, int, float, or str representing a numeric value.")

        quantized_amount = amount.quantize(
            Decimal("0." + "0" * self._get_currency_subunit()),
            rounding=Money.rounding
        )
        return quantized_amount

    def _get_currency_subunit(self):
        return self.currency.sub_unit if self.currency.sub_unit is not None else Currency.default_sub_unit

    @staticmethod
    def _get_default_currency():
        # TODO: Enable contexts
        return Currency('XXX')

    def __str__(self):
        return f"{self.amount:.{self._get_currency_subunit()}f} {self.currency}"

    def __repr__(self):
        return f"Money(amount={self.amount:.{self._get_currency_subunit()}f}, currency='{self.currency}')"
