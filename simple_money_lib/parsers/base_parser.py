import decimal
import re

from simple_money_lib import Currency


class BaseParser:
    """
    Base class for money parser. In addition to being the base, it also provides the baseline functionality.
    It is capable of converting a simpler string to a tuple of a decimal and a valid currency code
    """
    def parse(self, money_string: str) -> tuple[decimal.Decimal, str | None]:
        """
        This parser implements parsing of simple strings representing Money, without complex formatting.
        For example: "21.34 USD", "EUR 567.89", or "CNY1.23". "123.45" without currency is also ok.
        It will fail on more complex strings where numbers would not follow Python's format.
        Arguments:
            money_string: a string representing amount and (optionally) currency: "EUR 567.89"
        Returns:
            tuple of a decimal and a string representing a valid currency code: (Decimal("567.89", "EUR")
        Raises:
            ValueError
        """
        money_string = money_string.strip()

        if code := self.match_currency(money_string):
            # Case-insensitive replace
            amount_str = re.sub(re.escape(code), "", money_string, count=1, flags=re.IGNORECASE).strip()
        else:
            amount_str = money_string

        # Check for invalid patterns
        if not re.match(r"^-?\d+(\.\d+)?$", amount_str):
            raise ValueError(f"Invalid monetary amount: '{amount_str}'")

        try:
            amount_decimal = decimal.Decimal(amount_str)
        except decimal.InvalidOperation:
            raise ValueError(f"Unable to convert amount: {money_string}")
        return amount_decimal, code

    @staticmethod
    def match_currency(money_string: str) -> str | None:
        money_string = money_string.upper()
        known_currencies = sorted(Currency.all_currencies().keys(), key=len, reverse=True)
        # Iterate to find the longest match
        for code in known_currencies:
            if code[-1].isdigit():  # Currency ends with a digit
                # Check if it starts with the code + space, or ends with the code
                if money_string.startswith(f"{code} ") or money_string.endswith(code):
                    return code
            else:  # Standard matching
                if money_string.startswith(code) or money_string.endswith(code):
                    return code
        return None


class SimpleParserWithSubstitutions(BaseParser):
    def __init__(self, substitutions: dict = None):
        """
        A parser that extends SimpleMoneyParser by allowing value substitutions in the input string.

        Args:
            substitutions (dict): A dictionary of old_value : new_value pairs.
                For example, {"$": "USD", ",": "."} will replace all occurrences of '$' with 'USD'
                and all commas with dots. If no substitutions are provided, the parser behaves like SimpleMoneyParser.

        Comparison example:
            parser = SimpleMoneyParser()
            money_str = "1,250.50€"
            try:
                result = parser.parse("1,250.50€")
            except ValueError as e:
                print(f"This gives a ValueError: {e}")
            # Replace euro symbol with valid code and removing comma as thousands separator
            substitutions = {"€": "EUR", ",": ""}
            parser = SimpleParserWithSubstitutions(substitutions)
            result = parser.parse(money_str)
            print(result)  # (Decimal('1250.50'), 'EUR')
        """
        self.substitutions = substitutions
        super().__init__()  # Ensure the parent class is initialized

    def parse(self, money_string: str) -> tuple[decimal.Decimal, str | None]:
        if self.substitutions:
            for old_value, new_value in self.substitutions.items():
                # Add a trailing space if the new value ends with a digit
                if new_value and new_value[-1].isdigit():
                    new_value = new_value + " "
                money_string = money_string.replace(old_value, new_value)
        # Delegate parsing to the parent class
        return super().parse(money_string)
