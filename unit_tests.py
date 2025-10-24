from datetime import timedelta, timezone, datetime
import json
from pprint import pprint

from ezoff import *


def check_asset_return():
    asset = asset_return(asset_id=88888)
    pprint(asset.model_dump())


def check_assets_return():
    # Test of get_assets_v2_pd
    filter = {"custom_fields": [{"id": 70779, "value": "Rent"}]}
    assets = assets_return(filter=filter)
    pprint(assets)
    print(f"Returned {len(assets)} assets.")

    for asset in assets:
        pprint(asset.model_dump())


def check_checklist_return():
    checklists = checklists_return()
    pprint(checklists)


def check_members_return():
    filter = {"role_id": "1"}
    members = members_return(filter=filter)
    pprint(members)


def check_members_return_v1():
    filter = {
        "filter": "employee_identification_number",
        "filter_val": "7606",
    }
    members = members_return_v1(filter=filter)
    pprint(members)


def check_location_return():
    loc = location_return(location_id=13075)
    pprint(loc.model_dump())


def check_locations_return():
    locs = locations_return()
    print(f"Returned {len(locs)} locations.")


def check_work_order_return():
    wo_id = 26531
    wopd = work_order_return(work_order_id=wo_id)
    pprint(wopd.model_dump())


def check_work_orders_return():
    filter = {
        # "reviewer_id": 1336290, # Dispatch
        "state": ["in_progress", "not_started"],
    }

    work_orders = work_orders_return(filter=filter)
    print(f"Returned {len(work_orders)} work orders.")


def check_work_order_force_complete():
    work_order_id = 27996
    work_order_force_complete(work_order_id=work_order_id)


def check_work_order_update():
    work_order_id = 17087
    update_data = {"custom_fields": [{"id": 739, "value": "11 Marion"}]}

    work_order_update(work_order_id=work_order_id, update_data=update_data)


# check_work_order_return()
# check_work_orders_return()
check_checklist_return()

# check_members_return()
# check_members_return_v1()

# check_assets_return()

# check_locations_return()
# check_location_return()

# check_work_order_force_complete()
# check_work_order_update()
