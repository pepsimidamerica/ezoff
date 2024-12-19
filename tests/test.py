import os
import sys
from datetime import datetime, timedelta
from pprint import pprint

from dotenv import load_dotenv

# Load env vars from a .env file
load_dotenv()

sys.path.insert(0, "")

from ezoff import *

res = ezoff.get_filtered_members({"filters[location][value]": 148121})
print(res)
pass
