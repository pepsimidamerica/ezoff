import sys

from dotenv import load_dotenv

# Load env vars from a .env file
load_dotenv()

sys.path.insert(0, "")

from ezoff import get_filtered_assets

res = get_filtered_assets({"status": "possessions_of", "filter_param_val": 244382})
print(res)
pass
