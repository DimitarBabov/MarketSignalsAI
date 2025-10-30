import argparse
from datetime import date
from pathlib import Path
from typing import Dict, List

import yaml
import yfinance as yf


def get_supported_intervals() -> List[str]:
    # From yfinance docs/source as of 2025-10: minute to monthly
    return [
        "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h",
        "1d", "5d", "1wk", "1mo", "3mo",
    ]


def get_preset_to_interval() -> Dict[str, str]:
    # Common presets mapped to yfinance intervals
    return {
        "minute": "1m",
        "hourly": "1h",
        "daily": "1d",
        "weekly": "1wk",
        "monthly": "1mo",
    }


def load_config(config_path: str = "Data/config.yaml") -> dict:
    """Load configuration from YAML file"""
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Download OHLCV from Yahoo via yfinance. "
            "Reads tickers and intervals from config.yaml by default."
        )
    )
    parser.add_argument("--config", type=str, default="Data/config.yaml", help="Path to config file (default: Data/config.yaml)")
    parser.add_argument("--ticker", type=str, default=None, help="Override: single ticker to download (ignores config tickers)")
    parser.add_argument("--start", type=str, default=None, help="Override: start date YYYY-MM-DD")
    parser.add_argument("--end", type=str, default=date.today().strftime("%Y-%m-%d"), help="End date YYYY-MM-DD (default: today)")

    parser.add_argument(
        "--interval",
        type=str,
        default=None,
        help="Override: single interval to download (ignores config intervals)",
    )
    
    parser.add_argument(
        "--list-intervals",
        action="store_true",
        help="Print supported yfinance intervals and exit",
    )
    
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list_intervals:
        print("Supported intervals:")
        for itv in get_supported_intervals():
            print(f"- {itv}")
        return

    # Load configuration
    config = load_config(args.config)
    
    # Determine tickers to fetch
    if args.ticker:
        tickers = [args.ticker]
    else:
        tickers = config.get('tickers', ['SLV'])
    
    # Determine intervals to fetch
    if args.interval:
        intervals_to_fetch = [args.interval]
    else:
        intervals_to_fetch = config.get('intervals', ['1d'])
    
    # Get parameters from config
    start_date = args.start or config.get('start_date', '2010-01-01')
    end_date = args.end
    intraday_period = config.get('intraday_period', '60d')
    one_minute_period = config.get('one_minute_period', '7d')
    
    print(f"Downloading data for {len(tickers)} ticker(s) across {len(intervals_to_fetch)} interval(s)...")
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Intervals: {', '.join(intervals_to_fetch)}\n")

    intraday_set = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"}
    all_results = []
    
    for ticker in tickers:
        print(f"\n{'='*60}")
        print(f"Processing {ticker}")
        print(f"{'='*60}")
        
        for interval in intervals_to_fetch:
            try:
                if interval in intraday_set:
                    period = one_minute_period if interval == "1m" else intraday_period
                    df = yf.download(
                        ticker,
                        period=period,
                        interval=interval,
                        progress=False,
                        threads=False,
                    )
                else:
                    df = yf.download(
                        ticker,
                        start=start_date,
                        end=end_date,
                        interval=interval,
                        progress=False,
                        threads=False,
                    )

                # Create directory structure: Data/[symbol]/
                ticker_upper = ticker.upper()
                data_dir = Path("Data") / ticker_upper
                data_dir.mkdir(parents=True, exist_ok=True)
                out_path = data_dir / f"{ticker_upper}_{interval}.csv"
                
                df.to_csv(out_path)
                print(f"✓ {out_path}: {len(df):,} rows")
                all_results.append((ticker, interval, len(df)))
            except Exception as e:
                print(f"✗ {ticker} {interval}: {e}")
                all_results.append((ticker, interval, 0))

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for ticker, interval, nrows in all_results:
        status = "✓" if nrows > 0 else "✗"
        print(f"{status} {ticker:6s} {interval:5s}: {nrows:,} rows")


if __name__ == "__main__":
    main()