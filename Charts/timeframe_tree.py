"""
Efficient multi-timeframe tree for normalized trend_price JSON files.

The tree hierarchy is organized as: year -> month -> day -> hour -> minute.
Each node stores timeframe-specific metrics (trend_strength_*, last_close_price_*).
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Optional, List


@dataclass
class TreeNode:
    data: Dict[str, Dict[str, float]] = field(default_factory=dict)
    months: Dict[int, "TreeNode"] = field(default_factory=dict)
    days: Dict[int, "TreeNode"] = field(default_factory=dict)
    hours: Dict[int, "TreeNode"] = field(default_factory=dict)
    minutes: Dict[int, "TreeNode"] = field(default_factory=dict)


class TimeframeTree:
    """Hierarchical data structure for multi-timeframe market data."""

    TIMEFRAMES = ["1mo", "1wk", "1d", "1h", "5m"]

    def __init__(self, ticker: str, base_path: str = "Data_Charts_Images/output"):
        self.ticker = ticker.upper()
        self.base_path = Path(base_path)
        self.tree: Dict[int, TreeNode] = defaultdict(TreeNode)
        self.week_lookup: Dict[tuple, Dict[str, float]] = {}

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------
    def load_all_timeframes(self) -> None:
        ticker_root = self.base_path / self.ticker
        if not ticker_root.exists():
            raise FileNotFoundError(f"No data found for ticker '{self.ticker}' at {ticker_root}")

        for timeframe in self.TIMEFRAMES:
            tf_file = ticker_root / timeframe / "regression_data" / f"{self.ticker}_{timeframe}_trend_price.json"
            if tf_file.exists():
                self._load_timeframe_file(tf_file, timeframe)

    def _load_timeframe_file(self, path: Path, timeframe: str) -> None:
        with path.open("r") as file:
            payload = json.load(file)

        count = 0
        for key, record in payload.items():
            if not isinstance(record, dict):
                continue

            timestamp = record.get("timestamp")
            trend_key = f"trend_strength_{timeframe}"
            price_key = f"last_close_price_{timeframe}"

            if not timestamp or trend_key not in record or price_key not in record:
                continue

            dt = datetime.fromisoformat(timestamp)
            metrics = {
                "timestamp": timestamp,
                trend_key: record[trend_key],
                price_key: record[price_key],
            }

            self._insert(dt, timeframe, metrics)
            count += 1

        if count == 0:
            print(f"Warning: no records loaded from {path}")

    # ------------------------------------------------------------------
    # Tree insertion helpers
    # ------------------------------------------------------------------
    def _insert(self, dt: datetime, timeframe: str, metrics: Dict[str, float]) -> None:
        year_node = self.tree[dt.year]
        month_node = year_node.months.setdefault(dt.month, TreeNode())

        if timeframe == "1mo":
            month_node.data[timeframe] = metrics
            return

        if timeframe == "1wk":
            iso_year, iso_week, _ = dt.isocalendar()
            week_key = (iso_year, iso_week)
            self.week_lookup[week_key] = metrics
            month_node.data.setdefault("1wk", {})
            month_node.data["1wk"][iso_week] = metrics
            return

        day_node = month_node.days.setdefault(dt.day, TreeNode())

        if timeframe == "1d":
            day_node.data[timeframe] = metrics
            return

        hour_node = day_node.hours.setdefault(dt.hour, TreeNode())

        if timeframe == "1h":
            hour_node.data[timeframe] = metrics
            return

        if timeframe == "5m":
            minute_node = hour_node.minutes.setdefault(dt.minute, TreeNode())
            minute_node.data[timeframe] = metrics
            return

    # ------------------------------------------------------------------
    # Query API
    # ------------------------------------------------------------------
    def query(
        self,
        year: int,
        month: Optional[int] = None,
        day: Optional[int] = None,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
    ) -> Optional[Dict[str, Dict[str, float]]]:
        """Return timeframe metrics for the requested granularity."""

        year_node = self.tree.get(year)
        if not year_node:
            return None

        if month is None:
            return {
                m: data.data.get("1mo")
                for m, data in year_node.months.items()
                if "1mo" in data.data
            }

        month_node = year_node.months.get(month)
        if not month_node:
            return None

        if day is None:
            result: Dict[str, Dict[str, float]] = {}
            if "1mo" in month_node.data:
                result["1mo"] = month_node.data["1mo"]
            if "1wk" in month_node.data:
                result["1wk"] = month_node.data["1wk"]
            return result or None

        day_node = month_node.days.get(day)
        if not day_node:
            return None

        if hour is None:
            result: Dict[str, Dict[str, float]] = {}
            if "1d" in day_node.data:
                result["1d"] = day_node.data["1d"]
            iso_year, iso_week, _ = date(year, month, day).isocalendar()
            week_metrics = self.week_lookup.get((iso_year, iso_week))
            if week_metrics:
                result["1wk"] = week_metrics
            return result or None

        hour_node = day_node.hours.get(hour)
        if not hour_node:
            return None

        if minute is None:
            data = hour_node.data.get("1h")
            return {"1h": data} if data else None

        minute_node = hour_node.minutes.get(minute)
        if not minute_node:
            return None

        data = minute_node.data.get("5m")
        return {"5m": data} if data else None

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def get_latest(self, timeframe: str = "5m") -> Optional[Dict[str, float]]:
        if timeframe not in self.TIMEFRAMES:
            raise ValueError(f"Unsupported timeframe '{timeframe}'")

        for year in sorted(self.tree.keys(), reverse=True):
            year_node = self.tree[year]
            for month in sorted(year_node.months.keys(), reverse=True):
                month_node = year_node.months[month]
                if timeframe == "1mo" and "1mo" in month_node.data:
                    return month_node.data["1mo"]

                if timeframe == "1wk" and "1wk" in month_node.data:
                    weeks = month_node.data["1wk"]
                    latest_week = sorted(weeks.keys(), reverse=True)[0]
                    return weeks[latest_week]

                for day in sorted(month_node.days.keys(), reverse=True):
                    day_node = month_node.days[day]
                    if timeframe == "1d" and "1d" in day_node.data:
                        return day_node.data["1d"]

                    for hour in sorted(day_node.hours.keys(), reverse=True):
                        hour_node = day_node.hours[hour]
                        if timeframe == "1h" and "1h" in hour_node.data:
                            return hour_node.data["1h"]

                        if timeframe == "5m":
                            for minute in sorted(hour_node.minutes.keys(), reverse=True):
                                minute_node = hour_node.minutes[minute]
                                if "5m" in minute_node.data:
                                    return minute_node.data["5m"]
        return None

    def get_stats(self) -> Dict[str, int]:
        counts = {tf: 0 for tf in self.TIMEFRAMES}
        for year_node in self.tree.values():
            for month_node in year_node.months.values():
                if "1mo" in month_node.data:
                    counts["1mo"] += 1
                if "1wk" in month_node.data:
                    counts["1wk"] += len(month_node.data["1wk"])
                for day_node in month_node.days.values():
                    if "1d" in day_node.data:
                        counts["1d"] += 1
                    for hour_node in day_node.hours.values():
                        if "1h" in hour_node.data:
                            counts["1h"] += 1
                        for minute_node in hour_node.minutes.values():
                            if "5m" in minute_node.data:
                                counts["5m"] += 1
        return counts


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Query multi-timeframe trend data")
    parser.add_argument("--ticker", type=str, default="SLV", help="Ticker symbol")
    parser.add_argument("--year", type=int, required=True, help="Year to query")
    parser.add_argument("--month", type=int, help="Month (1-12)")
    parser.add_argument("--day", type=int, help="Day (1-31)")
    parser.add_argument("--hour", type=int, help="Hour (0-23)")
    parser.add_argument("--minute", type=int, help="Minute (0-59)")
    args = parser.parse_args()

    tree = TimeframeTree(args.ticker)
    tree.load_all_timeframes()

    result = tree.query(args.year, args.month, args.day, args.hour, args.minute)
    if not result:
        print("No data for the requested period")
        return

    print(f"Results for {args.ticker}:")
    for tf, metrics in result.items():
        if not metrics:
            continue
        print(f"\n{tf}:")
        for key, value in metrics.items():
            if key == "timestamp":
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value:.6f}")

    print("\nRecord counts by timeframe:")
    for tf, count in tree.get_stats().items():
        print(f"  {tf:>3}: {count}")


if __name__ == "__main__":
    main()

