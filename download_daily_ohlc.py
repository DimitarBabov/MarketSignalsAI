import argparse
from datetime import date
from typing import Dict, List

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Download OHLCV from Yahoo via yfinance with selectable timeframes. "
            "If neither --interval nor --preset is given, downloads all supported intervals."
        )
    )
    parser.add_argument("--ticker", type=str, default="SLV", help="Ticker symbol (default: SLV)")
    parser.add_argument("--start", type=str, default="2010-01-01", help="Start date YYYY-MM-DD (default: 2010-01-01)")
    parser.add_argument("--end", type=str, default=date.today().strftime("%Y-%m-%d"), help="End date YYYY-MM-DD (default: today)")

    presets = sorted(get_preset_to_interval().keys())
    parser.add_argument(
        "--preset",
        type=str,
        choices=presets,
        default=None,
        help=f"Timeframe preset (maps to yfinance intervals). Choices: {presets}. If omitted and --interval not set, downloads all.",
    )

    supported_intervals = get_supported_intervals()
    parser.add_argument(
        "--interval",
        type=str,
        choices=supported_intervals,
        default=None,
        help=(
            "Explicit yfinance interval. If provided, overrides --preset. "
            f"Supported: {supported_intervals}"
        ),
    )

    parser.add_argument(
        "--list-intervals",
        action="store_true",
        help="Print supported yfinance intervals and exit",
    )

    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Output CSV path (default: <ticker>_<interval>.csv)",
    )

    parser.add_argument(
        "--intraday-period",
        type=str,
        default="60d",
        help=(
            "Period to use for intraday intervals (>=2m), default 60d. "
            "Valid: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max"
        ),
    )
    parser.add_argument(
        "--one-minute-period",
        type=str,
        default="7d",
        help=(
            "Period to use for 1m interval (Yahoo limits 1m history), default 7d. "
            "Valid: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list_intervals:
        print("Supported intervals:")
        for itv in get_supported_intervals():
            print(f"- {itv}")
        return

    # Determine which intervals to fetch
    supported = get_supported_intervals()
    if args.interval:
        intervals_to_fetch = [args.interval]
    elif args.preset:
        intervals_to_fetch = [get_preset_to_interval()[args.preset]]
    else:
        intervals_to_fetch = supported

    intraday_set = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"}
    results = []
    for interval in intervals_to_fetch:
        if interval in intraday_set:
            period = args.one_minute_period if interval == "1m" else args.intraday_period
            df = yf.download(
                args.ticker,
                period=period,
                interval=interval,
                progress=False,
                threads=False,
            )
        else:
            df = yf.download(
                args.ticker,
                start=args.start,
                end=args.end,
                interval=interval,
                progress=False,
                threads=False,
            )

        out_path = args.out if (args.out and len(intervals_to_fetch) == 1) else f"{args.ticker.upper()}_{interval}.csv"
        df.to_csv(out_path)
        print(f"Saved {out_path} with {len(df):,} rows")
        results.append((interval, len(df)))

    # Summary
    print("\nSummary:")
    for interval, nrows in results:
        print(f"- {interval}: {nrows:,} rows")


if __name__ == "__main__":
    main()