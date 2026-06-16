"""
Random tests.
"""

import sys

from dotenv import load_dotenv

# Load env vars from a .env file
load_dotenv()

sys.path.insert(0, "")

from ezoff import locations_return

res = locations_return(state="active")
pass
