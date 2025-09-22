import sys

from dotenv import load_dotenv

# Load env vars from a .env file
load_dotenv()

sys.path.insert(0, "")

from ezoff import work_orders_return

res = work_orders_return(
    {"assigned_to_id": 1336290, "state": ["in_progress", "not_started"]}
)
pass
