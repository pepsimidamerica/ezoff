"""
This module contains functions to interact with the members v2 API in EZOfficeInventory.
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
def get_members_v2_pd(filter: Optional[dict]) -> Dict[int, MemberV2]:
    """
    Get filtered work orders.
    Returns dictionary of pydantic objects keyed by work order id.
    """
    member_dict = get_members_v2(filter=filter)
    members = {}

    for member in member_dict:
        try:
            members[member["id"]] = MemberV2(**member)

        except Exception as e:
            print(str(e))
            pprint(member)
            exit(0)

    return members


@_basic_retry
@Decorators.check_env_vars
def get_members_v2(filter: Optional[dict]) -> List[dict]:
    """
    Get filtered members.
    """
    if filter is not None:
        # Remove any keys that are not valid
        valid_keys = [
            "filters[creation_source]",
            "filters[last_sync_source]",
            "filters[department]",
            "filters[manager_id]",
            "filters[role_id]",
            "filters[team_id]",
            "filters[location_id]",
            "filters[all]",
            "filters[login_enabled]",
            "filters[external]",
            "filters[inactive]",
            "filters[inactive_members_with_items]",
            "filters[inactive_members_with_pending_associations]",
            "filters[off_boarding_overdue]",
            "filters[off_boarding_due_in]",
            "filters[created_during]",
            "filters[last_logged_in_during]",
            "filters[synced_during]",
        ]
        filter = {k: v for k, v in filter.items() if k in valid_keys}

    url = os.environ["EZO_BASE_URL"] + "api/v2/members"
    page = 1
    per_page = 100
    members = []

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
                f"Error, could not get members: {e.response.status_code} - {e.response.content}"
            )
        except requests.exceptions.RequestException as e:
            raise WorkOrderNotFound(f"Error, could not get members: {e}")

        data = response.json()

        if "members" not in data:
            raise NoDataReturned(f"No members found: {response.content}")

        members = members + data["members"]

        if "metadata" not in data or "total_pages" not in data["metadata"]:
            break

        if page >= data["metadata"]["total_pages"]:
            break

        page += 1

    return members


@Decorators.check_env_vars
def get_member_v2_pd(member_id: int) -> MemberV2:
    """
    Get a single member.
    Returns a pydantic object.
    """
    mem_dict = get_member_v2(member_id=member_id)

    return MemberV2(**mem_dict["member"])


@_basic_retry
@Decorators.check_env_vars
def get_member_v2(member_id: int) -> dict:
    """
    Get a single member.
    Returns a pydantic object.
    """

    # 'API User' is invalid in the member API. Hardcode response for API User's member id.
    if member_id == 238602:
        return {
            "member": {
                "id": 238602,
                "status": 1,
                "created_at": datetime.now(),
                "full_name": "API User",
                "email": "clambert@pepsimidamerica.com",
            }
        }

    url = os.environ["EZO_BASE_URL"] + f"api/v2/members/{member_id}"
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
            f"Error, could not get member details: {e.response.status_code} - {e.response.content}"
        )
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error, could not get member details: {e}")

    return response.json()
