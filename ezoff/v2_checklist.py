"""
This module contains functions to interact with the checklist v2 API in EZOfficeInventory.
"""

import os
from typing import Literal, Optional
from datetime import date, datetime
import requests
from pprint import pprint

from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from .exceptions import *
from .data_model import *

@Decorators.check_env_vars
def get_checklists_v2_pd() -> Dict[str, ChecklistV2]:
    """
    Get all checklists from EZ Office V2 API Call.
    Returns dictionary of pydantic objects keyed by checklist id.
    """
    checklist_dict = get_checklists_v2()
    checklists = {}

    for c in checklist_dict:
        checklist = checklist_dict[c]
        try:
            checklists[checklist['id']] = ChecklistV2(**checklist)

        except Exception as e:
            print(str(e))
            pprint(checklist)
            exit(0)

    return checklists


@Decorators.check_env_vars
def get_checklists_v2() -> dict:
    """
    Get all checklists from EZ Office. V2 API Call.

    https://pepsimidamerica.ezofficeinventory.com/api/v2/checklists?page=1&per_page=100
    """

    url = os.environ["EZO_BASE_URL"] + "/api/v2/checklists"

    page = 1
    per_page = 100
    all_checklists = {}

    while True:
        params = {"page": page, "per_page": per_page}

        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params=params,
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            raise Exception(
                f"Error, could not get checklists: {e.response.status_code} - {e.response.content}"
            )
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error, could not get checklists: {e}")

        data = response.json()

        if "checklists" not in data:
            raise NoDataReturned(f"No checklists found: {response.content}")

        for checklist in data["checklists"]:
            all_checklists[checklist["id"]] = checklist

        metadata = data["metadata"]

        if "total_pages" not in metadata:
            break

        if page >= metadata["total_pages"]:
            break

        page += 1

    return all_checklists
