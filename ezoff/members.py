"""
This module contains functions for interacting with members/roles/user setup in EZOfficeInventory
"""

import logging
import os
import time

import requests
from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff.data_model import CustomRole, Member, MemberCreate, Team
from ezoff.exceptions import NoDataReturned

logger = logging.getLogger(__name__)


@Decorators.check_env_vars
def member_create(
    first_name: str | None,
    last_name: str,
    role_id: int,
    email: str,
    employee_identification_number: str | None,
    team_ids: list[int] | None,
    user_listing_id: int | None,
    login_enabled: bool | None,
    subscribed_to_emails: bool | None,
    skip_confirmation_email: bool | None,
    address_name: str | None,
    address: str | None,
    address_line_2: str | None,
    city: str | None,
    state: str | None,
    zip_code: str | None,
    country: str | None,
    fax: str | None,
    phone_number: str | None,
    image_url: str | None,
    custom_fields: list[dict] | None,
) -> Member | None:
    """
    Create a new member.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/members"

    params = {k: v for k, v in locals().items() if v is not None}

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data={"member": params},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error creating member: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error creating member: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating member: {e}")
        raise Exception(f"Error creating member: {e}")

    if response.status_code == 200:
        return Member(**response.json()["member"])
    else:
        return None


@Decorators.check_env_vars
def members_create(members: list[MemberCreate]) -> list[Member] | None:
    """
    Creates new members in bulk.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/members/bulk_create"

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data={
                "members": [member.model_dump(exclude_none=True) for member in members]
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error creating members: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error creating members: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating member: {e}")
        raise Exception(f"Error creating member: {e}")

    if response.status_code == 200:
        return [Member(**x) for x in response.json()["members"]]
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def member_return(member_id: int) -> Member | None:
    """
    Returns a particular member.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/members/{member_id}"

    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
        "Cache-Control": "no-cache",
        "Host": f"{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com",
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
        logger.error(
            f"Error getting member: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error getting member: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting member: {e}")
        raise Exception(f"Error getting member: {e}")

    if response.status_code == 200:
        return Member(**response.json()["member"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def members_return(filter: dict | None = None) -> list[Member]:
    """
    Returns all members. Optionally, filter by
    """

    if filter:
        for field in filter:
            if field not in Member.model_fields:
                raise ValueError(f"'{field}' is not a valid field for a member.")
            filter = {"filters": filter}
    else:
        filter = None

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/members"

    all_members = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={
                    "Accept": "application/json",
                    "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                    "Cache-Control": "no-cache",
                    "Host": f"{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json",
                },
                data=filter,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error getting members: {e.response.status_code} - {e.response.content}"
            )
            raise Exception(
                f"Error creating members: {e.response.status_code} - {e.response.content}"
            )
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting member: {e}")
            raise Exception(f"Error getting member: {e}")

        data = response.json()

        if "members" not in data:
            raise NoDataReturned(f"No members found: {response.content}")

        all_members.extend(data["members"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [Member(**x) for x in all_members]


@Decorators.check_env_vars
def member_update(member_id: int, update_data: dict) -> Member | None:
    """
    Updates a particular member.
    """

    for field in update_data:
        if field not in Member.model_fields:
            raise ValueError(f"'{field}' is not a valid field for a member.")

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/members/{member_id}"

    try:
        response = requests.patch(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data={"member": update_data},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error updating members: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error updating members: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error updating member: {e}")
        raise Exception(f"Error updating member: {e}")

    if response.status_code == 200:
        return Member(**response.json()["member"])
    else:
        return None


@Decorators.check_env_vars
def member_activate(member_id: int) -> Member | None:
    """
    Activates a particular member.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/members/{member_id}/activate"

    try:
        response = requests.put(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error activating member: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error activating member: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error activating member: {e}")
        raise Exception(f"Error activating member: {e}")

    if response.status_code == 200:
        return Member(**response.json()["member"])
    else:
        return None


@Decorators.check_env_vars
def member_deactivate(member_id: int) -> Member | None:
    """
    Deactivates a particular member.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/members/{member_id}/deactivate"

    try:
        response = requests.put(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error deactivating member: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error deactivating member: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error deactivating member: {e}")
        raise Exception(f"Error deactivating member: {e}")

    if response.status_code == 200:
        return Member(**response.json()["member"])
    else:
        return None


@Decorators.check_env_vars
def custom_roles_return() -> list[CustomRole]:
    """
    Get all custom roles
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/custom_roles"

    all_custom_roles = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get custom roles: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting custom roles: {e}")
            raise

        data = response.json()

        if "custom_roles" not in data:
            raise NoDataReturned(f"No custom roles found: {response.content}")

        all_custom_roles.extend(data["custom_roles"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [CustomRole(**x) for x in all_custom_roles]


@Decorators.check_env_vars
def custom_role_update(custom_role_id: int, update_data) -> CustomRole | None:
    """
    Updates a particular custom role.
    """

    for field in update_data:
        if field not in CustomRole.model_fields:
            raise ValueError(f"'{field}' is not a valid field for a custom role.")

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/custom_roles/{custom_role_id}"

    try:
        response = requests.patch(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data={"custom_role": update_data},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error updating custom role: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error updating custom role: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error updating custom role: {e}")
        raise Exception(f"Error updating custom role: {e}")

    if response.status_code == 200:
        return CustomRole(**response.json()["custom_role"])
    else:
        return None


@Decorators.check_env_vars
def teams_return() -> list[Team]:
    """
    Get all teams
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/teams"

    all_teams = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, getting teams: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting teams: {e}")
            raise

        data = response.json()

        if "teams" not in data:
            raise NoDataReturned(f"No teams found: {response.content}")

        all_teams.extend(data["teams"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [Team(**x) for x in all_teams]
