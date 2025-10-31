# File: main.py
import os
import json
import sys

import pandas as pd
from data_loader import load_data
from image_utils import create_candlestick_with_regression_image
from save_utils import save_candlestick_image
from json_utils import normalize_json, rename_images_with_trend_strength

def process_data_into_images(csv_file, ticker, timeframe, window_size=56, height=224, 
                             output_folder='data_processed_imgs',
                             regression_folder='data_processed_imgs', 
                             overlap=23, blur=False, blur_radius=0, 
                             draw_regression_lines=True,
                             color_candles=True,
                             create_regression_labels=True,
                             trend_strength_to_img_name=False):
    """Process all data in the CSV file into candlestick images with specified window size and overlap."""
    data = load_data(csv_file)
  
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    else:
        # Delete all existing images in the folder
        for filename in os.listdir(output_folder):
            if filename.endswith('.png'):
                file_path = os.path.join(output_folder, filename)
                os.remove(file_path)
        print(f"Cleared existing images from {output_folder}")
    
    # Calculate the step size for the sliding window to create specified overlap
    step_size = window_size - overlap

    # Dictionary to store regression slopes for each image
    regression_data = {}

    # Slide through the dataset with specified overlap
    for i in range(0, len(data) - window_size + 1, step_size):
        window_data = data.iloc[i:i + window_size]
        if window_data.isnull().values.any():
            print(f"Skipping window {i}-{i+window_size} due to NaN values")
            continue
        # Adjust format for hourly data
        end_date = window_data.index[-1].strftime('%Y-%m-%d %H-%M-%S')
        (image, 
         slope_first, slope_second, slope_third, slope_whole, 
         price_change, 
         max_dev_scaled,
         colored_pixels_ratio) = (
        create_candlestick_with_regression_image(window_data, 
                                                 height=height, 
                                                 candlestick_width=3, 
                                                 spacing=1, 
                                                 blur=blur, 
                                                 blur_radius=blur_radius,
                                                 draw_regression_lines=draw_regression_lines, 
                                                 color_candles=color_candles))
        
        # Save image without trend strength first (will rename later with normalized value)
        filename = save_candlestick_image(image, ticker, timeframe, window_size, end_date, 
                                         output_folder, trend_strength=None)

        # Get the last close price from the window (current price)
        current_price = float(window_data['Close'].iloc[-1])

        # Save the regression slopes and additional data for this image
        regression_data[filename] = {
            "slope_first": slope_first,
            "slope_second": slope_second,
            "slope_third": slope_third,
            "slope_whole": slope_whole,
            "max_dev": max_dev_scaled,
            "price_change": price_change,
            "colored_pixels_ratio": colored_pixels_ratio,
            "current_price": current_price
        }
    #regression lables are only allowed if blur is false 
    #this is do because later we feed the resnet train model with blured images but 
    #want to use proper lables
    if(create_regression_labels and not blur):
        # Save the regression data to a JSON file
        if not os.path.exists(regression_folder):
            os.makedirs(regression_folder)

        regression_file = os.path.join(regression_folder, f"{ticker}_{timeframe}_regression_data.json")
        with open(regression_file, 'w') as json_file:
            json.dump(regression_data, json_file, indent=4)
        print(f"Regression data saved to '{regression_file}'")
        
        # Normalize and get the normalized data (pass timeframe as argument)
        normalized_json_path, normalized_data = normalize_json(regression_file, timeframe)
        print(f"Trend & Price data saved to '{normalized_json_path}'")
        
        # Rename image files with normalized trend strength values if enabled
        if trend_strength_to_img_name:
            print(f"\nRenaming images with normalized trend strength values...")
            rename_images_with_trend_strength(output_folder, normalized_data, normalized_json_path)



if __name__ == "__main__":   

    # Ask if user wants to process all available data
    process_all = input("Process all available data from config? (y/n, default: n): ").strip().lower()
    
    if process_all == 'y' or process_all == 'yes':
        # Load config to get tickers and intervals
        import yaml
        config_path = 'Data/config.yaml'
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            tickers = config.get('tickers', [])
            intervals = config.get('intervals', [])
            
            if not tickers or not intervals:
                print("No tickers or intervals found in config.yaml")
                exit()
            
            print(f"\nProcessing {len(tickers)} ticker(s) across {len(intervals)} interval(s)...")
            print(f"Tickers: {', '.join(tickers)}")
            print(f"Intervals: {', '.join(intervals)}\n")
            
            # Process each combination
            for ticker in tickers:
                for timeframe in intervals:
                    ticker_path = os.path.join('Data', ticker.upper())
                    
                    # Check if data exists
                    if not os.path.exists(ticker_path):
                        print(f"⚠ Skipping {ticker} - data folder not found")
                        continue
                    
                    # Find CSV file
                    available_files = [f for f in os.listdir(ticker_path) if f.endswith('.csv') and timeframe in f]
                    if not available_files:
                        print(f"⚠ Skipping {ticker} {timeframe} - CSV not found")
                        continue
                    
                    csv_file = os.path.join(ticker_path, available_files[0])
                    output_folder = os.path.join('Data_Charts_Images', 'output', ticker.upper(), timeframe, "images")
                    regression_folder = os.path.join('Data_Charts_Images', 'output', ticker.upper(), timeframe, 'regression_data')
                    
                    print(f"\n{'='*60}")
                    print(f"Processing: {ticker} - {timeframe}")
                    print(f"{'='*60}")
                    
                    # Set parameters
                    window_size = 16
                    height = 64
                    overlap = 15
                    blur = False
                    blur_radius = 1.25
                    draw_regression_lines = False
                    color_candles = True
                    create_regression_labels = True
                    trend_strength_to_img_name = True
                    
                    # Process
                    try:
                        process_data_into_images(csv_file, ticker, timeframe, window_size, height, 
                                               output_folder, regression_folder, overlap, blur, 
                                               blur_radius, draw_regression_lines, 
                                               color_candles=color_candles, 
                                               create_regression_labels=create_regression_labels,
                                               trend_strength_to_img_name=trend_strength_to_img_name)
                        print(f"✓ Completed {ticker} {timeframe}")
                    except Exception as e:
                        print(f"✗ Error processing {ticker} {timeframe}: {e}")
            
            print(f"\n{'='*60}")
            print("All processing complete!")
            print(f"{'='*60}")
            exit()
            
        except FileNotFoundError:
            print(f"Config file not found: {config_path}")
            print("Falling back to interactive mode...\n")
        except Exception as e:
            print(f"Error reading config: {e}")
            print("Falling back to interactive mode...\n")
    
    # Interactive mode (single ticker/timeframe)
    ticker = input("Enter the ticker symbol (default: SLV): ").strip() or "SLV"
    timeframe = input("Enter the timeframe (e.g., '5m', '1h', '1d', '1wk', '1mo'): ").strip() or "1d"
    
    # Updated to search in Data/[ticker]/ folder
    ticker_path = os.path.join('Data', ticker.upper())
    
    custom_csv = None
    custom_output = None
    if len(sys.argv) > 1:
        custom_csv = sys.argv[1]
    if len(sys.argv) > 2:
        custom_output = sys.argv[2]
    
    if not os.path.exists(ticker_path) and not custom_csv:
        print(f"No data available for ticker {ticker}.")
        print(f"Expected path: {ticker_path}")
        print(f"Run: python Data/download_ohlc.py --ticker {ticker}")
        exit()
    
    # Find the CSV file for the specified timeframe
    available_files = []
    if os.path.exists(ticker_path):
        available_files = [f for f in os.listdir(ticker_path) if f.endswith('.csv') and timeframe in f]
    if not available_files and not custom_csv:
        print(f"No CSV files available for ticker {ticker} and timeframe {timeframe}.")
        print(f"Available files in {ticker_path}:")
        if os.path.exists(ticker_path):
            all_files = [f for f in os.listdir(ticker_path) if f.endswith('.csv')]
            for f in all_files:
                print(f"  - {f}")
        exit()
    
    # Get the CSV file
    if custom_csv:
        csv_file = custom_csv
    else:
        csv_file = os.path.join(ticker_path, available_files[0])
    
    print(f"\nProcessing: {csv_file}")
    
    # Parameters for processing    
    if custom_output:
        output_folder = custom_output
        regression_folder = custom_output  # or customize as needed
    else:
        output_folder = os.path.join('Data_Charts_Images', 'output', ticker.upper(), timeframe, "images")
        regression_folder = os.path.join('Data_Charts_Images', 'output', ticker.upper(), timeframe, 'regression_data')
    window_size = 25          # Number of candlesticks per image
    height = 100                # Image height in pixels 
    overlap = 24               # Number of overlapping candlesticks between consecutive windows    
    blur = False               # Apply blur for natural mammalian vision effect
    blur_radius = 1.25
    draw_regression_lines = False
    color_candles = True
    create_regression_labels = True
    trend_strength_to_img_name = True  # Include trend strength in image filename
    
    # Process the data and generate images
    process_data_into_images(csv_file, ticker, timeframe, window_size, height, output_folder, 
                           regression_folder, overlap, blur, blur_radius, draw_regression_lines, 
                           color_candles=color_candles, create_regression_labels=create_regression_labels,
                           trend_strength_to_img_name=trend_strength_to_img_name)
