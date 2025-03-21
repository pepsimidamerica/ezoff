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
    # use_saved = True

    # if use_saved:
    #     with open('tasks.pkl', 'rb') as f:
    #         wo_dict = pickle.load(f)

    # else:
    #     wo_dict = get_work_orders_v2(filter=filter)      
    #     with open('tasks.pkl', 'wb') as f:
    #         pickle.dump(wo_dict, f)

    wo_dict = get_work_orders_v2(filter=filter)
    work_orders = {}

    for wo in wo_dict:
        try:
            work_orders[wo['id']] = WorkOrderV2(**wo)

        except Exception as e:
            print(str(e))
            pprint(wo)
            exit(0)

    return work_orders


@Decorators.check_env_vars
def get_work_orders_v2(filter: Optional[dict]) -> List[dict]:
    """
    Get filtered work orders.
    """

    if filter is not None:
        # Remove any keys that are not valid
        valid_keys = [
            "filters[reviewer_id]",
            "filters[State]",
            "filters[priority]",
            "filters[assigned_to_id]",
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
