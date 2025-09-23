import sys

from dotenv import load_dotenv

# Load env vars from a .env file
load_dotenv()

sys.path.insert(0, "")

from ezoff import assets_return

res = assets_return({"group_id": 356045, "sub_group_id": 442903})
pass
for asset in res:
    if asset.identifier == "8203":
        print("Found asset")
