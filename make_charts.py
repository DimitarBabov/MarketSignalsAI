import os
import glob
from typing import Tuple

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def infer_time_column(df: pd.DataFrame) -> str:
	"""Infer the datetime column name from known options."""
	for candidate in ["Datetime", "Date", "timestamp", "time", "date_time", "datetime"]:
		if candidate in df.columns:
			return candidate
	# Fallback: assume the first column is time-like
	return df.columns[0]


def read_close_series(csv_path: str) -> Tuple[pd.Series, pd.Series, str, str]:
	"""Read a CSV and return time series (index) and close values, plus ticker and timeframe label.

	The repository CSVs appear to have headers like:
	- row 0 (1st row): Price,Close,High,Low,Open,Volume (column names)
	- row 1 (2nd row): Ticker,SLV,SLV,SLV,SLV,SLV
	- row 2 (3rd row): Datetime or Date
	- row 3+ (4th row onwards): actual data
	"""
	# Read with skiprows to skip the first 3 metadata rows, and use row 0 as header
	data = pd.read_csv(csv_path, skiprows=[1, 2])
	
	if data.shape[0] == 0:
		raise ValueError(f"No data rows in {csv_path}")

	# Read the raw file again just to extract ticker from row 2 (index 1)
	raw = pd.read_csv(csv_path, header=None, nrows=2)
	try:
		ticker = str(raw.iloc[1, 1])  # Row 2, column 2 (index 1,1) should have 'SLV'
	except Exception:
		ticker = os.path.basename(csv_path).split("_")[0]

	# Infer time column - should be first column (either 'Price', 'Datetime', or 'Date')
	# Actually, looking at the structure, the first column name is 'Price' but contains datetime
	time_col = data.columns[0]  # This will be 'Price' column which contains the datetime
	
	# Parse datetime
	data[time_col] = pd.to_datetime(data[time_col], utc=True, errors="coerce")
	# Drop rows that failed to parse
	data = data.dropna(subset=[time_col])

	# Close column should be the 'Close' column
	close_col = "Close"
	if close_col not in data.columns:
		close_col = data.columns[1]  # Fallback to second column
	
	data[close_col] = pd.to_numeric(data[close_col], errors="coerce")
	data = data.dropna(subset=[close_col])

	# Timeframe from filename: e.g., SLV_1h.csv -> 1h
	base = os.path.basename(csv_path)
	parts = os.path.splitext(base)[0].split("_")
	timeframe = parts[1] if len(parts) > 1 else ""

	return data[time_col], data[close_col], ticker, timeframe


def save_chart(csv_path: str, output_dir: str = "charts", last_n: int = 100) -> str:
	"""Generate and save a 512x512 chart for the last N close prices from the CSV."""
	time_series, closes, ticker, timeframe = read_close_series(csv_path)

	# Keep only the last N points
	time_series = time_series.iloc[-last_n:]
	closes = closes.iloc[-last_n:]

	# Ensure output directory exists
	os.makedirs(output_dir, exist_ok=True)

	# Create figure 512x512 (in inches: dpi * inches = pixels). Use dpi=100 => 5.12 inches
	fig, ax = plt.subplots(figsize=(5.12, 5.12), dpi=100)
	ax.plot(time_series, closes, linewidth=1.5, color="#1f77b4")

	# Get the last datetime and format it based on timeframe
	last_datetime = time_series.iloc[-1]
	if timeframe in ["1m", "2m", "5m", "15m", "30m", "1h", "60m", "90m"]:
		# For intraday data: show YYYY-MM-DD HH:MM
		last_dt_str = last_datetime.strftime('%Y-%m-%d %H:%M')
	elif timeframe in ["1d", "5d", "1wk"]:
		# For daily/weekly data: show YYYY-MM-DD
		last_dt_str = last_datetime.strftime('%Y-%m-%d')
	elif timeframe in ["1mo", "3mo"]:
		# For monthly data: show YYYY-MM
		last_dt_str = last_datetime.strftime('%Y-%m')
	else:
		# Default: show YYYY-MM-DD HH:MM
		last_dt_str = last_datetime.strftime('%Y-%m-%d %H:%M')

	# Labels and title with ticker, timeframe, and last datetime
	label = f"Ticker Timeframe: {ticker} {timeframe}\nLast Time Period: {last_dt_str}"
	ax.set_title(label)
	ax.set_xlabel("Time")
	ax.set_ylabel("Price")

	# Rotate x labels for readability
	fig.autofmt_xdate()

	# Tight layout to avoid clipping
	plt.tight_layout()

	# Save
	outfile = os.path.join(output_dir, f"{ticker}_{timeframe or 'tf'}.png")
	fig.savefig(outfile)
	plt.close(fig)
	return outfile


def main() -> None:
	pattern = os.path.join(os.path.dirname(__file__), "SLV_*.csv")
	csv_files = sorted(glob.glob(pattern))
	if not csv_files:
		print("No CSV files found.")
		return

	for csv_path in csv_files:
		try:
			outfile = save_chart(csv_path)
			print(f"Saved chart: {outfile}")
		except Exception as exc:
			print(f"Failed to process {csv_path}: {exc}")


if __name__ == "__main__":
	main()


