import sys

from dotenv import load_dotenv

# Load env vars from a .env file
load_dotenv()

sys.path.insert(0, "")

from ezoff import members_return

res = members_return({"inactive_members_with_items": True, "role_id": 4052})
pass
