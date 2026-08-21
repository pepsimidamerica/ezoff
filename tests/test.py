"""
Random tests.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load env vars from a .env file
load_dotenv()

sys.path.insert(0, "")

from ezoff.client import EZOClient

cli = EZOClient(
    subdomain=os.environ["EZO_SUBDOMAIN"],
    token=os.environ["EZO_TOKEN"],
    cache_path=Path(__file__).parent.parent / ".cache" / "something.pkl",
)

ven = cli.vendor(62567).get()

pass

cli.close()

pass
