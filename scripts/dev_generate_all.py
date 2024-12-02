from pathlib import Path
import datetime
import json

TEMPLATE_ALL = """# Auto-generated module
# CHECKLINE {when}

# Includes all ISO currencies, source: https://en.wikipedia.org/wiki/ISO_4217

from simple_money_lib.currency import Currency as _Currency

# Export individual currencies
{currency_exports}

__all__ = [
    {currency_list}
    ]
"""

def generate_currency_all(output_file: Path, source_json: Path) -> None:
    """
    Generate file with all ISO currencies based on source JSON.
    Params:
    output_file     destination file
    source_json     source file
    """
    print("Generating file with all ISO currencies...")

    with open(source_json, "r") as f:
        metadata = json.load(f)

    currency_exports = "\n".join([f'{code} = _Currency("{code}")' for code in metadata.keys()])

    currency_codes = sorted(metadata.keys())
    codes_per_line = 16
    chunks = [currency_codes[i:i + codes_per_line] for i in range(0, len(currency_codes), codes_per_line)]
    currency_list = ",\n    ".join([", ".join(f'"{code}"' for code in chunk) for chunk in chunks])

    module_content = TEMPLATE_ALL.format(
        currency_exports=currency_exports,
        currency_list=currency_list,
        when=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    # Ensure the output directory exists
    output_dir = output_file.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write the generated module
    with open(output_file, "w") as f:
        f.write(module_content)

    print(f"Successfully generated: '{output_file}'")
