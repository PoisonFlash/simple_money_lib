from abc import ABC, abstractmethod
from decimal import Decimal

class MoneyParser(ABC):
    @abstractmethod
    def parse(self, money_string: str) -> tuple[Decimal, str | None]:
        """Parse a money string into an amount and currency."""
        pass
