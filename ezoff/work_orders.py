"""
This module contains functions to interact with work orders in EZOfficeInventory.

Note: API will inconsistently use a 'tasks' or 'work_orders' key when returning
info from these endpoints. Each endpoint just needs to be checked which it is.
"""

import logging
import os
import time
from datetime import datetime
from typing import Literal

import requests
from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff.data_model import (
    Component,
    LinkedInventory,
    ResponseMessages,
    WorkLog,
    WorkOrder,
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

    TODO v1

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
    Get all work orders. Optionally filter using one or more work order fields.
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


@Decorators.check_env_vars
def work_orders_search(search_term: str) -> list[WorkOrder]:
    """
    Search for work orders.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/search"

    all_work_orders = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params={"search": search_term},
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

        if "work_orders" not in data:
            logger.error(f"Error, could not get work orders: {response.content}")
            raise Exception(f"Error, could not get work orders: {response.content}")

        all_work_orders.extend(data["work_orders"])

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


@Decorators.check_env_vars
def work_order_linked_work_orders_return(work_order_id: int) -> list[WorkOrder]:
    """
    Returns work orders that are linked to a particular work order.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/linked_work_orders"

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


@Decorators.check_env_vars
def work_order_linked_inventory_return(work_order_id: int) -> list[LinkedInventory]:
    """
    Returns list of inventory items linked to a particular work order.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/linked_inventory_items"

    all_inven = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                data=filter,
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get linked inventory: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get linked inventory: {e}")
            raise

        data = response.json()

        if "linked_inventory_items" not in data:
            logger.error(f"Error, could not get linked inventory: {response.content}")
            raise Exception(
                f"Error, could not get linked inventory: {response.content}"
            )

        all_inven.extend(data["linked_inventory_items"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [LinkedInventory(**x) for x in all_inven]


@_basic_retry
@Decorators.check_env_vars
def work_order_types_return() -> list[dict]:
    """
    Get work order types
    TODO v1
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


@Decorators.check_env_vars
def work_order_work_logs_return(work_order_id: int) -> list[WorkLog]:
    """
    Returns a list of work logs attached to a particular work order.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}"

    all_logs = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                data=filter,
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get logs: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get logs: {e}")
            raise

        data = response.json()

        if "work_logs" not in data:
            logger.error(f"Error, could not get logs: {response.content}")
            raise Exception(f"Error, could not get logs: {response.content}")

        all_logs.extend(data["work_logs"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [WorkLog(**x) for x in all_logs]


@Decorators.check_env_vars
def work_order_update(work_order_id: int, update_data: dict) -> WorkOrder | None:
    """
    Updates a work order.
    """

    for field in update_data:
        if field not in WorkOrder.model_fields:
            raise ValueError(f"'{field}' is not a valid field for a group.")

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/work_logs"

    try:
        response = requests.put(
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
            data={"work_order": update_data},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error updating work order: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error updating work order: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error updating work order: {e}")
        raise Exception(f"Error updating work order: {e}")

    if response.status_code == 200 and "work_order" in response.json():
        return WorkOrder(**response.json()["work_order"])
    else:
        return None


@Decorators.check_env_vars
def work_order_add_work_log(
    work_order_id: int,
    started_on_dttm: datetime,
    ended_on_dttm: datetime,
    hours_spent: float = 1,
    cost_per_hour: float = 0,
    note: str | None = None,
    custom_attributes: dict | None = None,
) -> dict:
    """
    Add a work log to a particular work order
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/tasks/{work_order_id}/task_work_logs.json"

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data={
                "task_work_log": {
                    "resource_id": 2657,  # Is misc always going to be 2657?
                    "rate_type": "standard",
                    "cost_per_hour": cost_per_hour,
                    "time_spent": hours_spent,
                    "total_cost": cost_per_hour * hours_spent,  # Is this needed?
                    "resource_type": "MiscellaneousComponent",
                    "description": note,
                    "custom_attributes": custom_attributes,
                },
                "started_on_date": started_on_dttm.strftime("%m/%d/%Y"),
                "started_on_time": started_on_dttm.strftime("%I:%M %p"),
                "ended_on_date": ended_on_dttm.strftime("%m/%d/%Y"),
                "ended_on_time": ended_on_dttm.strftime("%I:%M %p"),
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error adding work log: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error adding work log: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error adding work log: {e}")
        raise Exception(f"Error adding work log: {e}")

    return response.json()


@Decorators.check_env_vars
def work_order_add_linked_inv(
    work_order_id: int, inv_items: list[LinkedInventory]
) -> ResponseMessages | None:
    """
    Add linked inventory items to a work order
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/link_inventory"

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data={"work_order": {"linked_inventory_items": inv_items}},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error adding linked inv: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error adding linked inv: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error adding linked inv: {e}")
        raise Exception(f"Error adding linked inv: {e}")

    if response.status_code == 200 and "messages" in response.json():
        return ResponseMessages(**response.json()["messages"])
    else:
        return None


def work_order_routing_update(
    work_order_id: int,
    assigned_to_id: str,
    task_type_id: int,
    start_dttm: datetime,
    due_dttm: datetime,
    supervisor_id: str | None = None,
    reviewer_id: str | None = None,
) -> WorkOrder | None:
    """
    Update the assigned to user and start/end time of a workorder.
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
    # TODO Need to change the fields here
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

    result = work_order_update(work_order_id=work_order_id, update_data=filter)

    return result


@Decorators.check_env_vars
def work_order_add_component(
    work_order_id: int, components: list[Component]
) -> ResponseMessages | None:
    """
    Adds a component to a work order.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/add_components"

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
            data={"work_order": {"components": components}},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error adding component: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error adding component: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error adding component: {e}")
        raise Exception(f"Error adding component: {e}")

    if "messages" in response.json():
        return ResponseMessages(**response.json()["messages"])
    else:
        return None


@Decorators.check_env_vars
def work_order_mark_in_progress(
    work_order_id: int,
    start_work_on_all_assets: bool = True,
    actual_start_date: datetime | None = None,
    component_ids: list[int] | None = None,
    supervisor_id: int | None = None,
    assigned_to_id: int | None = None,
    assigned_to_type: str | None = None,
) -> ResponseMessages | None:
    """
    Start a work order
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/mark_in_progress"

    try:
        response = requests.patch(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data={
                "work_order": {
                    "start_work_on_all_assets": start_work_on_all_assets,
                    "actual_start_date": actual_start_date,
                    "component_ids": component_ids,
                    "supervisor_id": supervisor_id,
                    "assigned_to_id": assigned_to_id,
                    "assigned_to_type": assigned_to_type,
                }
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error marking in progress: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error marking in progress: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error marking in progress: {e}")
        raise Exception(f"Error marking in progress: {e}")

    if "messages" in response.json():
        return ResponseMessages(**response.json()["messages"])
    else:
        return None


@Decorators.check_env_vars
def work_order_mark_on_hold(
    work_order_id: int, comment: str | None = None
) -> ResponseMessages | None:
    """
    Start a particular work order
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/mark_on_hold"

    try:
        response = requests.patch(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data={
                "work_order": {
                    "comment": comment,
                }
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error marking on hold: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error marking on hold: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error marking on hold: {e}")
        raise Exception(f"Error marking on hold: {e}")

    if "messages" in response.json():
        return ResponseMessages(**response.json()["messages"])
    else:
        return None


@Decorators.check_env_vars
def work_order_mark_complete(
    work_order_id: int, completed_on_dttm: datetime
) -> ResponseMessages | None:
    """
    Completes a particular work order.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/mark_complete"

    try:
        response = requests.patch(
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
            data={
                "work_order": {
                    "completed_on_date": completed_on_dttm.strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    )
                }
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error marking complete: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error marking complete: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error marking complete: {e}")
        raise Exception(f"Error marking complete: {e}")

    if "messages" in response.json():
        return ResponseMessages(**response.json()["messages"])
    else:
        return None


@Decorators.check_env_vars
def work_order_add_linked_wo(
    work_order_id: int, wo_ids_to_link: list[int]
) -> ResponseMessages | None:
    """
    Links one or more work orders to a particular work order.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/link_work_orders"

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
            data={"work_order": {"work_order_ids": wo_ids_to_link}},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error linking work orders: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error linking work orders: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error linking work orders: {e}")
        raise Exception(f"Error linking work orders: {e}")

    if "messages" in response.json():
        return ResponseMessages(**response.json()["messages"])
    else:
        return None


@Decorators.check_env_vars
def work_order_remove_linked_wo(
    work_order_id: int, wo_ids_to_link: list[int]
) -> ResponseMessages | None:
    """
    Unlinks one or more work orders from a particular work order.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/unlink_work_orders"

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
            data={"work_order": {"work_order_ids": wo_ids_to_link}},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error unlinking work orders: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error unlinking work orders: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error unlinking work orders: {e}")
        raise Exception(f"Error unlinking work orders: {e}")

    if "messages" in response.json():
        return ResponseMessages(**response.json()["messages"])
    else:
        return None


@Decorators.check_env_vars
def work_order_add_linked_po(
    work_order_id: int, po_ids_to_link: list[int]
) -> ResponseMessages | None:
    """
    Links one or more purchase orders to a particular work order.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/link_po"

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
            data={"work_order": {"purchase_order_ids": po_ids_to_link}},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error linking purchase orders: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error linking purchase orders: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error linking purchase orders: {e}")
        raise Exception(f"Error linking purchase orders: {e}")

    if "messages" in response.json():
        return ResponseMessages(**response.json()["messages"])
    else:
        return None


@Decorators.check_env_vars
def work_order_remove_linked_po(
    work_order_id: int, po_ids_to_link: list[int]
) -> ResponseMessages | None:
    """
    Unlinks one or more purchase orders from a particular work order.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/unlink_po"

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
            data={"work_order": {"purchase_order_ids": po_ids_to_link}},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error unlinking purchase orders: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error unlinking purchase orders: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error unlinking purchase orders: {e}")
        raise Exception(f"Error unlinking purchase orders: {e}")

    if "messages" in response.json():
        return ResponseMessages(**response.json()["messages"])
    else:
        return None


@Decorators.check_env_vars
def work_orders_start_component_service(
    work_order_id: int, component_ids: list[int]
) -> ResponseMessages | None:
    """
    Starts service on one or more assets on a work order.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/start_components_service"

    try:
        response = requests.patch(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            data={"component_ids": component_ids},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error starting service: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error starting service: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error starting service: {e}")
        raise Exception(f"Error starting service: {e}")

    if "messages" in response.json():
        return ResponseMessages(**response.json()["messages"])
    else:
        return None


@Decorators.check_env_vars
def work_orders_end_component_service(
    work_order_id: int, component_ids: list[int]
) -> ResponseMessages | None:
    """
    Ends service on one or more assets on a work order.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/end_components_service"

    try:
        response = requests.patch(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            data={"component_ids": component_ids},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error ending service: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error ending service: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error ending service: {e}")
        raise Exception(f"Error ending service: {e}")

    if "messages" in response.json():
        return ResponseMessages(**response.json()["messages"])
    else:
        return None


def work_order_add_checklist(
    work_order_id: int, checklist_id: int, asset_id: int | None = None
) -> dict:
    """
    Add a single checklist to an existing work order.

    Args:
        work_order_id (int): User facing ID of work order.
        checklist_id (int): Internal ID of checklist to link with work order.
        asset_id (int): Internal ID of asset to assign this checklist to.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/tasks/{work_order_id}/add_checklists.json"

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data={"checklist_ids": str(checklist_id), "asset_id": str(asset_id)},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error adding checklist: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error adding checklist: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error adding checklist: {e}")
        raise Exception(f"Error adding checklist: {e}")

    return response.json()


def work_order_update_checklist(
    work_order_id: int,
    checklist_id: int,
    checklist_values: list[dict],
    asset_id: int | None = None,
) -> ResponseMessages | None:
    """
    Updates an existing checklist in a work order.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/update_work_order_checklist"

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data={
                "work_order": {
                    "checklist_id": checklist_id,
                    "asset_id": asset_id,
                    "checklist_values": checklist_values,
                }
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error updating checklist: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error updating checklist: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error updating checklist: {e}")
        raise Exception(f"Error updating checklist: {e}")

    if "messages" in response.json():
        return ResponseMessages(**response.json()["messages"])
    else:
        return None


@Decorators.check_env_vars
def work_order_remove_checklist(
    work_order_id: int, checklist_id: int
) -> ResponseMessages | None:
    """
    Removes a checklist from a work order.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/remove_checklist"

    try:
        response = requests.delete(
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
            data={"work_order": {"checklist_id": checklist_id}},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error removing checklist: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error removing checklist: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error removing checklist: {e}")
        raise Exception(f"Error removing checklist: {e}")

    if "messages" in response.json():
        return ResponseMessages(**response.json()["messages"])
    else:
        return None


@Decorators.check_env_vars
def work_order_delete(work_order_id: int) -> WorkOrder | None:
    """
    Deletes a particular work order.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}"

    try:
        response = requests.delete(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error deleting: {e.response.status_code} - {e.response.content}")
        raise Exception(
            f"Error deleting: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error deleting: {e}")
        raise Exception(f"Error deleting: {e}")

    if response.status_code == 200 and "work_order" in response.json():
        return WorkOrder(**response.json()["work_order"])
    else:
        return None


@Decorators.check_env_vars
def work_orders_delete(work_order_ids: list[int]) -> ResponseMessages | None:
    """
    Deletes multiple work orders.
    Note: Mass deletion must be enabled in company settings.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/mass_delete"

    try:
        response = requests.patch(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            data={"work_order": {"ids": work_order_ids}},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error deleting: {e.response.status_code} - {e.response.content}")
        raise Exception(
            f"Error deleting: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error deleting: {e}")
        raise Exception(f"Error deleting: {e}")

    if response.status_code == 200 and "messages" in response.json():
        return ResponseMessages(**response.json()["messages"])
    else:
        return None
