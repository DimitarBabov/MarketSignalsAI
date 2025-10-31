# File: data_loader.py
import pandas as pd

# Load financial data from CSV
def load_data(csv_file):
    """Load financial data from a CSV file with yfinance multi-header format."""
    # Read CSV skipping the ticker row (row 1) and datetime header row (row 2)
    # Rows: 0=columns, 1=ticker, 2=datetime header, 3+=data
    df = pd.read_csv(csv_file, skiprows=[1, 2])
    
    # The first column is 'Price' but contains datetime values
    time_col = df.columns[0]  # This is 'Price'
    
    # Parse datetime and set as index
    df[time_col] = pd.to_datetime(df[time_col], utc=True)
    df.set_index(time_col, inplace=True)
    df.index.name = 'Datetime'
    
    # Return only OHLCV columns
    return df[['Open', 'High', 'Low', 'Close', 'Volume']]