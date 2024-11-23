import pandas as pd
import json

def read_wiki_table(url: str, table_index: int) -> pd.DataFrame:
    df = pd.read_html(url)
    df = df[table_index]
    return df

def clean_df(df: pd.DataFrame, to_replace: str, replace_with: str = '') -> pd.DataFrame:
    # Clean all columns headers
    df.columns = df.columns.str.replace(to_replace, replace_with, regex=True)
    # Clean all string cells
    df = df.apply(lambda col: col.str.replace(to_replace, replace_with, regex=True) if col.dtype == 'object' else col)
    return df

def download_currencies() -> None:
    currency_url = 'https://en.wikipedia.org/wiki/ISO_4217'  # ISO currency codes
    # Load currencies from Wikipedia, clean, and save to CSV
    csv_file = 'iso_currency_codes.csv'
    read_wiki_table(currency_url, 1) \
        .pipe(clean_df, r'\[.*?\]') \
        .to_csv(csv_file, index=False)
    print(f"ISO currency codes table saved to '{csv_file}'")

def download_countries() -> None:
    country_url = 'https://en.wikipedia.org/wiki/ISO_3166-1'  # ISO country codes
    # Load countries from Wikipedia, clean, and save to CSV
    csv_file = 'iso_country_codes.csv'
    read_wiki_table(country_url, 1) \
        .pipe(clean_df, r'\[.*?\]') \
        .to_csv(csv_file, index=False)
    print(f"ISO countries codes table saved to '{csv_file}'")


def generate_currency_all() -> None:
    """Generate file with all currencies based on pre-created CSV"""
    filename = "gen_all.py"

    imports = [
        "from simple_money_lib.currency import Currency",
        ""
    ]

    csv_file = 'iso_currency_codes.csv'
    df = pd.read_csv(csv_file, usecols=[0, 1, 2, 3])
    # Replace "." in 'D' with None and ensure it stays as int | None
    df['D'] = df['D'].replace('.', None).astype('Int64')  # Keeps as integer nullable (Int64 supports None)
    # Ensure 'Num' column is integer or None
    df['Num'] = df['Num'].astype('Int64')  # Convert to integer nullable (Int64 supports None)

    # Add currencies codes to __all__ for wildcard imports
    alls = []
    # Generate the Currency instances as strings
    currency_strings = []
    for _, row in df.iterrows():
        code = row['Code']
        numeric = row['Num'] if row['Num'] is not pd.NA else None  # Replace <NA> with None
        sub_unit = row['D'] if row['D'] is not pd.NA else None  # Replace <NA> with None
        name = row['Currency']
        currency_str = f"{code} = Currency('{code}', {numeric}, {sub_unit}, '{name}')"
        currency_strings.append(currency_str)
        alls.append(' '*10 + '"' + code + '"')

    lb = '\n'
    alls = f"{lb}__all__ = [{lb}" + f",{lb}".join(alls) + lb + " " * 10 + "]" + lb
    with open(filename, 'w') as f:
        for item in imports:
            f.write(item + "\n")
        for item in currency_strings:
            f.write(item + "\n")
        f.write(alls)

def generate_predefined_currencies_json() -> None:
    """Generate a JSON file with predefined currencies based on pre-created CSV."""
    csv_file = 'iso_currency_codes.csv'
    json_file = 'predefined_currencies.json'

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
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(currencies_dict, f, ensure_ascii=False, indent=4)

    print(f"Predefined currencies JSON saved to '{json_file}'")

# Call the function
generate_predefined_currencies_json()
