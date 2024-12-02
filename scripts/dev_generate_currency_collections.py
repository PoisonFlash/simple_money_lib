import json
from pathlib import Path
import datetime


_TEMPLATE = """# Auto-generated module
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

def _load_metadata(metadata_file):
    """Load the collections metadata from the JSON file."""
    with open(metadata_file, "r") as f:
        return json.load(f)

def _generate_module(name, metadata, output_folder: Path):
    """Generate a Python module for a currency collection."""
    currencies = ", ".join([f'{code}' for code in metadata["currencies"]])
    currency_exports = "\n".join([f'{code} = _Currency("{code}")' for code in metadata["currencies"]])
    currency_list = ", ".join([f'"{code}"' for code in metadata["currencies"]])

    module_content = _TEMPLATE.format(
        name=name,
        currencies=currencies,
        description=metadata["description"],
        currency_exports=currency_exports,
        currency_list=currency_list,
        when=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    # Ensure the output directory exists
    output_folder.mkdir(parents=True, exist_ok=True)

    # Write the generated module to the output directory
    file_path = output_folder / f"{name}.py"
    with open(file_path, "w") as f:
        f.write(module_content)

    print(f"\tCollection generated: {file_path}")

def generate_collections(collections_json_file_path: Path, output_folder: Path) -> None:
    print("Generating collections...")
    metadata = _load_metadata(collections_json_file_path)
    for name, data in metadata.items():
        _generate_module(name, data, output_folder)
    print("All currency collections successfully generated")

