import pandas as pd

# URLs of Wikipedia pages with the ISO codes tables
currency_url = 'https://en.wikipedia.org/wiki/ISO_4217'  # ISO currency codes
country_url = 'https://en.wikipedia.org/wiki/ISO_3166-1'  # ISO country codes

# Load tables from Wikipedia
currency_tables = pd.read_html(currency_url)
country_tables = pd.read_html(country_url)

# ISO currency codes
currency_table = currency_tables[1]
# Clean all columns headers to remove [references]
currency_table.columns = currency_table.columns.str.replace(r'\[.*?\]', '', regex=True)
# Clean all columns to remove [references]
currency_table = currency_table.apply(
    lambda col: col.str.replace(r'\[.*?\]', '', regex=True) if col.dtype == 'object' else col)
# Save currencies to CSV
currency_table.to_csv('iso_currency_codes.csv', index=False)

# ISO country codes
country_table = country_tables[1]
# Clean all columns headers to remove [references]
country_table.columns = currency_table.columns.str.replace(r'\[.*?\]', '', regex=True)
# Clean all columns to remove [references]
country_table = currency_table.apply(
    lambda col: col.str.replace(r'\[.*?\]', '', regex=True) if col.dtype == 'object' else col)
# Save countries to CSV
country_table.to_csv('iso_country_codes.csv', index=False)

print("ISO currency codes and country codes tables have been saved.")
