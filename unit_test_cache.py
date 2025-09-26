import logging
import sys

# from dotenv import load_dotenv
from ezoff import *

# Load env vars from a .env file
# load_dotenv()

# sys.path.insert(0, "")

logger = logging.getLogger(__name__)



def print_test_heading(title: str):
    logger.debug("*" * 100)
    logger.debug(f"** Testing {title} Cache")
    logger.debug("*" * 100)


def test_asset_cache():
    print_test_heading(title="Asset")
    ac = AssetCache(debug=True, use_saved=False)
    locations = [11336, 12388]
    for location in locations:
        asset_filter = {"location_id": location}
        ac.download(filter=asset_filter)

    for asset_id in ac.assets:
        asset = ac.assets[asset_id]
        logger.debug(f"ID: {asset.id} Name: {asset.name}")
    pass


def test_location_cache():
    print_test_heading(title="Location")
    lc = LocationCache(debug=True, use_saved=False)
    location_filter = {"state": "active"}
    lc.download(filter=location_filter)

    for location_id in lc.locations:
        location = lc.locations[location_id]
        logger.debug(f"ID: {location.id} Name: {location.name}")


def test_member_cache():
    print_test_heading(title="Member")
    mc = MemberCache(debug=True, use_saved=False)
    manager_ids = [223968, 497695]
    for mgr_id in manager_ids:
        member_filter = {"manager_id": mgr_id}
        mc.download(filter=member_filter)

    for member_id in mc.members:
        member = mc.members[member_id]
        logger.debug(f"ID: {member.id} Name: {member.full_name}")
    pass


def test_workorder_cache():
    print_test_heading(title="Work Order")
    wc = WorkOrderCache(debug=True, use_saved=False)
    assets_ids = [27325, 14753]
    for asset_id in assets_ids:
        asset_filter = {"asset_id": asset_id}
        wc.download(filter=asset_filter)

    for workorder_id in wc.work_orders:
        workorder = wc.work_orders[workorder_id]
        logger.debug(f"ID: {workorder.id} Name: {workorder.title}")
    pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    print('Running EZ-Office Cache Unit Tests')
    test_asset_cache()
    # test_location_cache()
    test_member_cache()
    test_workorder_cache()
