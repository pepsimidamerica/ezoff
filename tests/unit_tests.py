from datetime import datetime
from pprint import pprint

from ezoff import *


def check_asset_checkout():
    asset = asset_checkout(
        asset_id=19671,
        user_id=1285712,
        location_id=8326,
        request_verification=False,
        comments=f"Checked out by 279 #TEST.",
    )
    pprint(asset.model_dump())


def check_asset_update_location():
    asset = asset_update_location(asset_id=19671, location_seq_num=160)
    pprint(asset.model_dump())


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


def check_location_v1_return():
    loc = location_return_v1(location_id=13075)
    pprint(loc.model_dump())


def check_locations_return():
    locs = locations_return()
    print(f"Returned {len(locs)} locations.")


def check_work_order_create():
    asset_id = 19671
    wo = {
        "assigned_to_id": 1336290,
        "custom_fields": [
            {
                "id": 728,
                "name": "Estimated Service Minutes",
                "type": "double",
                "value": 60,
            },
            {
                "id": 729,
                "name": "Service Details",
                "type": "string",
                "value": "Asset ID: 144788 : Fountain - Replacement for K8 "
                "- 60 Minutes",
            },
            {"id": 739, "name": "Depot", "type": "dropdown", "value": "11 Marion"},
        ],
        "description": "Customer is in need of a new fountain. Existing fountain has ",
        "due_date": "2026-06-17T06:00:00Z",
        "expected_start_date": "2026-06-17T07:00:00Z",
        "location_id": 7,
        "mark_items_unavailable": False,
        "priority": "medium",
        "reviewer_id": "1336290",
        "title": "279 IS TEST",
        "work_type_name": "Delivery",
    }
    res = work_order_create(**wo)
    pprint(res.model_dump())
    wo_id = res.id

    components = [{"resource_id": asset_id, "resource_type": "Asset"}]
    res = work_order_add_component(work_order_id=wo_id, components=components)
    pprint(res.model_dump())

    res = work_order_add_checklist(work_order_id=wo_id, checklist_id=1223, asset_id=asset_id)
    pprint(res)


def check_work_order_return():
    wo_id = 35220
    wopd = work_order_return(work_order_id=wo_id)
    pprint(wopd.model_dump())


def check_work_orders_return():
    filter = {
        "reviewer_id": 1336290,  # Dispatch
        "state": ["in_progress", "not_started"],
    }

    work_orders = work_orders_return(filter=filter)
    print(f"Returned {len(work_orders)} work orders.")


def check_work_order_force_complete():
    work_order_id = 35220
    work_order_force_complete(work_order_id=work_order_id)


def check_work_order_update():
    # work_order_id = 35220
    # update_data = {"custom_fields": [{"id": 739, "value": "11 Marion"}]}

    work_order_id = 36736
    update_data = {
        "location_id": 160,
        "custom_fields": [{"id": 739, "value": "11 Marion"}],
    }

    work_order_update(work_order_id=work_order_id, update_data=update_data)


def check_work_order_routing_update():
    work_order_routing_update(
        work_order_id=35220,
        assigned_to_id=244379,
        # supervisor_id=244379,
        # task_type_id=21450,
        start_dttm=datetime.now(),
        due_dttm=datetime.now(),
        reviewer_id=244379,
    )



# check_members_return()
# check_members_return_v1()

# check_asset_checkout()
# check_assets_return()
# check_asset_update_location()

# check_locations_return()
# check_location_return()
# check_location_v1_return()


check_work_order_create()

# check_work_order_return()
# check_work_orders_return()
# check_checklist_return()
# check_work_order_force_complete()
# check_work_order_update()
# check_work_order_routing_update()
