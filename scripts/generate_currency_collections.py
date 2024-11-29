import json
from pathlib import Path
import datetime

# Path to the metadata file and the output directory
METADATA_FILE = Path("collections_metadata.json")
OUTPUT_DIR = Path("../simple_money_lib/currencies")

TEMPLATE = """# Auto-generated module
# CHECKLINE {when}
from simple_money_lib.currency import Currency as _Currency
from simple_money_lib.currencies.currency_collections import CurrencyCollection as _CurrencyCollection

# Export individual currencies
{currency_exports}

{name}_currencies = _CurrencyCollection(
    {currencies},
    name="{name}",
    description="{description}"
)

__all__ = [{currency_list}, "{name}_currencies"]
"""

def load_metadata():
    """Load the collections metadata from the JSON file."""
    with open(METADATA_FILE, "r") as f:
        return json.load(f)

def generate_module(name, metadata):
    """Generate a Python module for a currency collection."""
    currencies = ", ".join([f'{code}' for code in metadata["currencies"]])
    currency_exports = "\n".join([f'{code} = _Currency("{code}")' for code in metadata["currencies"]])
    currency_list = ", ".join([f'"{code}"' for code in metadata["currencies"]])

    module_content = TEMPLATE.format(
        name=name,
        currencies=currencies,
        description=metadata["description"],
        currency_exports=currency_exports,
        currency_list=currency_list,
        when=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    # Ensure the output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Write the generated module to the output directory
    file_path = OUTPUT_DIR / f"{name}.py"
    with open(file_path, "w") as f:
        f.write(module_content)

def main():
    """Main script function."""
    metadata = load_metadata()
    for name, data in metadata.items():
        generate_module(name, data)
    print("Currency collections generated")

if __name__ == "__main__":
    main()
