import sys

from dotenv import load_dotenv

# Load env vars from a .env file
load_dotenv()

sys.path.insert(0, "")

from ezoff import assets_return, inventories_return, locations_return, members_return

# TODO Test each of the returns that are involved with EZOffice-Sync

# assets = assets_return({"group_id": 356045}) # Passed
# inv = inventories_return() # Test again
loc = locations_return()
mem = members_return({"role_id": 3790})

pass
