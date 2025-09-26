"""
This module contains functions for interacting with members/roles/user setup in EZOfficeInventory
"""

import logging
import os
import time
from typing import Optional
import requests
from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff.data_model import CustomRole, Member, MemberCreate, Team, UserListing
from ezoff.exceptions import NoDataReturned

logger = logging.getLogger(__name__)


@Decorators.check_env_vars
def members_return_v1(filter: Optional[dict]) -> list[dict]:
    """
    Get members from EZOfficeInventory
    Optionally filter by email, employee_identification_number, or status
    https://ezo.io/ezofficeinventory/developers/#api-retrieve-members
    """

    if filter is not None:
        if "filter" not in filter or "filter_val" not in filter:
            raise ValueError("filter must have 'filter' and 'filter_val' keys")
        
        if filter["filter"] not in [
            "email",
            "employee_identification_number",
            "status",
        ]:
            raise ValueError(
                "filter['filter'] must be one of 'email', 'employee_identification_number', 'status'"
            )

    # url = os.environ["EZO_BASE_URL"] + "members.api"
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/members.api"

    page = 1
    all_members = []

    while True:
        params = {"page": page, "include_custom_fields": "true"}
        if filter is not None:
            params.update(filter)

        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params=params,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get members: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get members: {e}")
            raise

        data = response.json()
        if "members" not in data:
            logger.error(f"Error, could not get members: {data}")
            raise Exception(f"Error, could not get members: {response.content}")

        all_members.extend(data["members"])

        if "total_pages" not in data:
            break

        if page >= data["total_pages"]:
            break

        page += 1

        # Potentially running into rate limiting issues with this endpoint
        # Sleep for a second to avoid this
        time.sleep(1)

    return all_members
