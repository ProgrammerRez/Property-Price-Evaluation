import json

def read_csv_to_dict(filename):
    data = {}
    with open(filename, encoding='utf-8') as f:
        for line in f:
            if line.strip() and ',' in line:
                key, value = line.strip().split(',', 1)
                try:
                    key = int(key)
                    value = value.strip().strip('"')
                    data[key] = value
                except ValueError:
                    continue  # Skip lines with invalid data
    return data

# Read both CSVs
locality_dict = read_csv_to_dict('locality.csv')
price_dict = read_csv_to_dict('ppsqft.csv')

# Merge both into a single dictionary
merged_data = {}
for key in locality_dict:
    if key in price_dict:
        try:
            price = float(price_dict[key])
        except ValueError:
            price = price_dict[key]  # keep as string if not convertible
        merged_data[key] = {
            "locality": locality_dict[key],
            "price_per_sqft": price
        }

# Save as JSON
with open('merged_output.json', 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, indent=4)
