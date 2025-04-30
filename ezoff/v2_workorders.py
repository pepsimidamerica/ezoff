"""
This module contains functions to interact with the work orders v2 API in EZOfficeInventory.
"""

import os
from typing import Literal, Optional, List
from datetime import date, datetime
import requests
from pprint import pprint
import json

from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from .exceptions import *
from .data_model import *


@Decorators.check_env_vars
def add_work_order_component_v2(
    work_order_id: int, components: List[Component]
) -> dict:
    """
    Adds a component to a work order.
    """

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
        "Cache-Control": "no-cache",
        "Host": "pepsimidamerica.ezofficeinventory.com",
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
def complete_work_order_v2(work_order_id: int, completed_on_dttm: datetime) -> dict:
    """
    Completes a work order.
    """

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
        "Cache-Control": "no-cache",
        "Host": "pepsimidamerica.ezofficeinventory.com",
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


@Decorators.check_env_vars
def create_work_order_v2(work_order: dict) -> dict:
    """
    Creates a work order.
    """

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
        "Cache-Control": "no-cache",
        "Host": "pepsimidamerica.ezofficeinventory.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Content-Length": "75",
    }
    url = f"{os.environ['EZO_BASE_URL']}api/v2/work_orders"
    payload = {"work_order": work_order}

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
def get_work_orders_v2_pd(filter: Optional[dict]) -> Dict[int, WorkOrderV2]:
    """
    Get filtered work orders.
    Returns dictionary of pydantic objects keyed by work order id.
    """
    wo_dict = get_work_orders_v2(filter=filter)
    work_orders = {}

    for wo in wo_dict:
        try:
            work_orders[wo["id"]] = WorkOrderV2(**wo)

        except Exception as e:
            print("Error in get_work_orders_v2_pd()")
            print(str(e))
            pprint(wo)
            exit(0)

    return work_orders


@_basic_retry
@Decorators.check_env_vars
def get_work_orders_v2(filter: Optional[dict]) -> List[dict]:
    """
    Get filtered work orders.
    """

    url = os.environ["EZO_BASE_URL"] + "api/v2/work_orders"
    page = 1
    all_work_orders = []

    # Add the 'filter' key if it doesn't already exist in the filter dict.
    if filter is not None and "filters" not in filter:
        filter = {"filters": filter}

    while True:
        params = {"page": page}

        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
            "Cache-Control": "no-cache",
            "Host": "pepsimidamerica.ezofficeinventory.com",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
        }

        try:
            response = _fetch_page(
                url,
                headers=headers,
                params=params,
                data=json.dumps(filter),
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            raise WorkOrderNotFound(
                f"Error, could not get work orders: {e.response.status_code} - {e.response.content}"
            )
        except requests.exceptions.RequestException as e:
            raise WorkOrderNotFound(f"Error, could not get work orders: {e}")

        data = response.json()

        if "tasks" not in data:
            raise NoDataReturned(f"No work orders found: {response.content}")

        all_work_orders = all_work_orders + data["tasks"]

        if "metadata" not in data or "total_pages" not in data["metadata"]:
            break

        if page >= data["metadata"]["total_pages"]:
            break

        page += 1

    return all_work_orders


@Decorators.check_env_vars
def get_work_order_v2_pd(work_order_id: int) -> WorkOrderV2:
    """
    Get a single work order.
    Returns a pydantic object.
    """
    wo_dict = get_work_order_v2(work_order_id=work_order_id)

    return WorkOrderV2(**wo_dict["work_order"])


@_basic_retry
@Decorators.check_env_vars
def get_work_order_v2(work_order_id: int) -> dict:
    """
    Get a single work order.
    """
    url = os.environ["EZO_BASE_URL"] + f"api/v2/work_orders/{work_order_id}"
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
        "Cache-Control": "no-cache",
        "Host": "pepsimidamerica.ezofficeinventory.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise WorkOrderNotFound(
            f"Error, could not get work order details: {e.response.status_code} - {e.response.content}"
        )
    except requests.exceptions.RequestException as e:
        raise WorkOrderNotFound(f"Error, could not get work order details: {e}")

    return response.json()


@Decorators.check_env_vars
def remove_checklist_work_order_v2(work_order_id: int, checklist_id: int) -> dict:
    """
    Removes a checklist from a work order.
    """

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
        "Cache-Control": "no-cache",
        "Host": "pepsimidamerica.ezofficeinventory.com",
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


@Decorators.check_env_vars
def update_work_order_v2(work_order_id: int, work_order: dict) -> dict:
    """
    Updates a work order.
    """

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
        "Cache-Control": "no-cache",
        "Host": "pepsimidamerica.ezofficeinventory.com",
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
