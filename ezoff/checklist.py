"""
This module contains functions to interact with checklists in EZOfficeInventory.
"""

import os
from typing import Literal, Optional
from datetime import date, datetime
import requests
from pprint import pprint

from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from .exceptions import *


@Decorators.check_env_vars
def get_checklists() -> dict:
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
