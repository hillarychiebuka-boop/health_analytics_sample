import os

# Facility Configuration
FACILITIES = [
    "State House Medical Center", 
    "Lafia Specialist Hospital", 
    "Keffi General Hospital", 
    "Akwanga General Hospital"
]

# Brand & Color Palette (Enterprise Slate & Health Blue)
COLOR_PRIMARY = "#0F172A"    # Dark Slate Header
COLOR_SECONDARY = "#0284C7"  # Vibrant Health Blue
COLOR_BG = "#F8FAFC"         # Clean Light Gray

# Asset Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")  # Adjust extension if logo is .jpg or .svg