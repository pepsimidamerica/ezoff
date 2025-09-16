"""
This module contains functions to interact with work orders in EZOfficeInventory.

Note: API will inconsistently use a 'tasks' or 'work_orders' key when returning
info from these endpoints. Each endpoint just needs to be checked which.
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import Literal

import requests
from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff.data_model import Component, WorkOrder
from ezoff.exceptions import (
    ChecklistLinkError,
    WorkOrderNotFound,
    WorkOrderUpdateError,
)

logger = logging.getLogger(__name__)


@Decorators.check_env_vars
def work_order_create(
    title: str,
    state: Literal["request"],
    priority: Literal["High", "Medium", "Low"],
    description: str | None = None,
    created_by_id: int | None = None,
    work_type_name: str | None = None,
    mark_items_unavailable: bool = False,
    warranty: bool = False,
    supervisor_id: int | None = None,
    assigned_to_id: int | None = None,
    assigned_to_type: str | None = None,
    secondary_assignee_ids: list[int] | None = None,
    reviewer_id: int | None = None,
    require_approval_from_reviewer: bool = False,
    location_id: int | None = None,
    expected_start_date: datetime | None = None,
    due_date: datetime | None = None,
    repetition: bool | None = None,
    repetition_start_date: datetime | None = None,
    repetition_end_date: datetime | None = None,
    repeat_every_duration: str | None = None,
    repeat_every_basis: int | None = None,
    recurrence_based_on_completion: bool | None = None,
    recurrence_based_on_interval: bool | None = None,
    custom_fields: list[dict] | None = None,
) -> WorkOrder | None:
    """
    Creates a work order.
    """

    params = {k: v for k, v in locals().items() if v is not None}

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders"

    try:
        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Cache-Control": "no-cache",
                "Host": f"{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            },
            data={"work_order": params},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error creating work order: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error creating work order: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating work order: {e}")
        raise Exception(f"Error creating work order: {e}")

    if response.status_code == 200 and "work_order" in response.json():
        return WorkOrder(**response.json()["work_order"])
    else:
        return None


@Decorators.check_env_vars
def service_create(asset_id: int, service: dict) -> dict:
    """
    Creates a service record against a given asset
    https://ezo.io/ezofficeinventory/developers/#api-create-service

    TODO Don't see this directly mentioned in the API v2 docs.

    :param asset_id: The ID of the asset to create the service record against
    :param service: A dictionary containing the service record details
    """

    # Required fields
    if "service[end_date]" not in service:
        raise ValueError("service must have 'service[end_date]' key")
    if "service_end_time" not in service:
        raise ValueError("service must have 'service_end_time' key")
    if "service_type_name" not in service:
        raise ValueError("service must have 'service_type_name' key")
    if "service[description]" not in service:
        raise ValueError("service must have 'service[description]' key")

    # Remove any keys that are not valid
    valid_keys = [
        "service[start_date]",
        "service_start_time",
        "service[end_date]",
        "service_end_time",
        "service_type_name",
        "service[description]",
        "inventory_ids",
    ]

    service = {
        k: v
        for k, v in service.items()
        if k in valid_keys or k.startswith("linked_inventory_items")
    }

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/assets/{asset_id}/services.api"

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            params={"create_service_ticket_only": "true"},
            data=service,
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error, could not create service: {e.response.status_code} - {e.response.content}"
        )
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not create service: {e}")
        raise

    return response.json()


@_basic_retry
@Decorators.check_env_vars
def work_order_return(work_order_id: int) -> WorkOrder | None:
    """
    Get a single work order.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}"

    try:
        response = requests.get(
            url,
            headers={
                "Accept": "application/json",
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Cache-Control": "no-cache",
                "Host": f"{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error getting work order: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error getting work order: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting work order: {e}")
        raise Exception(f"Error getting work order: {e}")

    if response.status_code == 200 and "work_order" in response.json():
        return WorkOrder(**response.json()["work_order"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def work_orders_return(filter: dict | None = None) -> list[WorkOrder]:
    """
    Get filtered work orders. Optionally filter using one or more work order fields.
    """

    if filter:
        for field in filter:
            if field not in WorkOrder.model_fields:
                raise ValueError(f"'{field}' is not a valid field for a work order.")
            filter = {"filters": filter}
    else:
        filter = None

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders"

    all_work_orders = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                data=filter,
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get work orders: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get work orders: {e}")
            raise

        data = response.json()

        if "tasks" not in data:
            logger.error(f"Error, could not get work orders: {response.content}")
            raise Exception(f"Error, could not get work orders: {response.content}")

        all_work_orders.extend(data["tasks"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [WorkOrder(**x) for x in all_work_orders]


@_basic_retry
@Decorators.check_env_vars
def work_order_types_return() -> list[dict]:
    """
    Get work order types
    Function doesn't appear to be paginated even though most other similar
    functions are.
    https://ezo.io/ezofficeinventory/developers/#api-get-task-types
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/assets/task_types.api"

    try:
        response = requests.get(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error, could not get work order types: {e.response.status_code} - {e.response.content}"
        )
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not get work order types: {e}")
        raise

    if "work_order_types" not in response.json():
        logger.error(f"Error, could not get work order types: {response.content}")
        raise Exception(f"Error, could not get work order types: {response.content}")

    return response.json()["work_order_types"]


# TODO Linked Work orders return


@Decorators.check_env_vars
def work_order_update(work_order_id: int, work_order: dict) -> dict:
    """
    Updates a work order.
    """

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
        "Cache-Control": "no-cache",
        "Host": f"{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Content-Length": "75",
    }
    url = f"{os.environ['EZO_BASE_URL']}api/v2/work_orders/{str(work_order_id)}/"

    try:
        response = requests.put(
            url,
            headers=headers,
            data=json.dumps(work_order),
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise WorkOrderNotFound(
            f"Error, could not update work order: {e.response.status_code} - {e.response.content}"
        )
    except requests.exceptions.RequestException as e:
        raise WorkOrderNotFound(f"Error, could not update work order: {str(e)}")

    return response.json()


@Decorators.check_env_vars
def work_order_add_work_log(work_order_id: int, work_log: dict) -> dict:
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
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error, could not add log to work order: {e.response.status_code} - {e.response.content}"
        )
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not add log to work order: {e}")
        raise

    return response.json()


@Decorators.check_env_vars
def work_order_add_linked_inv(work_order_id: int, linked_inv: dict) -> dict:
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
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error, could not add linked inv to work order: {e.response.status_code} - {e.response.content}"
        )
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not add linked inv to work order: {e}")
        raise

    return response.json()


def update_work_order_routing(
    work_order_id: int,
    assigned_to_id: str,
    task_type_id: int,
    start_dttm: datetime,
    due_dttm: datetime,
    supervisor_id: str | None = None,
    reviewer_id: str | None = None,
) -> dict:
    """Update the assigned to user and start/end time of a workorder.
    Intended for use by an external routing system.

    Args:
        work_order_id (int): User facing work order ID.
        assigned_to_id (str): System ID of user to assign to work order.
        task_type_id (int): Task type of the work order.
        start_dttm (date): Start datetime of the work order.
        due_dttm (date): Due datetime of the work order.
        supervisor_id (str): Supervisor ID to assign the work order.
        reviewer_id (str): Reviewer ID to assign the work order.

    Returns:
        dict: Response from the EZ Office API endpoint.
    """
    filter = {
        "task[assigned_to_id]": assigned_to_id,
        "task[task_type_id]": str(task_type_id),
        "due_date": due_dttm.strftime("%m/%d/%Y"),
        "start_time": due_dttm.strftime("%H:%M"),
        "expected_start_date": start_dttm.strftime("%m/%d/%Y"),
        "expected_start_time": start_dttm.strftime("%H:%M"),
    }

    if supervisor_id is not None:
        filter["task[supervisor_id]"] = supervisor_id
        print(f"Updating work order supervisor to: {supervisor_id}")

    if reviewer_id is not None:
        filter["task[reviewer_id]"] = reviewer_id

    result = update_work_order(work_order_id=work_order_id, filter=filter)

    return result


@Decorators.check_env_vars
def work_order_add_component(work_order_id: int, components: list[Component]) -> dict:
    """
    Adds a component to a work order.
    """

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
        "Cache-Control": "no-cache",
        "Host": f"{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Content-Length": "75",
    }
    url = (
        f"{os.environ['EZO_BASE_URL']}api/v2/work_orders/{work_order_id}/add_components"
    )
    payload = {"work_order": {"components": []}}
    for component in components:
        payload["work_order"]["components"].append(component.model_dump())

    try:
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload),
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise WorkOrderUpdateError(
            f"Error, could not create work order: {e.response.status_code} - {e.response.content}"
        )
    except requests.exceptions.RequestException as e:
        raise WorkOrderUpdateError(f"Error, could not create work order: {str(e)}")

    return response.json()


@Decorators.check_env_vars
def work_order_mark_in_progress(work_order_id: int) -> dict:
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
        response = requests.patch(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error, could not start work order: {e.response.status_code} - {e.response.content}"
        )
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not start work order: {e}")
        raise

    return response.json()


# TODO Mark on hold


@Decorators.check_env_vars
def work_order_mark_complete(work_order_id: int, completed_on_dttm: datetime) -> dict:
    """
    Completes a work order.
    """

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
        "Cache-Control": "no-cache",
        "Host": f"{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Content-Length": "75",
    }
    url = (
        f"{os.environ['EZO_BASE_URL']}api/v2/work_orders/{work_order_id}/mark_complete"
    )
    payload = {
        "work_order": {
            "completed_on_date": completed_on_dttm.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }

    try:
        response = requests.patch(
            url,
            headers=headers,
            data=json.dumps(payload),
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise WorkOrderNotFound(
            f"Error, could not complete work order: {e.response.status_code} - {e.response.content}"
        )
    except requests.exceptions.RequestException as e:
        raise WorkOrderNotFound(f"Error, could not complete work order: {str(e)}")

    return response.json()


def work_order_add_checklist(
    service_call_id: int, checklist_id: int, asset_id: int
) -> dict:
    """
    Add a single checklist to an existing service call.

    Args:
        service_call_id (int): User facing ID of service call.
        checklist_id (int): Internal ID of checklist to link with service call.
        asset_id (int): Internal ID of asset to assign this checklist to.

    Raises:
        ChecklistLinkError: General error thrown when link checklist API call fails.
    """

    url = (
        os.environ["EZO_BASE_URL"]
        + "tasks/"
        + str(service_call_id)
        + "/add_checklists.json"
    )
    data = {"checklist_ids": str(checklist_id), "asset_id": str(asset_id)}

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data=data,
            timeout=60,
        )
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        raise ChecklistLinkError(
            f"Error, could not link checklist to service call: {e.response.status_code} - {e.response.content}"
        )

    except requests.exceptions.RequestException as e:
        raise ChecklistLinkError(
            f"Error, could not link checklist to service call: {e}"
        )

    return response.json()


# TODO Add checklist (/tasks/{work_order_id}/add_checklists.json Not documented for some reason)


@Decorators.check_env_vars
def work_order_remove_checklist(work_order_id: int, checklist_id: int) -> dict:
    """
    Removes a checklist from a work order.
    """

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
        "Cache-Control": "no-cache",
        "Host": f"{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Content-Length": "75",
    }
    url = f"{os.environ['EZO_BASE_URL']}api/v2/work_orders/{work_order_id}/remove_checklist"
    payload = {"work_order": {"checklist_id": checklist_id}}

    try:
        response = requests.delete(
            url,
            headers=headers,
            data=json.dumps(payload),
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise WorkOrderNotFound(
            f"Error, could not remove checklist from work order: {e.response.status_code} - {e.response.content}"
        )
    except requests.exceptions.RequestException as e:
        raise WorkOrderNotFound(
            f"Error, could not remove checklist from work order: {str(e)}"
        )

    return response.json()
