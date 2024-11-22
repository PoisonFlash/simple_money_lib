import pandas as pd

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


# URLs of Wikipedia pages with the ISO codes tables
currency_url = 'https://en.wikipedia.org/wiki/ISO_4217'  # ISO currency codes
country_url = 'https://en.wikipedia.org/wiki/ISO_3166-1'  # ISO country codes

# Load currencies from Wikipedia, clean, and save to CSV
csv_file = 'iso_currency_codes.csv'
read_wiki_table(currency_url, 1) \
    .pipe(clean_df, r'\[.*?\]') \
    .to_csv(csv_file, index=False)
print(f"ISO currency codes table saved to '{csv_file}'")

# Load countries from Wikipedia, clean, and save to CSV
csv_file = 'iso_country_codes.csv'
read_wiki_table(country_url, 1) \
    .pipe(clean_df, r'\[.*?\]') \
    .to_csv(csv_file, index=False)
print(f"ISO countries codes table saved to '{csv_file}'")
