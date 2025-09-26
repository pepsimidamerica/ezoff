import sys

from dotenv import load_dotenv

# Load env vars from a .env file
load_dotenv()

sys.path.insert(0, "")

from ezoff import inventories_return

# res = assets_return({"group_id": 356045, "sub_group_id": 442903})
res = inventories_return()
pass
