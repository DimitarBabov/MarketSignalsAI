import os
import shutil
import json
import numpy as np
from sklearn.cluster import KMeans

def normalize_json(input_json_path, timeframe):
    """Normalize regression data and add timeframe-specific trend strength.
    
    Args:
        input_json_path: Path to the regression data JSON file
        timeframe: Timeframe string (e.g., '5m', '1h', '1d', '1wk', '1mo')
    """
    epsilon = 1e-6
    with open(input_json_path, 'r') as file:
        json_data = json.load(file)

    # Replace '_regression_data' with '_trend_price' in filename
    base, ext = os.path.splitext(input_json_path)
    output_json_path = base.replace('_regression_data', '_trend_price') + ext

    # Extract parameters
    max_dev_values = [item["max_dev"] for item in json_data.values() if isinstance(item, dict)]
    colored_pixels_ratios = [item["colored_pixels_ratio"] for item in json_data.values() if isinstance(item, dict)]
   
    max_dev_mean = np.mean(max_dev_values)
    colored_pixels_mean = np.mean(colored_pixels_ratios)
    

    modified_json = {
        "_comments": [
            "shape: sequence of slopes ('n' = negative, 'p' = positive).",          
            f"trend_strength_{timeframe}: (price_change / max_dev_norm) / colored_pixels_ratio_norm",
            f"current_price_{timeframe}: close price of the last candle in the window (for trading simulation)"
        ]
    }

    for key, value in json_data.items():
        if not isinstance(value, dict):
            modified_json[key] = value
            continue

        max_dev = value["max_dev"]
        price_change = value["price_change"]
        colored_pixels_ratio = value["colored_pixels_ratio"]
        current_price = value.get("current_price", None)  # Get current_price if exists

        max_dev_norm = max_dev/max_dev_mean
        colored_pixels_ratio_norm = colored_pixels_ratio/colored_pixels_mean   

        # Calculate trend strength (negate because of inverted y-axis in image coordinates)
        # Positive value = price going up, Negative value = price going down
        trend_strength = -(price_change / max_dev_norm)

        slopes = [value["slope_first"], value["slope_second"], value["slope_third"], value["slope_whole"]]
        shape = "".join("p" if s > 0 else "n" for s in slopes)

        # Create keys with timeframe suffix
        trend_key = f"trend_strength_{timeframe}"
        price_key = f"current_price_{timeframe}"
        
        modified_json[key] = {
            "shape": shape,
            trend_key: trend_strength/colored_pixels_ratio_norm,
            price_key: current_price
        }

    with open(output_json_path, 'w') as file:
        json.dump(modified_json, file, indent=4)

    print(f"Trend & Price data saved to: {output_json_path}")
    return output_json_path, modified_json


def rename_images_with_trend_strength(output_folder, normalized_json_data, json_file_path):
    """Rename image files to include normalized trend strength values and update JSON keys."""
    import os
    import json
    
    renamed_count = 0
    updated_json = {}
    
    # Copy non-dict entries (like _comments)
    for key, value in normalized_json_data.items():
        if not isinstance(value, dict):
            updated_json[key] = value
    
    for filename, data in normalized_json_data.items():
        if not isinstance(data, dict) or not filename.endswith('.png'):
            continue
        
        # Extract trend strength from normalized data (find trend_strength_* key)
        trend_strength = None
        for key in data.keys():
            if key.startswith('trend_strength_'):
                trend_strength = data[key]
                break
        
        if trend_strength is None:
            updated_json[filename] = data
            continue
        
        # Build old and new file paths
        old_path = os.path.join(output_folder, filename)
        
        # Check if file already has trend strength (skip if already renamed)
        if '_trend_' in filename:
            updated_json[filename] = data
            continue
            
        # Insert trend strength before .png extension
        base_name = filename.replace('.png', '')
        new_filename = f"{base_name}_trend_{trend_strength:.3f}.png"
        new_path = os.path.join(output_folder, new_filename)
        
        # Rename the file
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            renamed_count += 1
            # Update JSON with new filename as key
            updated_json[new_filename] = data
        else:
            # File doesn't exist, keep old key
            updated_json[filename] = data
    
    # Save updated JSON with new filenames as keys
    with open(json_file_path, 'w') as f:
        json.dump(updated_json, f, indent=4)
    
    print(f"Renamed {renamed_count} images with normalized trend strength values")
    print(f"Updated JSON file with new filenames")
    return renamed_count