"""
Covers everything related to groups and subgroups in EZOfficeInventory.

TODO: Add group depreciation rates
"""

import logging
import os
from typing import Literal

from ezoff._helpers import (
    _get_ezo_headers,
    _get_paginated,
    _http_request,
    _parse_response,
)
from ezoff.data_model import DepreciationRate, Group, ResponseMessages

logger = logging.getLogger(__name__)


def group_create(
    name: str,
    description: str | None = None,
    asset_depreciation_mode: Literal["Useful Life", "Percentage"] | None = None,
    triage_completion_period: int | None = None,
    triage_completion_period_basis: (
        Literal["minutes", "hours", "days", "weeks", "months", "indefinite"] | None
    ) = None,
    allow_staff_to_set_checkout_duration: bool | None = None,
    staff_checkout_duration_months: int | None = None,
    staff_checkout_duration_weeks: int | None = None,
    staff_checkout_duration_days: int | None = None,
    staff_checkout_duration_hours: int | None = None,
    depreciation_rates: list[DepreciationRate] | None = None,
) -> Group | None:
    """
    Creates a new top-level group for items.

    :param name: Name of the group
    :type name: str
    :param description: Description of the group
    :type description: str, optional
    :param asset_depreciation_mode: The mode assets in the group will depreciate in, either 'Useful Life' or 'Percentage'
    :type asset_depreciation_mode: str, optional
    :param triage_completion_period: The time period within which the triage must be completed
    :type triage_completion_period: int, optional
    :param triage_completion_period_basis: The basis for the triage completion period, either 'minutes', 'hours', 'days', 'weeks', 'months', or 'indefinite'
    :type triage_completion_period_basis: str, optional
    :param allow_staff_to_set_checkout_duration: Whether staff are allowed to set checkout duration for assets in this group
    :type allow_staff_to_set_checkout_duration: bool, optional
    :param staff_checkout_duration_months: The number of months staff can set for checkout duration
    :type staff_checkout_duration_months: int, optional
    :param staff_checkout_duration_weeks: The number of weeks staff can set for checkout duration
    :type staff_checkout_duration_weeks: int, optional
    :param staff_checkout_duration_days: The number of days staff can set for checkout duration
    :type staff_checkout_duration_days: int, optional
    :param staff_checkout_duration_hours: The number of hours staff can set for checkout duration
    :type staff_checkout_duration_hours: int, optional
    :param depreciation_rates: A list of depreciation rates to apply to the group
    :type depreciation_rates: list of DepreciationRate, optional
    :return: The created group, or None if the creation failed
    :rtype: Group or None
    """
    params = {k: v for k, v in locals().items() if v is not None}

    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups",
        json={"group": params},
        context="Group Create",
    )

    return _parse_response(
        response=response,
        key="group",
        model=Group,
        success_status_codes=[200],
    )


def group_return(group_id: int) -> Group | None:
    """
    Returns a particular group.

    :param group_id: The ID of the group to return
    :type group_id: int
    :return: The group with the specified ID, or None if not found
    :rtype: Group or None
    """
    response = _http_request(
        method="GET",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups/{group_id}",
        context="Group Return",
    )

    return _parse_response(
        response=response,
        key="group",
        model=Group,
        success_status_codes=[200],
    )


def groups_return() -> list[Group]:
    """
    Returns all groups.

    :return: A list of all groups
    :rtype: list of Group
    """
    all_groups = _get_paginated(
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups",
        headers=_get_ezo_headers(),
        results_key="groups",
        context="Groups Return",
    )

    return [Group(**x) for x in all_groups]


def group_update(group_id: int, update_data: dict) -> Group | None:
    """
    Updates a particular group.

    :param group_id: The ID of the group to update
    :type group_id: int
    :param update_data: A dictionary of fields to update and their new values
    :type update_data: dict
    :return: The updated group, or None if the update failed
    :rtype: Group | None
    """
    for field in update_data:
        if field not in Group.model_fields:
            raise ValueError(f"'{field}' is not a valid field for a group.")

    response = _http_request(
        method="PATCH",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups/{group_id}",
        json={"group": update_data},
        context="Group Update",
    )

    return _parse_response(
        response=response,
        key="group",
        model=Group,
        success_status_codes=[200],
    )


def group_delete(group_id: int) -> ResponseMessages | None:
    """
    Deletes a particular group.

    :param group_id: The ID of the group to delete
    :type group_id: int
    :return: ResponseMessages object if there are any messages, else None.
    :rtype: ResponseMessages | None
    """
    response = _http_request(
        method="DELETE",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups/{group_id}",
        context="Group Delete",
    )

    return _parse_response(
        response=response,
        key="messages",
        model=ResponseMessages,
        success_status_codes=[200],
    )


def subgroup_create(
    parent_id: int,
    name: str,
    description: str | None = None,
    asset_depreciation_mode: Literal["Useful Life", "Percentage"] | None = None,
    triage_completion_period: int | None = None,
    triage_completion_period_basis: (
        Literal["minutes", "hours", "days", "weeks", "months", "indefinite"] | None
    ) = None,
    allow_staff_to_set_checkout_duration: bool | None = None,
    staff_checkout_duration_months: int | None = None,
    staff_checkout_duration_weeks: int | None = None,
    staff_checkout_duration_days: int | None = None,
    staff_checkout_duration_hours: int | None = None,
    depreciation_rates: list[DepreciationRate] | None = None,
) -> Group | None:
    """
    Creates a subgroup under a parent group.

    :param parent_id: The ID of the parent group under which to create the subgroup
    :type parent_id: int
    :param name: Name of the subgroup
    :type name: str
    :param description: Description of the subgroup
    :type description: str, optional
    :param asset_depreciation_mode: The mode assets in the subgroup will depreciate in, either 'Useful Life' or 'Percentage'
    :type asset_depreciation_mode: str, optional
    :param triage_completion_period: The time period within which the triage must be completed
    :type triage_completion_period: int, optional
    :param triage_completion_period_basis: The basis for the triage completion period, either 'minutes', 'hours', 'days', 'weeks', 'months', or 'indefinite'
    :type triage_completion_period_basis: str, optional
    :param allow_staff_to_set_checkout_duration: Whether staff are allowed to set checkout duration for assets in this subgroup
    :type allow_staff_to_set_checkout_duration: bool, optional
    :param staff_checkout_duration_months: The number of months staff can set for checkout duration
    :type staff_checkout_duration_months: int, optional
    :param staff_checkout_duration_weeks: The number of weeks staff can set for checkout duration
    :type staff_checkout_duration_weeks: int, optional
    :param staff_checkout_duration_days: The number of days staff can set for checkout duration
    :type staff_checkout_duration_days: int, optional
    :param staff_checkout_duration_hours: The number of hours staff can set for checkout duration
    :type staff_checkout_duration_hours: int, optional
    :param depreciation_rates: A list of depreciation rates to apply to the subgroup
    :type depreciation_rates: list of DepreciationRate, optional
    :return: The created subgroup, or None if the creation failed
    :rtype: Group | None
    """
    params = {k: v for k, v in locals().items() if v is not None}

    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups/{parent_id}/sub_groups",
        json={"sub_group": params},
        context="SubGroup Create",
    )

    return _parse_response(
        response=response,
        key="sub_group",
        model=Group,
        success_status_codes=[200],
    )


def subgroup_return(group_id: int, subgroup_id: int) -> Group | None:
    """
    Returns a particular subgroup.

    :param group_id: The ID of the parent group
    :type group_id: int
    :param subgroup_id: The ID of the subgroup to return
    :type subgroup_id: int
    :return: The subgroup with the specified ID, or None if not found
    :rtype: Group | None
    """
    response = _http_request(
        method="GET",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups/{group_id}/sub_groups/{subgroup_id}",
        context="SubGroup Return",
    )

    return _parse_response(
        response=response,
        key="sub_group",
        model=Group,
        success_status_codes=[200],
    )


def subgroups_return(group_id: int) -> list[Group]:
    """
    Get all subgroups under a particular group.

    :param group_id: Filter to get subgroups of a specific group
    :type group_id: int
    :return: A list of all subgroups under the specified group
    :rtype: list[Group]
    """
    all_subgroups = _get_paginated(
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups/{group_id}",
        headers=_get_ezo_headers(),
        results_key="sub_groups",
        context="SubGroups Return",
    )

    return [Group(**x) for x in all_subgroups]


def subgroup_update(group_id: int, subgroup_id: int, update_data: dict) -> Group | None:
    """
    Updates a particular subgroup.

    :param group_id: The ID of the parent group
    :type group_id: int
    :param subgroup_id: The ID of the subgroup to update
    :type subgroup_id: int
    :param update_data: A dictionary of fields to update and their new values
    :type update_data: dict
    :return: The updated subgroup, or None if the update failed
    :rtype: Group | None
    """
    for field in update_data:
        if field not in Group.model_fields:
            raise ValueError(f"'{field}' is not a valid field for a group.")

    response = _http_request(
        method="PATCH",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups/{group_id}/sub_groups/{subgroup_id}",
        json={"sub_group": update_data},
        context="SubGroup Update",
    )

    return _parse_response(
        response=response,
        key="sub_group",
        model=Group,
        success_status_codes=[200],
    )


def subgroup_delete(group_id: int, subgroup_id: int) -> ResponseMessages | None:
    """
    Deletes a particular subgroup.

    :param group_id: The ID of the parent group
    :type group_id: int
    :param subgroup_id: The ID of the subgroup to delete
    :type subgroup_id: int
    :return: ResponseMessages object if there are any messages, else None.
    :rtype: ResponseMessages | None
    """
    response = _http_request(
        method="DELETE",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/groups/{group_id}/sub_groups/{subgroup_id}",
        context="SubGroup Delete",
    )

    return _parse_response(
        response=response,
        key="messages",
        model=ResponseMessages,
        success_status_codes=[200],
    )
