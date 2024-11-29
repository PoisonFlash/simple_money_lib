from simple_money_lib.currency import Currency
from simple_money_lib.errors import CurrencyNotFoundError

class CurrencyCollection:
    def __init__(self, *currencies, name=None, description=None):
        """
        Initialize a CurrencyCollection with a set of currencies.

        :param currencies: A mix of Currency objects and valid string codes.
        :param name: Optional name for the collection (e.g., "Major Currencies").
        :param description: Optional description for the collection.
        :raises CurrencyCodeInvalid: If an invalid currency code is used during initialization.
        """
        self.name = name
        self.description = description
        self._currencies = {}
        for currency in currencies:
            if isinstance(currency, Currency):
                self._currencies[currency.code] = currency
            elif isinstance(currency, str):
                try:
                    self._currencies[currency.upper()] = Currency(currency.upper())
                except CurrencyNotFoundError:
                    continue  # Skip invalid currencies
            else:
                raise ValueError(f"Invalid currency: {currency}")

    def __contains__(self, item):
        """
        Check if a currency is in the collection.

        :param item: A Currency object or a valid string code.
        :return: True if the currency is in the collection, False otherwise.
        """
        if isinstance(item, Currency):
            return item.code in self._currencies
        elif isinstance(item, str):
            try:
                return item.upper() in self._currencies
            except CurrencyNotFoundError:
                return False
        else:
            return False

    def __iter__(self):
        """
        Iterate over the Currency objects in the collection.

        :return: An iterator over Currency objects.
        """
        return iter(self._currencies.values())

    def __repr__(self):
        """
        Return a string representation of the CurrencyCollection.

        :return: A string showing the codes of all currencies in the collection.
        """
        return f"CurrencyCollection({', '.join(self._currencies.keys())})"


