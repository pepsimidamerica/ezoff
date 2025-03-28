"""
This module contains functions to interact with the work orders v2 API in EZOfficeInventory.
"""

import os
from typing import Literal, Optional, List
from datetime import date, datetime
import requests
from pprint import pprint

from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from .exceptions import *
from .data_model import *

import pickle


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
            print('Error in get_work_orders_v2_pd()')
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
    if filter is not None:
        # Remove any keys that are not valid
        valid_keys = [
            "filters[priority]",
            "filters[created_on]",
            "filters[due_date]",
            "filters[expected_start_date]",
            "filters[repetition_end_date]",
            "filters[repetition_start_date]",
            "filters[state]",
            "filters[assigned_to_type]",
            "filters[assigned_to_id]",
            "filters[created_by_id]",
            "filters[reviewer_id]",
            "filters[supervisor_id]",
            "filters[asset_id]",
            "filters[work_type_id]",
            "filters[preventive]",
            "filters[recurring]",
            "filters[review_pending_on_me]",
            "filters[scheduled]",
            "filters[location_id]",
        ]

        filter = {k: v for k, v in filter.items() if k in valid_keys}

    url = os.environ["EZO_BASE_URL"] + "api/v2/work_orders"

    print(f"Filter: {filter}")

    page = 1
    per_page = 100
    all_work_orders = []

    while True:
        params = {"page": page, "per_page": per_page}

        if filter is not None:
            params.update(filter)

        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
            "Cache-Control": "no-cache",
            "Host": "pepsimidamerica.ezofficeinventory.com",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

        try:
            response = _fetch_page(
                url,
                headers=headers,
                params=params,
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

    return WorkOrderV2(**wo_dict['work_order'])


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
        raise Exception(
            f"Error, could not get work order details: {e.response.status_code} - {e.response.content}"
        )
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error, could not get work order details: {e}")

    return response.json()