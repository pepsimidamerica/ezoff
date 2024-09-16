import os
import sys
from datetime import datetime, timedelta
from pprint import pprint

from dotenv import load_dotenv

# Load env vars from a .env file
load_dotenv()

sys.path.insert(0, "")

from ezoff import *

# res = ezoff.retire_asset(
#     14753,
#     {
#         "fixed_asset[retire_reason_id]": 250829,
#         "fixed_asset[retired_on]": "08/30/2024",
#         "fixed_asset[salvage_value]": 100.00,
#     },
# )

# res = ezoff.reactivate_asset(14753, {"fixed_asset[location_id]": 7})

# item_id = get_items_for_token_input("#14753")[0]["id"]

# pass

# res = ezoff.get_work_orders({"filters[item]": item_id})
# pass

res = get_all_inventories()

pass
