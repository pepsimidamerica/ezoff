"""
This module contains functions for interacting with members/roles/user setup in EZOfficeInventory.
"""

import logging
import os

from ezoff._helpers import (
    _get_ezo_headers,
    _get_paginated,
    _http_request,
    _parse_response,
)
from ezoff.data_model import CustomRole, Member, MemberCreate, Team, UserListing

logger = logging.getLogger(__name__)


def member_create(
    first_name: str | None,
    last_name: str,
    role_id: int,
    email: str,
    employee_identification_number: str | None = None,
    description: str | None = None,
    department: str | None = None,
    team_ids: list[int] | None = None,
    user_listing_id: int | None = None,
    work_location: int | None = None,
    login_enabled: bool | None = None,
    subscribed_to_emails: bool | None = None,
    skip_confirmation_email: bool | None = None,
    address_name: str | None = None,
    address: str | None = None,
    address_line_2: str | None = None,
    city: str | None = None,
    state: str | None = None,
    zip_code: str | None = None,
    country: str | None = None,
    fax: str | None = None,
    phone_number: str | None = None,
    image_url: str | None = None,
    custom_fields: list[dict] | None = None,
) -> Member | None:
    """
    Create a new member.

    :param first_name: First name of the member
    :type first_name: str | None
    :param last_name: Last name of the member
    :type last_name: str
    :param role_id: Role ID for the member, corresponds to what permissions they have
    :type role_id: int
    :param email: Email address of the member. Note: must be unique.
    :type email: str
    :param employee_identification_number: Employee ID number for the member
    :type employee_identification_number: str, optional
    :param description: Description of the member
    :type description: str, optional
    :param department: Department the member belongs to
    :type department: str, optional
    :param team_ids: List of team IDs to assign the member to
    :type team_ids: list[int], optional
    :param user_listing_id: User listing ID to associate with the member
    :type user_listing_id: int, optional
    :param login_enabled: Whether the member can log in. Non-login members can be used for non-employees or simply tracking purposes.
    :type login_enabled: bool, optional
    :param subscribed_to_emails: Whether the member is subscribed to emails
    :type subscribed_to_emails: bool, optional
    :param skip_confirmation_email: Whether to skip sending a confirmation email
    :type skip_confirmation_email: bool, optional
    :param address_name: Name associated with the member's address
    :type address_name: str, optional
    :param address: Address of the member
    :type address: str, optional
    :param address_line_2: Second line of the member's address
    :type address_line_2: str, optional
    :param city: City of the member's address
    :type city: str, optional
    :param state: State of the member's address
    :type state: str, optional
    :param zip_code: Zip code of the member's address
    :type zip_code: str, optional
    :param country: Country of the member's address
    :type country: str, optional
    :param fax: Fax number of the member
    :type fax: str, optional
    :param phone_number: Phone number of the member
    :type phone_number: str, optional
    :param image_url: URL of the member's image
    :type image_url: str, optional
    :param custom_fields: List of custom fields for the member
    :type custom_fields: list[dict], optional
    :return: The created member, or None if creation failed
    :rtype: Member | None
    """
    params = {k: v for k, v in locals().items() if v is not None}

    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/members",
        json={"member": params},
        context="Member Create",
    )

    return _parse_response(
        response=response,
        key="member",
        model=Member,
        success_status_codes=[200],
    )


def members_create(members: list[MemberCreate]) -> list[Member] | None:
    """
    Creates new members in bulk.

    :param members: A list of MemberCreate objects representing the members to create. Same fields present in member_create()
    :return: The list of created Members if successful, else None
    :rtype: list[Member]
    """
    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/members/bulk_create",
        json={"members": [member.model_dump(exclude_none=True) for member in members]},
        context="Members Create",
    )

    if response.status_code == 200 and "members" in response.json():
        return [Member(**x) for x in response.json()["members"]]

    return None


def member_return(member_id: int) -> Member | None:
    """
    Returns a particular member.

    :param member_id: The ID of the member to return
    :return: The member if found, else None
    :rtype: Member | None
    """
    response = _http_request(
        method="GET",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/members/{member_id}",
        context="Member Return",
    )

    return _parse_response(
        response=response,
        key="member",
        model=Member,
        success_status_codes=[200],
    )


def members_return(filter: dict | None = None) -> list[Member]:
    """
    Returns all members. Optionally, filter by one or more member fields.

    :param filter:  Dictionary of member fields and the values to filter results by.
    :type filter: dict, optional
    :return: List of members
    :rtype: list[Member]
    """
    query_params = {}
    if filter:
        invalid = filter.keys() - (
            Member.model_fields.keys()
            | {
                "all",
                "login_enabled",
                "external",
                "inactive",
                "inactive_members_with_items",
                "inactive_members_with_pending_associations",
                "location_id",
            }
        )
        if invalid:
            raise ValueError(
                f"'{next(iter(invalid))}' is not a valid field for a member."
            )
        query_params = {f"filters[{k}]": v for k, v in filter.items()}

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/members"
    if query_params:
        url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])

    all_members = _get_paginated(
        url=url,
        headers=_get_ezo_headers(),
        results_key="members",
        context="members return",
    )

    return [Member(**x) for x in all_members]


def member_update(member_id: int, update_data: dict) -> Member | None:
    """
    Updates a particular member.

    :param member_id: The ID of the member to update
    :param update_data: Dictionary of fields to update on the member. See Member model for valid fields.
    :return: The updated member if successful, else None
    :rtype: Member | None
    """
    invalid = update_data.keys() - Member.model_fields.keys()
    if invalid:
        raise ValueError(f"Invalid fields: {', '.join(invalid)}")

    response = _http_request(
        method="PATCH",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/members/{member_id}",
        headers=_get_ezo_headers(),
        json={"member": update_data},
        context="Member Update",
    )

    return _parse_response(
        response=response,
        key="member",
        model=Member,
        success_status_codes=[200],
    )


def member_activate(member_id: int) -> Member | None:
    """
    Activates a particular member.

    :param member_id: The ID of the member to activate
    :return: The activated member if successful, else None
    :rtype: Member | None
    """
    response = _http_request(
        method="PUT",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/members/{member_id}/activate",
        context="Member Activate",
    )

    return _parse_response(
        response=response,
        key="member",
        model=Member,
        success_status_codes=[200],
    )


def member_deactivate(member_id: int) -> Member | None:
    """
    Deactivates a particular member.

    :param member_id: The ID of the member to deactivate
    :return: The deactivated member if successful, else None
    :rtype: Member | None
    """
    response = _http_request(
        method="PUT",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/members/{member_id}/deactivate",
        context="Member Deactivate",
    )

    return _parse_response(
        response=response,
        key="member",
        model=Member,
        success_status_codes=[200],
    )


def custom_roles_return() -> list[CustomRole]:
    """
    Get all custom roles.

    :return: List of custom roles
    :rtype: list[CustomRole]
    """
    all_custom_roles = _get_paginated(
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/custom_roles",
        headers=_get_ezo_headers(),
        results_key="custom_roles",
        context="Custom Roles Return",
    )

    return [CustomRole(**x) for x in all_custom_roles]


def custom_role_update(custom_role_id: int, update_data: dict) -> CustomRole | None:
    """
    Updates a particular custom role.

    :param custom_role_id: The ID of the custom role to update
    :param update_data: Dictionary of fields to update on the custom role. See CustomRole model for valid fields.
    :return: The updated custom role if successful, else None
    :rtype: CustomRole | None
    """
    for field in update_data:
        if field not in CustomRole.model_fields:
            raise ValueError(f"'{field}' is not a valid field for a custom role.")

    response = _http_request(
        method="PATCH",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/custom_roles/{custom_role_id}",
        json={"custom_role": update_data},
        context="Custom Role Update",
    )

    return _parse_response(
        response=response,
        key="custom_role",
        model=CustomRole,
        success_status_codes=[200],
    )


def teams_return() -> list[Team]:
    """
    Get all teams.

    :return: List of teams
    :rtype: list[Team]
    """
    all_teams = _get_paginated(
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/teams",
        headers=_get_ezo_headers(),
        results_key="teams",
        context="Teams Return",
    )

    return [Team(**x) for x in all_teams]


def user_listings_return() -> list[UserListing]:
    """
    Returns all user listings.
    Note: This API endpoint is documented, but I only ever get a 403 when
    trying to use it. Even though obviously using the API key. Not sure.

    :return: List of user listings
    :rtype: list[UserListing]
    """
    all_user_listings = _get_paginated(
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/user_listings",
        headers=_get_ezo_headers(),
        results_key="user_listings",
        context="User Listings Return",
    )

    return [UserListing(**x) for x in all_user_listings]
