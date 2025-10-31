"""
Test suite for TimeframeTree data structure.

Tests tree loading, querying, and data integrity across multiple timeframes.
"""

import sys
import os

# Add parent directory to path to import the Charts module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Charts.timeframe_tree import TimeframeTree
from datetime import datetime


def print_separator(title=""):
    """Print a formatted separator line."""
    if title:
        print(f"\n{'='*70}")
        print(f"  {title}")
        print('='*70)
    else:
        print('-'*70)


def test_load_data(ticker='SLV'):
    """Test 1: Load all timeframes and verify data is loaded."""
    print_separator(f"TEST 1: Loading Data for {ticker}")
    
    try:
        tree = TimeframeTree(ticker)
        tree.load_all_timeframes()
        
        stats = tree.get_stats()
        print(f"\n✓ Successfully loaded data for {ticker}")
        print(f"\nRecord counts by timeframe:")
        total_records = 0
        for tf in ['5m', '1h', '1d', '1wk', '1mo']:
            count = stats.get(tf, 0)
            total_records += count
            status = "✓" if count > 0 else "✗"
            print(f"  {status} {tf:>4}: {count:>6,} records")
        
        print(f"\nTotal records loaded: {total_records:,}")
        
        if total_records == 0:
            print("\n⚠ WARNING: No data loaded. Check if trend_price.json files exist.")
            return None
        
        return tree
        
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        return None


def test_query_by_year(tree, year=2025):
    """Test 2: Query data by year only."""
    print_separator(f"TEST 2: Query by Year ({year})")
    
    try:
        result = tree.query(year=year)
        
        if result:
            print(f"\n✓ Found data for year {year}")
            print(f"  Monthly records: {len(result)}")
            
            # Show sample
            months = sorted(result.keys())[:3]
            for month in months:
                if result[month]:
                    print(f"\n  Month {month}:")
                    data = result[month]
                    if isinstance(data, dict):
                        for key, value in list(data.items())[:2]:
                            print(f"    {key}: {value}")
        else:
            print(f"\n✗ No data found for year {year}")
            
    except Exception as e:
        print(f"\n✗ FAILED: {e}")


def test_query_by_month(tree, year=2025, month=10):
    """Test 3: Query data by year and month."""
    print_separator(f"TEST 3: Query by Month ({year}-{month:02d})")
    
    try:
        result = tree.query(year=year, month=month)
        
        if result:
            print(f"\n✓ Found data for {year}-{month:02d}")
            print(f"  Available timeframes: {list(result.keys())}")
            
            for tf, data in result.items():
                if tf == '1mo' and data:
                    print(f"\n  {tf} data:")
                    print(f"    Timestamp: {data.get('timestamp', 'N/A')}")
                    print(f"    Trend: {data.get(f'trend_strength_{tf}', 'N/A'):.3f}")
                    print(f"    Price: ${data.get(f'last_close_price_{tf}', 'N/A'):.2f}")
                elif tf == '1wk' and isinstance(data, dict):
                    print(f"\n  {tf} data: {len(data)} weekly records")
        else:
            print(f"\n✗ No data found for {year}-{month:02d}")
            
    except Exception as e:
        print(f"\n✗ FAILED: {e}")


def test_query_by_day(tree, year=2025, month=10, day=30):
    """Test 4: Query data by specific day."""
    print_separator(f"TEST 4: Query by Day ({year}-{month:02d}-{day:02d})")
    
    try:
        result = tree.query(year=year, month=month, day=day)
        
        if result:
            print(f"\n✓ Found data for {year}-{month:02d}-{day:02d}")
            
            for tf, data in result.items():
                if data:
                    print(f"\n  {tf} data:")
                    print(f"    Timestamp: {data.get('timestamp', 'N/A')}")
                    trend_key = f'trend_strength_{tf}'
                    price_key = f'last_close_price_{tf}'
                    if trend_key in data:
                        print(f"    Trend: {data[trend_key]:.3f}")
                    if price_key in data:
                        print(f"    Price: ${data[price_key]:.2f}")
        else:
            print(f"\n✗ No data found for {year}-{month:02d}-{day:02d}")
            
    except Exception as e:
        print(f"\n✗ FAILED: {e}")


def test_query_by_hour(tree, year=2025, month=10, day=30, hour=14):
    """Test 5: Query data by specific hour."""
    print_separator(f"TEST 5: Query by Hour ({year}-{month:02d}-{day:02d} {hour:02d}:00)")
    
    try:
        result = tree.query(year=year, month=month, day=day, hour=hour)
        
        if result:
            print(f"\n✓ Found data for {year}-{month:02d}-{day:02d} {hour:02d}:00")
            
            for tf, data in result.items():
                if data:
                    print(f"\n  {tf} data:")
                    print(f"    Timestamp: {data.get('timestamp', 'N/A')}")
                    trend_key = f'trend_strength_{tf}'
                    price_key = f'last_close_price_{tf}'
                    if trend_key in data:
                        print(f"    Trend: {data[trend_key]:.3f}")
                    if price_key in data:
                        print(f"    Price: ${data[price_key]:.2f}")
        else:
            print(f"\n✗ No data found for {year}-{month:02d}-{day:02d} {hour:02d}:00")
            
    except Exception as e:
        print(f"\n✗ FAILED: {e}")


def test_query_by_minute(tree, year=2025, month=10, day=30, hour=14, minute=30):
    """Test 6: Query data by specific minute (most granular)."""
    print_separator(f"TEST 6: Query by Minute ({year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d})")
    
    try:
        result = tree.query(year=year, month=month, day=day, hour=hour, minute=minute)
        
        if result:
            print(f"\n✓ Found data for {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}")
            
            for tf, data in result.items():
                if data:
                    print(f"\n  {tf} data:")
                    print(f"    Timestamp: {data.get('timestamp', 'N/A')}")
                    trend_key = f'trend_strength_{tf}'
                    price_key = f'last_close_price_{tf}'
                    if trend_key in data:
                        print(f"    Trend: {data[trend_key]:.3f}")
                    if price_key in data:
                        print(f"    Price: ${data[price_key]:.2f}")
        else:
            print(f"\n✗ No data found for {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}")
            
    except Exception as e:
        print(f"\n✗ FAILED: {e}")


def test_get_latest(tree):
    """Test 7: Get the most recent data for each timeframe."""
    print_separator("TEST 7: Get Latest Data Points")
    
    print("\nMost recent data per timeframe:")
    for tf in ['5m', '1h', '1d', '1wk', '1mo']:
        try:
            latest = tree.get_latest(tf)
            
            if latest:
                trend_key = f'trend_strength_{tf}'
                price_key = f'last_close_price_{tf}'
                
                print(f"\n  {tf}:")
                print(f"    Timestamp: {latest.get('timestamp', 'N/A')}")
                if trend_key in latest:
                    print(f"    Trend: {latest[trend_key]:.3f}")
                if price_key in latest:
                    print(f"    Price: ${latest[price_key]:.2f}")
            else:
                print(f"\n  {tf}: No data available")
                
        except Exception as e:
            print(f"\n  {tf}: ✗ FAILED - {e}")


def test_data_integrity(tree):
    """Test 8: Verify data integrity and structure."""
    print_separator("TEST 8: Data Integrity Check")
    
    issues = []
    
    # Test 1: Check if timestamps are present and valid
    print("\nChecking timestamps...")
    for tf in ['5m', '1h', '1d']:
        latest = tree.get_latest(tf)
        if latest:
            if not latest.get('timestamp'):
                issues.append(f"{tf}: Missing timestamp")
            else:
                try:
                    datetime.fromisoformat(latest['timestamp'])
                except:
                    issues.append(f"{tf}: Invalid timestamp format")
    
    # Test 2: Check if required keys are present
    print("Checking required keys...")
    for tf in ['5m', '1h', '1d']:
        latest = tree.get_latest(tf)
        if latest:
            trend_key = f'trend_strength_{tf}'
            price_key = f'last_close_price_{tf}'
            
            if trend_key not in latest:
                issues.append(f"{tf}: Missing {trend_key}")
            if price_key not in latest:
                issues.append(f"{tf}: Missing {price_key}")
    
    # Report results
    if issues:
        print(f"\n✗ Found {len(issues)} integrity issue(s):")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✓ All integrity checks passed!")


def test_query_performance(tree):
    """Test 9: Query performance for different granularities."""
    print_separator("TEST 9: Query Performance")
    
    import time
    
    queries = [
        ("Year query", lambda: tree.query(year=2025)),
        ("Month query", lambda: tree.query(year=2025, month=10)),
        ("Day query", lambda: tree.query(year=2025, month=10, day=30)),
        ("Hour query", lambda: tree.query(year=2025, month=10, day=30, hour=14)),
        ("Minute query", lambda: tree.query(year=2025, month=10, day=30, hour=14, minute=30)),
    ]
    
    print("\nQuery execution times:")
    for name, query_func in queries:
        start = time.time()
        result = query_func()
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        status = "✓" if result else "✗"
        print(f"  {status} {name:20s}: {elapsed:>8.3f} ms")


def run_all_tests(ticker='SLV'):
    """Run all test cases."""
    print(f"\n{'#'*70}")
    print(f"#  TIMEFRAME TREE TEST SUITE - {ticker}")
    print(f"{'#'*70}")
    
    # Load data
    tree = test_load_data(ticker)
    
    if not tree:
        print("\n✗ Cannot continue tests without loaded data")
        return
    
    # Run query tests
    test_query_by_year(tree, year=2025)
    test_query_by_month(tree, year=2025, month=10)
    test_query_by_day(tree, year=2025, month=10, day=30)
    test_query_by_hour(tree, year=2025, month=10, day=30, hour=14)
    test_query_by_minute(tree, year=2025, month=10, day=30, hour=14, minute=30)
    
    # Latest data
    test_get_latest(tree)
    
    # Integrity checks
    test_data_integrity(tree)
    
    # Performance
    test_query_performance(tree)
    
    print_separator()
    print("\n✓ All tests completed!")
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test TimeframeTree implementation')
    parser.add_argument('--ticker', type=str, default='SLV', help='Ticker symbol to test')
    args = parser.parse_args()
    
    run_all_tests(args.ticker)

