import pandas as pd
import json
from pathlib import Path

def _read_wiki_table(url: str, table_index: int) -> pd.DataFrame:
    df = pd.read_html(url)
    df = df[table_index]
    return df

def _clean_df(df: pd.DataFrame, to_replace: str, replace_with: str = '') -> pd.DataFrame:
    # Clean all columns headers
    df.columns = df.columns.str.replace(to_replace, replace_with, regex=True)
    # Clean all string cells
    df = df.apply(lambda col: col.str.replace(to_replace, replace_with, regex=True) if col.dtype == 'object' else col)
    return df

def download_currencies() -> None:
    """Downloads currency codes data from Wikipedia and saves to the current working directory"""
    currency_url = 'https://en.wikipedia.org/wiki/ISO_4217'  # ISO currency codes
    # Load currencies from Wikipedia, clean, and save to CSV
    csv_file = 'iso_currency_codes.csv'
    _read_wiki_table(currency_url, 1) \
        .pipe(_clean_df, r'\[.*?\]') \
        .to_csv(csv_file, index=False)
    print(f"ISO currency codes table saved to '{csv_file}'")

def download_countries() -> None:
    """Downloads country codes data from Wikipedia and saves to the current working directory"""
    country_url = 'https://en.wikipedia.org/wiki/ISO_3166-1'  # ISO country codes
    # Load countries from Wikipedia, clean, and save to CSV
    csv_file = 'iso_country_codes.csv'
    _read_wiki_table(country_url, 1) \
        .pipe(_clean_df, r'\[.*?\]') \
        .to_csv(csv_file, index=False)
    print(f"ISO countries codes table saved to '{csv_file}'")

def generate_predefined_currencies_json(destination_json_file: Path) -> None:
    """Generate a JSON file with predefined currencies based on pre-created CSV."""
    csv_file = 'iso_currency_codes.csv'
    # json_file = 'predefined_currencies.json'

    df = pd.read_csv(csv_file, usecols=[0, 1, 2, 3])
    # Replace "." in 'D' with None and ensure it stays as int | None
    df['D'] = df['D'].replace('.', None).astype('Int64')  # Keeps as integer nullable (Int64 supports None)
    # Ensure 'Num' column is integer or None
    df['Num'] = df['Num'].astype('Int64')  # Convert to integer nullable (Int64 supports None)

    # Convert the DataFrame to a dictionary with the desired structure
    currencies_dict = {}
    for _, row in df.iterrows():
        code = row['Code']
        numeric = row['Num'] if row['Num'] is not pd.NA else None  # Replace <NA> with None
        sub_unit = row['D'] if row['D'] is not pd.NA else None  # Replace <NA> with None
        name = row['Currency']
        currencies_dict[code] = {
            "numeric": numeric,
            "sub_unit": sub_unit,
            "name": name
        }

    # Write the dictionary to a JSON file
    with open(destination_json_file, 'w', encoding='utf-8') as f:
        json.dump(currencies_dict, f, ensure_ascii=False, indent=4)

    print(f"Predefined currencies JSON saved to '{destination_json_file.name}'")

def update_iso_currencies(destination_json_file: Path) -> None:
    print("Updating ISO currencies from Wikipedia...")
    download_currencies()
    generate_predefined_currencies_json(destination_json_file)
    print("Update completed")
