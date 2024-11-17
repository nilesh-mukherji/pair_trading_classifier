import requests
import pandas as pd
import os

# Replace with your Financial Modeling Prep API key
API_KEY = os.getenv("API_KEY")

# List of top 10 sector indices (replace with actual symbols from FMP if needed)
sector_indices = [
    "SPY",  # S&P 500 ETF as a placeholder
    "XLY",  # Consumer Discretionary
    "XLP",  # Consumer Staples
    "XLE",  # Energy
    "XLF",  # Financials
    "XLV",  # Health Care
    "XLI",  # Industrials
    "XLK",  # Information Technology
    "XLB",  # Materials
    "XLRE"  # Real Estate
]

# Function to fetch historical data for a given index
def fetch_historical_data(index_symbol):
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{index_symbol}?apikey={API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if "historical" in data:
            return pd.DataFrame(data["historical"])
        else:
            print(f"No historical data available for {index_symbol}")
            return None
    else:
        print(f"Failed to fetch data for {index_symbol}: {response.status_code}")
        return None

# Directory to save the CSV files
output_dir = "./sector_data/"

# Fetch and save data for each index
for index in sector_indices:
    print(f"Fetching data for {index}...")
    historical_data = fetch_historical_data(index)
    if historical_data is not None:
        historical_data.to_csv(f"{output_dir}{index}_historical.csv", index=False)
        print(f"Data for {index} saved to {output_dir}{index}_historical.csv")
    else:
        print(f"No data saved for {index}")

print("Data fetching complete!")