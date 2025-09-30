import sys

from dotenv import load_dotenv

# Load env vars from a .env file
load_dotenv()

sys.path.insert(0, "")

from ezoff import assets_return, locations_return

res = assets_return({"group_id": 356045})
# res = locations_return(state="inactive")
pass
