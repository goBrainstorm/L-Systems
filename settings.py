import sys # Needed for float min/max, keep if rule parsing logic expands
import math # Keep for potential future settings needing math

# --- Constants ---
DRAWING_PADDING = 50
SLIDER_FLOAT_PRECISION = 1 # How many decimal places for float sliders

# --- Default Settings ---
DEFAULT_SETTINGS = {
    "axiom": "X",
    "rules_string": "X:F+[[X]-X]-F[-FX]+X,F:FF", # String representation
    "rules": {"X": "F+[[X]-X]-F[-FX]+X", "F": "FF"}, # Parsed representation
    "iterations": 5,
    "angle_deg": 25.0,
    "start_angle_deg": 90.0,
    "length": 5.0,
    "line_thickness": 1,
    # Removed start_pos, start_x_ratio, start_y_ratio - Renderer/Main will handle initial placement
    "line_color": (0, 255, 0),       # Green
    "background_color": (0, 0, 0), # Black
    "angle_variation_deg": 3.0,
    "length_variation_factor": 0.05
}

# --- Utility Functions ---
def parse_rules(rules_string):
    """Parses a string like 'F:FF,X:F+[[X]-X]-F[-FX]+X' into a dictionary."""
    rules = {}
    try:
        # Handle potential empty string or strings without colons gracefully
        if not rules_string or ':' not in rules_string:
            return {}
        pairs = rules_string.split(',')
        for pair in pairs:
            pair = pair.strip()
            if ':' in pair:
                key, value = pair.split(':', 1)
                key = key.strip()
                value = value.strip()
                if key: # Ensure key is not empty
                    rules[key] = value
    except Exception as e:
        print(f"Error parsing rules string '{rules_string}': {e}. Using empty rules.")
        return {} # Return empty dict on error
    return rules

# Pre-parse the default rules string
DEFAULT_SETTINGS["rules"] = parse_rules(DEFAULT_SETTINGS["rules_string"]) 