from pathlib import Path
import argparse

from dev_update_from_wiki import update_iso_currencies
from dev_generate_all import generate_currency_all
from dev_generate_currency_collections import generate_collections


# Get the root directory of the project
project_root = Path(__file__).resolve().parent.parent

# Paths to the target subfolders in the library
data_folder = project_root / "simple_money_lib" / "data"
currency_folder = project_root / "simple_money_lib" / "currencies"

# Names of files
iso_currencies_file = 'predefined_currencies.json'
all_file = 'all.py'
collections_file = 'collections_metadata.json'

def _ensure_directories_exist():
    # Ensure the directories exist
    data_folder.mkdir(parents=True, exist_ok=True)
    currency_folder.mkdir(parents=True, exist_ok=True)

def main(wiki_update=False):
    _ensure_directories_exist()

    iso_path = data_folder / iso_currencies_file
    all_path = currency_folder / all_file

    if wiki_update:
        update_iso_currencies(iso_path)

    generate_currency_all(output_file=all_path, source_json=iso_path)

    collections_path = data_folder / collections_file
    generate_collections(collections_path, currency_folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Manage currency data for the simple_money_lib project."
    )
    parser.add_argument(
        'action',
        nargs='?',
        choices=['update', 'u', 'build', 'b'],
        help="Specify 'update' or 'u' to update ISO currencies from Wikipedia."
    )

    args = parser.parse_args()

    if args.action in ['update', 'u']:
        main(wiki_update=True)
    elif args.action in ['build', 'b']:
        main(wiki_update=False)
    else:
        print("Usage: dev_main.py [update|u|build|b]")
