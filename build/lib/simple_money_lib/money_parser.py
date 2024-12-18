import re
from typing import Tuple
from decimal import Decimal

from _inactive.currency_context import CurrencyContext


class MoneyParser:
    thousand_separators = [".", ",", "'", " ", "\xa0", "\u202F", "\u066C", "\uFF0C"]
    decimal_separators = [".", ",", "\u066B", "\uFF0E"]
    currency_symbols = ["$", "€", "£", "¥", "₹"]

    # Build regex patterns
    thousand_separators_re = ''.join(re.escape(sep) for sep in thousand_separators)
    decimal_separators_re = ''.join(re.escape(sep) for sep in decimal_separators)
    currency_symbols_re = ''.join(re.escape(sep) for sep in currency_symbols)
    currency_codes_re = r"[A-Za-z]{1,3}"

    @classmethod
    def _split_currency_and_value(cls, value_string: str) -> tuple:
        value_string = value_string.strip()

        # Build the currency symbols regex from the higher-level declarations
        currencies_re = rf"({cls.currency_symbols_re}|{cls.currency_codes_re})"
        # Initialize variables to hold the parts
        currency_start = ''
        currency_end = ''

        # If the string contains only currency symbols or codes
        if re.fullmatch(currencies_re, value_string):
            return value_string, None

        # Find the first position of a digit or whitespace to determine where currency ends
        for i, char in enumerate(value_string):
            if char in cls.decimal_separators:
                currency_start = value_string[:i].strip()
                value_string = "0" + value_string[i:].strip()  # ".5" -> "0.5"
                break
            if char.isdigit() or char.isspace():
                currency_start = value_string[:i].strip()
                value_string = value_string[i:].strip()
                break

        # Now reverse the string to find if there's currency at the end
        for i, char in enumerate(reversed(value_string)):
            if char.isdigit() or char.isspace() or char in cls.decimal_separators:
                currency_end = value_string[len(value_string) - i:].strip()
                value_string = value_string[:len(value_string) - i].strip()
                break

        # If both start and end have currency, prioritize the start section
        if currency_start:
            currency_part = currency_start
        elif currency_end:
            currency_part = currency_end
        else:
            currency_part = None

        # The remaining part is the value (cleaned up)
        value_part = value_string

        return currency_part, value_part

    def parse(self, value_string: str) -> Tuple[Decimal, str]:
        """Convert string like '50.00 kr' or '$100' to tuple of Decimal value and Currency"""
        error_invalid_value = f"Invalid value: '{value_string}'"

        if not value_string:
            raise ValueError(error_invalid_value)

        # Split currency and value
        currency_part, value_part = self._split_currency_and_value(value_string)

        # Value must be present
        if not value_part:
            raise ValueError(error_invalid_value)

        # Convert to Currency object
        if currency_part:
            currency = CurrencyContext.get_currency(currency_part)
        else:
            currency = CurrencyContext.get_default_currency()

        # Modify the pattern to capture the decimal separator and decimal part, which is 1 or 2 digits
        pattern = rf"^(.*?)([{self.decimal_separators_re}])(\d{{1,2}})$"

        if match := re.match(pattern, value_part):
            value_part, decimal_separator_used, decimal_part = match.group(1), match.group(2), match.group(3)
        else:
            decimal_part = '00'  # No decimal part found
            decimal_separator_used = None

        # Ensure 2-digits decimal part
        if len(decimal_part) == 1:
            decimal_part = f"{decimal_part}0"

        # Ensure the decimal separator doesn't appear in the value part before the decimal
        if decimal_separator_used and decimal_separator_used in value_part:
            raise ValueError(error_invalid_value)

        # Verify validity of the main value if it is not already decimal
        if not value_part.isdecimal():
            for separator in self.thousand_separators:
                parts = value_part.split(separator)
                # First part can be 1-3 digits, rest must be exactly 3 digits
                if len(parts[0]) in {1, 2, 3} and all(len(part) == 3 for part in parts[1:]):
                    # If valid, clean the value by removing the separator
                    value_part = int(''.join(parts))
                    break
            else:
                # If no valid thousand separator is found or the format is incorrect, raise an error
                raise ValueError(error_invalid_value)

        value = Decimal(f"{value_part}.{decimal_part}")

        return value, str(currency.code)


if __name__ == '__main__':
    test_values = ["kr000", "000kr", "kr 000", "000 kr", "$1,250.50", "1,250.50$", "€ 1 250,50",
                   "$.5", "$50.51",
                   "USD 1000", "1000 USD", "000",
                   "50.55 kr", "50,55 kr",
                   "350.55 kr", "6,55 kr",
                   "1 250,55 kr", "1,250.55 kr",
                   "kr 1 250,50", "kr 1,250.50", "1.250,50",
                   "1,250.50", "kr 1 250,50",
                   "1250.50", "1250,50",
                   "0", "0.0", "0,0", "0.01", "0,01", "7,01",
                   ".55", "0.5", ",51", "0,5", ".5", ",5",
                   "kr.55", "kr,55",
                   "$.", "$", "0 0",
                   "", " ", ".", ",",
                   "kr.", "kr,", ".kr", ",krn",
                   "abc123", "@@@500", "1.2.3", "1.250.50 kr", None,
                   "1 000,111.33kr", "10000d0"]

    from context_templates import DefaultCurrencyContext

    DefaultCurrencyContext.activate()
    # DanishCurrencyContext.activate()
    mp = MoneyParser()
    for item in test_values:
        try:
            amount, currency = mp.parse(item)
            pres = f"{amount} {currency}"
            print(f"Test value: {str(item):>14}  result: {pres:>12}")
        except ValueError as e:
            print(f"ValueError on '{item}'")
