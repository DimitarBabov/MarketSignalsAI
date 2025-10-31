# MarketSignalsAI - Data Processing Workflow

This document describes the complete workflow for downloading market data and generating candlestick chart images with trend analysis.

---

## Prerequisites

1. **Python 3.9+** installed
2. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Required packages:**
   - pandas >= 2.0.0
   - matplotlib >= 3.7.0
   - yfinance >= 0.2.0
   - numpy >= 1.24.0
   - pillow >= 10.0.0
   - pyyaml >= 6.0

---

## Step 1: Configure Tickers and Intervals

Edit `Data/config.yaml` to specify which tickers and timeframes to download:

```yaml
# List of tickers to download
tickers:
  - SLV
  - AGQ

# List of intervals to download for each ticker
intervals:
  - 5m
  - 1h
  - 1d
  - 1wk
  - 1mo

# Download parameters
start_date: "2010-01-01"
intraday_period: "60d"
one_minute_period: "7d"
```

**Available intervals:**
- Intraday: `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m`, `1h`
- Daily+: `1d`, `5d`, `1wk`, `1mo`, `3mo`

---

## Step 2: Download Market Data

Run the data downloader script to fetch OHLCV data from Yahoo Finance:

```bash
python Data/download_ohlc.py
```

This will:
- Read tickers and intervals from `Data/config.yaml`
- Download data for each combination
- Save CSV files to `Data/[TICKER]/[TICKER]_[INTERVAL].csv`

**Example output structure:**
```
Data/
├── SLV/
│   ├── SLV_5m.csv
│   ├── SLV_1h.csv
│   ├── SLV_1d.csv
│   ├── SLV_1wk.csv
│   └── SLV_1mo.csv
└── AGQ/
    ├── AGQ_5m.csv
    ├── AGQ_1h.csv
    ├── AGQ_1d.csv
    ├── AGQ_1wk.csv
    └── AGQ_1mo.csv
```

### Alternative: Download Single Ticker/Interval

```bash
# Download only SLV daily data
python Data/download_ohlc.py --ticker SLV --interval 1d

# Download only AGQ 1-hour data
python Data/download_ohlc.py --ticker AGQ --interval 1h
```

---

## Step 3: Generate Candlestick Images

Run the image processing script:

```bash
python Charts/process_to_imgs_main.py
```

### Option A: Batch Processing (Recommended)

When prompted:
```
Process all available data from config? (y/n, default: n): y
```

This will:
- Process **all tickers and intervals** from `config.yaml`
- Generate images for each combination
- Create trend analysis JSON files
- Show progress for each ticker/timeframe

**Output:** `Data_Charts_Images/output/[TICKER]/[INTERVAL]/`

### Option B: Interactive Single Processing

When prompted:
```
Process all available data from config? (y/n, default: n): n
Enter the ticker symbol (default: SLV): AGQ
Enter the timeframe (e.g., '5m', '1h', '1d', '1wk', '1mo'): 1d
```

This will process only the specified ticker and timeframe.

---

## Step 4: Output Structure

After processing, your output will be organized as:

```
Data_Charts_Images/output/
├── SLV/
│   ├── 5m/
│   │   ├── images/
│   │   │   ├── SLV_5m_25c_2025-10-30 12-00-00_trend_15.234.png
│   │   │   ├── SLV_5m_25c_2025-10-30 12-01-00_trend_12.456.png
│   │   │   └── ...
│   │   └── regression_data/
│   │       ├── SLV_5m_regression_data.json (raw data)
│   │       └── SLV_5m_trend_price.json (normalized)
│   ├── 1h/
│   ├── 1d/
│   ├── 1wk/
│   └── 1mo/
└── AGQ/
    └── (same structure)
```

---

## Generated Files Explained

### 1. **Candlestick Images** (`images/*.png`)

- **Filename format:** `{TICKER}_{INTERVAL}_{WINDOW_SIZE}c_{DATE}_{TIME}_trend_{VALUE}.png`
- **Example:** `SLV_1d_25c_2025-10-30 00-00-00_trend_27.649.png`
- **Contains:**
  - 25 candlesticks (configurable window size)
  - Color-coded: Green (bullish), Red (bearish)
  - 100px height (configurable)
  - Trend strength value in filename

### 2. **Raw Regression Data** (`regression_data/*_regression_data.json`)

Contains detailed technical analysis for each image:
- Slope calculations (first/second/third/whole window)
- Price change metrics
- Max deviation values
- Colored pixel ratios
- Current price

### 3. **Normalized Trend & Price Data** (`regression_data/*_trend_price.json`)

**Optimized for trading simulation:**

```json
{
    "_comments": [
        "shape: sequence of slopes ('n' = negative, 'p' = positive).",
        "trend_strength_1d: (price_change / max_dev_norm) / colored_pixels_ratio_norm",
        "current_price_1d: close price of the last candle in the window (for trading simulation)"
    ],
    "SLV_1d_25c_2025-10-30 00-00-00_trend_27.649.png": {
        "shape": "pnpn",
        "trend_strength_1d": 27.649,
        "current_price_1d": 34.89
    }
}
```

**Key fields:**
- `shape`: Pattern of slopes (p=positive, n=negative)
- `trend_strength_{interval}`: Normalized trend strength (positive=bullish, negative=bearish)
- `current_price_{interval}`: Last close price in the window

---

## Configuration Parameters

Edit these in `Charts/process_to_imgs_main.py` (lines 154-162 for batch mode, lines 236-244 for interactive mode):

```python
window_size = 25                    # Number of candlesticks per image
height = 100                        # Image height in pixels
overlap = 24                        # Overlapping candles between windows
blur = False                        # Apply Gaussian blur
blur_radius = 1.25                  # Blur intensity (if enabled)
draw_regression_lines = False       # Draw trend lines on image
color_candles = True                # Color code bull/bear candles
create_regression_labels = True     # Generate JSON label files
trend_strength_to_img_name = True   # Include trend value in filename
```

**Common configurations:**

| Use Case | window_size | height | overlap | blur |
|----------|-------------|--------|---------|------|
| **ML Training** | 16-32 | 64-128 | high (e.g., 15/16) | False |
| **Visual Analysis** | 50-100 | 200+ | low (e.g., 1) | False |
| **Pattern Recognition** | 20-30 | 100-150 | medium (e.g., 10-15) | True |

---

## Quick Start Example

```bash
# 1. Configure tickers (already done in config.yaml)

# 2. Download data
python Data/download_ohlc.py

# 3. Generate images (batch mode)
python Charts/process_to_imgs_main.py
# When prompted: y

# 4. Check output
ls Data_Charts_Images/output/SLV/1d/images/
```

---

## Troubleshooting

### Issue: "No data available for ticker"
**Solution:** Run step 2 first to download data

### Issue: "No CSV files available"
**Solution:** Check that the interval exists in `Data/config.yaml` and was downloaded

### Issue: "Module not found"
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Images not renamed with trend strength
**Solution:** Ensure `trend_strength_to_img_name = True` and `create_regression_labels = True`

---


## Notes

- **Storage:** Images are cleared and regenerated each run to save space
- **Normalization:** Trend strength is normalized across the entire dataset for comparability
- **Timeframe-specific:** All metrics include the timeframe suffix (e.g., `trend_strength_5m`)
- **UTC Timestamps:** All dates/times are in UTC timezone

