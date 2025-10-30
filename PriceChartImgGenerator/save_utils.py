import os

def save_candlestick_image(image, ticker, timeframe, window_size, end_date, output_folder, trend_strength=None):
    """Save the candlestick image with a filename based on the ticker, timeframe, window size, and end date.
    
    Args:
        image: PIL Image object to save
        ticker: Ticker symbol
        timeframe: Timeframe (e.g., '1d', '1h')
        window_size: Number of candles in the image
        end_date: End date string
        output_folder: Output directory path
        trend_strength: Optional trend strength value to include at end of filename
    """
    if trend_strength is not None:
        # Format trend_strength to 3 decimal places and add at the end
        filename = f"{ticker}_{timeframe}_{window_size}c_{end_date}_{trend_strength:.3f}.png"
    else:
        filename = f"{ticker}_{timeframe}_{window_size}c_{end_date}.png"
    
    filepath = os.path.join(output_folder, filename)
    image.save(filepath)
    #print(f"Saved: {filepath}")
    return filename