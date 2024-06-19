import json
import os
from pprint import pprint

from assets import *
from groups import *
from locations import *
from members import *
from workorders import *

if __name__ == "__main__":
    """
    Testing
    """
    # Import JSON config file
    try:
        with open("config.json") as json_file:
            config = json.load(json_file)
    except Exception as e:
        print("Error, could not open config file: ", e)
        exit(1)
    os.environ["EZO_BASE_URL"] = config["EZO_BASE_URL"]
    os.environ["EZO_TOKEN"] = config["EZO_TOKEN"]

    result = get_subgroups(356045)
    pass
    pprint(result)
