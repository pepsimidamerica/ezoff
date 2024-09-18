"""
This module contains functions to interact with work orders in EZOfficeInventory.
"""

import os
from typing import Literal, Optional

import requests

from ezoff.auth import Decorators


@Decorators.check_env_vars
def get_work_orders(filter: Optional[dict]) -> dict:
    """
    Get filtered work orders.

    Note: This endpoint is weird. It supports many more filters than the
    documentation advertises. There is a corresponding filter for each
    of the filter options in the EZOffice web interface.
    https://ezo.io/ezofficeinventory/developers/#api-get-filtered-task
    """

    if filter is not None:
        # Remove any keys that are not valid
        valid_keys = [
            "filters[assigned_to]",
            "filters[created_by]",
            "filters[supervisor]",
            "filters[reviewer]",
            "filters[created_on]",
            "filters[state]",
            "filters[item]",
            "filters[priority]",
            "filters[task_type]",
            "filters[due_date]",
            "filters[expected_start_date]",
            "filters[repetition_start_date]",
            "filters[repetition_start_date]",
            "filters[repetition_end_date]",
            "filters[preventative]",
            "filters[on_repeat]",
            "filters[task_location]",
            # "filters[review_pending_on_me]",  # Don't know if actually useful when API is calling and not user
            "filters[scheduled]",
        ]

        filter = {k: v for k, v in filter.items() if k in valid_keys}
        filter["filter"] = "filter"  # Required when using filters

    url = os.environ["EZO_BASE_URL"] + "tasks.api"

    page = 1
    all_work_orders = {}

    while True:
        params = {"page": page}
        if filter is not None:
            params.update(filter)

        try:
            response = requests.get(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params=params,
                timeout=30,
            )
        except Exception as e:
            print("Error, could not get work orders from EZOfficeInventory: ", e)
            raise Exception(
                "Error, could not get work orders from EZOfficeInventory: " + str(e)
            )

        if response.status_code != 200:
            print(
                f"Error {response.status_code}, could not get work orders from EZOfficeInventory: ",
                response.content,
            )
            break

        data = response.json()

        if "work_orders" not in data:
            print(
                f"Error, could not get work orders from EZOfficeInventory: ",
                response.content,
            )
            raise Exception(
                f"Error, could not get work orders from EZOfficeInventory: "
                + str(response.content)
            )

        all_work_orders.update(data["work_orders"])

        if "total_pages" not in data:
            print("Error, could not get total_pages from EZOfficeInventory: ", data)
            break

        if page >= data["total_pages"]:
            break

        page += 1

    return all_work_orders


@Decorators.check_env_vars
def get_work_order_details(work_order_id: int) -> dict:
    """
    Get work order details
    https://ezo.io/ezofficeinventory/developers/#api-retrive-task-details
    """

    url = os.environ["EZO_BASE_URL"] + "tasks/" + str(work_order_id) + ".api"

    try:
        response = requests.get(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=30,
        )
    except Exception as e:
        print("Error, could not get work order from EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not get work order from EZOfficeInventory: " + str(e)
        )

    if response.status_code != 200:
        print(
            f"Error {response.status_code}, could not get work order from EZOfficeInventory: ",
            response.content,
        )
        raise Exception(
            f"Error, could not get work order from EZOfficeInventory: "
            + str(response.content)
        )

    return response.json()


@Decorators.check_env_vars
def get_work_order_types() -> list[dict]:
    """
    Get work order types
    Function doesn't appear to be paginated even though most other similar
    functions are.
    https://ezo.io/ezofficeinventory/developers/#api-get-task-types
    """

    url = os.environ["EZO_BASE_URL"] + "task_types.api"

    try:
        response = requests.get(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=30,
        )
    except Exception as e:
        print("Error, could not get work order types from EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not get work order types from EZOfficeInventory: " + str(e)
        )

    if response.status_code != 200:
        print(
            f"Error {response.status_code}, could not get work order types from EZOfficeInventory: ",
            response.content,
        )
        raise Exception(
            f"Error, could not get work order types from EZOfficeInventory: "
            + str(response.content)
        )

    if "work_order_types" not in response.json():
        print(
            f"Error, could not get work order types from EZOfficeInventory: ",
            response.content,
        )
        raise Exception(
            f"Error, could not get work order types from EZOfficeInventory: "
            + str(response.content)
        )

    return response.json()["work_order_types"]


@Decorators.check_env_vars
def create_work_order(work_order: dict) -> dict:
    """
    Create a work order
    https://ezo.io/ezofficeinventory/developers/#api-create-task
    """

    # Required fields
    if "task[title]" not in work_order:
        raise ValueError("work_order must have 'task[title]' key")
    if "task[task_type]" not in work_order:
        raise ValueError("work_order must have 'task[task_type]' key")
    if "due_date" not in work_order:
        raise ValueError("work_order must have 'due_date' key")
        # Also check that the date is in the correct format mm/dd/yyyy
        try:
            datetime.strptime(work_order["due_date"], "%m/%d/%Y")
        except ValueError:
            raise ValueError("work_order['due_date'] must be in the format mm/dd/yyyy")

    # Remove any keys that are not valid
    valid_keys = [
        "task[title]",
        "task[task_type]",
        "task[task_type_id]",
        "task[priority]",
        "task[assigned_to_id]",
        "task[reviewer_id]",
        "task[mark_items_unavailable]",
        "expected_start_date",
        "expected_start_time",
        "due_date",
        "start_time",
        "base_cost",
        "inventory_ids",
        "checklist_ids",
        "associated_assets",
        "custom_field_names",
    ]

    work_order = {
        k: v
        for k, v in work_order.items()
        if k in valid_keys
        or k.startswith("task[custom_attributes]")
        or k.startswith("linked_inventory_items")
        or k.startswith("associated_checklists")
    }

    url = os.environ["EZO_BASE_URL"] + "tasks.api"

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data=work_order,
            timeout=30,
        )
    except Exception as e:
        print("Error, could not create work order in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not create work order in EZOfficeInventory: " + str(e)
        )

    return response.json()


@Decorators.check_env_vars
def start_work_order(work_order_id: int) -> dict:
    """
    Start a work order
    https://ezo.io/ezofficeinventory/developers/#api-start-task
    """

    url = (
        os.environ["EZO_BASE_URL"]
        + "tasks/"
        + str(work_order_id)
        + "/mark_in_progress.api"
    )

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=30,
        )
    except Exception as e:
        print("Error, could not start work order in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not start work order in EZOfficeInventory: " + str(e)
        )

    return response.json()


@Decorators.check_env_vars
def end_work_order(work_order_id: int) -> dict:
    """
    End a work order
    https://ezo.io/ezofficeinventory/developers/#api-end-task
    """

    url = (
        os.environ["EZO_BASE_URL"]
        + "tasks/"
        + str(work_order_id)
        + "/mark_complete.api"
    )

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=30,
        )
    except Exception as e:
        print("Error, could not end work order in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not end work order in EZOfficeInventory: " + str(e)
        )

    return response.json()


@Decorators.check_env_vars
def add_work_log_to_work_order(work_order_id: int, work_log: dict) -> dict:
    """
    Add a work log to a work order
    resource id and resource type vary depending on type of component
    work log is being added against. Asset vs Group vs Member etc. Docu has a table
    https://ezo.io/ezofficeinventory/developers/#api-add-work-log-to-task
    """

    # Required fields
    if "task_work_log[time_spent]" not in work_log:
        raise ValueError("work_log must have 'task_work_log[time_spent]' key")
    if "task_work_log[user_id]" not in work_log:
        raise ValueError("work_log must have 'task_work_log[user_id]' key")

    # Remove any keys that are not valid
    valid_keys = [
        "task_work_log[time_spent]",
        "task_work_log[user_id]",
        "task_work_log[description]",
        "task_work_log[resource_id]",
        "task_work_log[resource_type]",
        "started_on_date",
        "started_on_time",
        "ended_on_date",
        "ended_on_time",
    ]

    work_log = {k: v for k, v in work_log.items() if k in valid_keys}

    url = (
        os.environ["EZO_BASE_URL"]
        + "tasks/"
        + str(work_order_id)
        + "/task_work_logs.api"
    )

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data=work_log,
            timeout=30,
        )
    except Exception as e:
        print("Error, could not add work log to work order in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not add work log to work order in EZOfficeInventory: "
            + str(e)
        )

    return response.json()


@Decorators.check_env_vars
def add_linked_inv_to_work_order(work_order_id: int, linked_inv: dict) -> dict:
    """
    Add linked inventory items to a work order
    resource id and resource type vary depending on type of component
    linked inventory is being added against. Asset vs Group vs Member etc. Docu has a table
    https://ezo.io/ezofficeinventory/developers/#api-add-linked-inventory-to-task
    """

    # Required fields
    if "inventory_id" not in linked_inv:
        raise ValueError("linked_inv must have 'inventory_id' key")
    if not any(
        key.startswith("linked_inventory_items[") and key.endswith("][quantity]")
        for key in linked_inv.keys()
    ):
        raise ValueError(
            "linked_inv must have a key that matches the format linked_inventory_items[{Inventory#}][quantity]"
        )

    # Remove any keys that are not valid
    valid_keys = ["inventory_id"]

    linked_inv = {
        k: v
        for k, v in linked_inv.items()
        if k in valid_keys
        or (k.startswith("linked_inventory_items[") and k.endswith("][quantity]"))
        or (k.startswith("linked_inventory_items[") and k.endswith("][location_id]"))
        or (k.startswith("linked_inventory_items[") and k.endswith("][resource_id]"))
        or (k.startswith("linked_inventory_items[") and k.endswith("][resource_type]"))
    }

    url = (
        os.environ["EZO_BASE_URL"]
        + "tasks/"
        + str(work_order_id)
        + "/link_inventory.api"
    )

    try:
        response = requests.patch(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data=linked_inv,
            timeout=30,
        )
    except Exception as e:
        print(
            "Error, could not add linked inventory items to work order in EZOfficeInventory: ",
            e,
        )
        raise Exception(
            "Error, could not add linked inventory items to work order in EZOfficeInventory: "
            + str(e)
        )

    return response.json()


@Decorators.check_env_vars
def get_checklists() -> list[dict]:
    """
    Get checklists
    https://ezo.io/ezofficeinventory/developers/#api-retrieve-checklists
    """

    page = 1
    all_checklists = []

    while True:
        try:
            response = requests.get(
                os.environ["EZO_BASE_URL"] + "checklists.api",
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params={"page": page},
                timeout=30,
            )
        except Exception as e:
            print("Error, could not get checklists from EZOfficeInventory: ", e)
            raise Exception(
                "Error, could not get checklists from EZOfficeInventory: " + str(e)
            )

        if response.status_code != 200:
            print(
                f"Error {response.status_code}, could not get checklists from EZOfficeInventory: ",
                response.content,
            )
            break

        data = response.json()

        if "checklists" not in data:
            print(
                f"Error, could not get checklists from EZOfficeInventory: ",
                response.content,
            )
            raise Exception(
                f"Error, could not get checklists from EZOfficeInventory: "
                + str(response.content)
            )

        all_checklists.extend(data["checklists"])

        if "total_pages" not in data:
            print("Error, could not get total_pages from EZOfficeInventory: ", data)
            break

        if page >= data["total_pages"]:
            break

        page += 1

    return all_checklists
