from moneyed import *
from moneyed import Money as _BaseMoney

import simple_money_lib.money_parser as _mp


class Money(_BaseMoney):
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], str):
            # Handle the case where a single string is passed
            amount, currency = _mp.MoneyParser().parse(args[0])
            # Call the original Money constructor with parsed values
            super().__init__(amount=amount, currency=currency)
        else:
            # If not a single string, fall back to the original Money constructor
            super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        # Simplified overwriting
        return f"{self.amount:.2f} {self.currency}"
