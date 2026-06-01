from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

DEFAULT_DEM_PATH = DATA_DIR / "GMTED2km.tif"
DEFAULT_CALIBRATION_PATH = DATA_DIR / "RadiometricCorrectionParameter.json"

NODATA = -9999
REFLECTANCE_SCALE = 10000
