import os
import sys
from datetime import datetime, timedelta
from pprint import pprint
from ezoff import *


opts = {
    'seqs': 14753,
    'project_id': 2,
}

res = project_link_asset(options=opts)

pprint(res)
