"""
This module contains functions to interact with work orders in EZOfficeInventory.

Note: API will inconsistently use a 'tasks' or 'work_orders' key when returning
info from these endpoints. Each endpoint just needs to be checked which it is.
"""

import logging
import os
from datetime import datetime
from typing import Literal

from ezoff._helpers import (
    _get_ezo_headers,
    _get_paginated,
    _http_request,
    _parse_response,
)
from ezoff.data_model import (
    Component,
    LinkedInventory,
    ResponseMessages,
    WorkLog,
    WorkOrder,
)

logger = logging.getLogger(__name__)


def work_order_create(
    title: str,
    state: Literal["request"],
    priority: Literal["High", "Medium", "Low"],
    description: str | None = None,
    created_by_id: int | None = None,
    work_type_name: str | None = None,
    mark_items_unavailable: bool = False,
    warranty: bool = False,
    supervisor_id: int | None = None,
    assigned_to_id: int | None = None,
    assigned_to_type: Literal["User", "Team", "Vendor"] | None = None,
    secondary_assignee_ids: list[int] | None = None,
    reviewer_id: int | None = None,
    require_approval_from_reviewer: bool = False,
    location_id: int | None = None,
    expected_start_date: datetime | None = None,
    due_date: datetime | None = None,
    repetition: bool | None = None,
    repetition_start_date: datetime | None = None,
    repetition_end_date: datetime | None = None,
    repeat_every_duration: str | None = None,
    repeat_every_basis: int | None = None,
    recurrence_based_on_completion: bool | None = None,
    recurrence_based_on_interval: bool | None = None,
    custom_fields: list[dict] | None = None,
) -> WorkOrder | None:
    """
    Creates a work order.

    :param title: The title of the work order.
    :type title: str
    :param state: The state of the work order. Not sure what other valid values might be.
    :type state: str
    :param priority: The priority of the work order. Valid values are "High", "Medium", and "Low".
    :type priority: str
    :param description: A description of the work order.
    :type description: str, optional
    :param created_by_id: The ID of the user creating the work order.
    :type created_by_id: int, optional
    :param work_type_name: The name of the work type for the work order.
    :type work_type_name: str, optional
    :param mark_items_unavailable: Whether to mark items linked to the work order as unavailable.
    :type mark_items_unavailable: bool, optional
    :param warranty: Whether the work order is under warranty.
    :type warranty: bool, optional
    :param supervisor_id: The ID of the supervisor for the work order.
    :type supervisor_id: int, optional
    :param assigned_to_id: The ID of the user assigned to the work order.
    :type assigned_to_id: int, optional
    :param assigned_to_type: The type of the user assigned to the work order. Valid values are "User", "Team", and "Vendor".
    :type assigned_to_type: str, optional
    :param secondary_assignee_ids: A list of IDs of secondary assignees for the work order.
    :type secondary_assignee_ids: list[int], optional
    :param reviewer_id: The ID of the reviewer for the work order.
    :type reviewer_id: int, optional
    :param require_approval_from_reviewer: Whether the work order requires approval from the reviewer.
    :type require_approval_from_reviewer: bool, optional
    :param location_id: The ID of the location for the work order.
    :type location_id: int, optional
    :param expected_start_date: The expected start date of the work order.
    :type expected_start_date: datetime, optional
    :param due_date: The due date of the work order.
    :type due_date: datetime, optional
    :param repetition: Whether the work order is a repeating work order.
    :type repetition: bool, optional
    :param repetition_start_date: The start date of the repetition.
    :type repetition_start_date: datetime, optional
    :param repetition_end_date: The end date of the repetition.
    :type repetition_end_date: datetime, optional
    :param repeat_every_duration: The duration of the repetition. For example, "Month".
    :type repeat_every_duration: str, optional
    :param repeat_every_basis: The basis of the repetition.
    :type repeat_every_basis: int, optional
    :param recurrence_based_on_completion: Whether the repetition is based on completion of the work order.
    :type recurrence_based_on_completion: bool, optional
    :param recurrence_based_on_interval: Whether the repetition is based on a fixed interval.
    :type recurrence_based_on_interval: bool, optional
    :param custom_fields: A list of custom fields to set on the work order. Each item in
        the list should be a dictionary with 'id' and 'value' keys.
    :type custom_fields: list[dict], optional
    :return: The created work order object if successful, else None.
    :rtype: WorkOrder | None
    """
    params = {k: v for k, v in locals().items() if v is not None}

    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders",
        json={"work_order": params},
        context="Work Order Create",
    )

    return _parse_response(
        response=response,
        key="work_order",
        model=WorkOrder,
        success_status_codes=[200],
    )


def service_create(asset_id: int, service: dict) -> dict:
    """
    Creates a service record against a given asset.

    https://ezo.io/ezofficeinventory/developers/#api-create-service

    Note: API v1 endpoint, not sure what equivalent in v2 is.

    :param asset_id: The ID of the asset to create the service record against
    :type asset_id: int
    :param service: A dictionary containing the service record details
    :type service: dict
    :return: The created service record/response from API
    :rtype: dict
    """
    # Required fields
    if "service[end_date]" not in service:
        raise ValueError("service must have 'service[end_date]' key")
    if "service_end_time" not in service:
        raise ValueError("service must have 'service_end_time' key")
    if "service_type_name" not in service:
        raise ValueError("service must have 'service_type_name' key")
    if "service[description]" not in service:
        raise ValueError("service must have 'service[description]' key")

    # Remove any keys that are not valid
    valid_keys = [
        "service[start_date]",
        "service_start_time",
        "service[end_date]",
        "service_end_time",
        "service_type_name",
        "service[description]",
        "inventory_ids",
    ]

    service = {
        k: v
        for k, v in service.items()
        if k in valid_keys or k.startswith("linked_inventory_items")
    }

    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/assets/{asset_id}/services.api",
        json=service,
        context="Service Record Create",
    )

    return response.json()


def work_order_return(work_order_id: int) -> WorkOrder | None:
    """
    Get a single work order.

    :param work_order_id: The ID of the work order to retrieve.
    :type work_order_id: int
    :return: The work order object if found, else None.
    :rtype: WorkOrder | None
    """
    response = _http_request(
        method="GET",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}",
        headers=_get_ezo_headers(
            {
                "Cache-Control": "no-cache",
                "Host": f"{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            }
        ),
        context="Work Order",
    )

    return _parse_response(
        response=response,
        key="work_order",
        model=WorkOrder,
        success_status_codes=[200],
    )


def work_orders_return(filter: dict | None = None) -> list[WorkOrder]:
    """
    Get all work orders. Optionally filter using one or more work order fields.

    :param filter: A dictionary of fields to filter the work orders by.
    :type filter: dict, optional
    :return: A list of work order objects.
    :rtype: list[WorkOrder]
    """
    query_params = {}
    if filter:
        invalid = filter.keys() - WorkOrder.model_fields.keys()
        if invalid:
            raise ValueError(
                f"'{next(iter(invalid))}' is not a valid field for a work order."
            )
        query_params = {f"filters[{k}]": v for k, v in filter.items()}

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders"
    if query_params:
        url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])

    all_work_orders = _get_paginated(
        url=url,
        headers=_get_ezo_headers(),
        results_key="work_orders",
        context="Work Orders Return",
    )

    return [WorkOrder(**x) for x in all_work_orders]


def work_orders_search(search_term: str) -> list[WorkOrder]:
    """
    Search for work orders. Generally equivalent to usingthe search box in the UI.
    Generally recommended to use the work_orders_return function if you have any
    specific filters to go off of. But this is still useful for some cases, such as
    searching via user input.

    :param search_term: The term to search for in work orders.
    :type search_term: str
    :return: A list of work order objects that match the search term.
    :rtype: list[WorkOrder]
    """
    all_work_orders = _get_paginated(
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/search?search={search_term}",
        headers=_get_ezo_headers(),
        results_key="work_orders",
        context="Work Orders Search",
    )

    return [WorkOrder(**x) for x in all_work_orders]


def work_order_linked_work_orders_return(work_order_id: int) -> list[WorkOrder]:
    """
    Returns work orders that are linked to a particular work order.

    :param work_order_id: The ID of the work order to retrieve linked work orders for.
    :type work_order_id: int
    :return: A list of work order objects that are linked to the specified work order.
    :rtype: list[WorkOrder]
    """
    all_work_orders = _get_paginated(
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/linked_work_orders",
        headers=_get_ezo_headers(),
        results_key="work_orders",
        context="Work Order Linked Work Orders Return",
    )

    return [WorkOrder(**x) for x in all_work_orders]


def work_order_linked_inventory_return(work_order_id: int) -> list[LinkedInventory]:
    """
    Returns list of inventory items linked to a particular work order.

    :param work_order_id: The ID of the work order to retrieve linked inventory for.
    :type work_order_id: int
    :return: A list of linked inventory items.
    :rtype: list[LinkedInventory]
    """
    all_inven = _get_paginated(
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/linked_inventory_items",
        headers=_get_ezo_headers(),
        results_key="linked_inventory_items",
        context="Work Order Linked Inventory Return",
    )

    return [LinkedInventory(**x) for x in all_inven]


def work_order_types_return() -> list[dict]:
    """
    Get work order types.
    TODO v1 Not sure if there is a v2 equivalent.
    Function doesn't appear to be paginated even though most other similar
    functions are.

    https://ezo.io/ezofficeinventory/developers/#api-get-task-types

    :return: A list of work order types.
    :rtype: list[dict]
    """
    response = _http_request(
        method="GET",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/assets/task_types.api",
        context="Work Order Types Return",
    )

    if "work_order_types" not in response.json():
        logger.error(f"Error, could not get work order types: {response.content}")
        raise Exception(f"Error, could not get work order types: {response.content}")

    return response.json()["work_order_types"]


def work_order_work_logs_return(work_order_id: int) -> list[WorkLog]:
    """
    Returns a list of work logs attached to a particular work order.

    :param work_order_id: The ID of the work order to retrieve work logs for.
    :type work_order_id: int
    :return: A list of work log objects.
    :rtype: list[WorkLog]
    """
    all_logs = _get_paginated(
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}",
        headers=_get_ezo_headers(),
        results_key="work_logs",
        context="Work Order Work Logs Return",
    )

    return [WorkLog(**x) for x in all_logs]


def work_order_update(work_order_id: int, update_data: dict) -> WorkOrder | None:
    """
    Updates a work order.

    :param work_order_id: The ID of the work order to update.
    :type work_order_id: int
    :param update_data: A dictionary of fields to update on the work order.
    :type update_data: dict
    :return: The updated work order object if successful, else None.
    :rtype: WorkOrder | None
    """
    for field in update_data:
        if field not in WorkOrder.model_fields:
            raise ValueError(f"'{field}' is not a valid field for a group.")

    response = _http_request(
        method="PUT",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}",
        json={"work_order": update_data},
        context="Work Order Update",
    )

    return _parse_response(
        response=response,
        key="work_order",
        model=WorkOrder,
        success_status_codes=[200],
    )


def work_order_add_work_log(
    work_order_id: int,
    started_on_dttm: datetime,
    ended_on_dttm: datetime,
    hours_spent: float = 1,
    cost_per_hour: float = 0,
    note: str | None = None,
    custom_attributes: dict | None = None,
) -> dict:
    """
    Add a work log to a particular work order.

    Note: Found this one via the browser console. So not positive on all the
    valid values for parameters or return values.

    :param work_order_id: The ID of the work order to add the work log to.
    :type work_order_id: int
    :param started_on_dttm: The datetime the work started.
    :type started_on_dttm: datetime
    :param ended_on_dttm: The datetime the work ended.
    :type ended_on_dttm: datetime
    :param hours_spent: The number of hours spent on the work.
    :type hours_spent: float, optional
    :param cost_per_hour: The cost per hour of the work.
    :type cost_per_hour: float, optional
    :param note: A note to include with the work log.
    :type note: str, optional
    :param custom_attributes: A dictionary of custom attributes to include with the work log.
    :type custom_attributes: dict, optional
    :return: The response from the API.
    :rtype: dict
    """
    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/tasks/{work_order_id}/task_work_logs.json",
        json={
            "task_work_log": {
                "resource_id": 2657,  # Is misc always going to be 2657?
                "rate_type": "standard",
                "cost_per_hour": cost_per_hour,
                "time_spent": hours_spent,
                "total_cost": cost_per_hour * hours_spent,  # Is this needed?
                "resource_type": "MiscellaneousComponent",
                "description": note,
                "custom_attributes": custom_attributes,
            },
            "started_on_date": started_on_dttm.strftime("%m/%d/%Y"),
            "started_on_time": started_on_dttm.strftime("%I:%M %p"),
            "ended_on_date": ended_on_dttm.strftime("%m/%d/%Y"),
            "ended_on_time": ended_on_dttm.strftime("%I:%M %p"),
        },
        context="Work Order Add Work Log",
    )
    return response.json()


def work_order_add_linked_inv(
    work_order_id: int, inv_items: list[LinkedInventory]
) -> ResponseMessages | None:
    """
    Add linked inventory items to a work order.

    :param work_order_id: The ID of the work order to add linked inventory to.
    :type work_order_id: int
    :param inv_items: A list of LinkedInventory items to add to the work order.
    :type inv_items: list[LinkedInventory]
    :return: Response messages from the API if any, else None.
    :rtype: ResponseMessages | None
    """
    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/link_inventory",
        headers=_get_ezo_headers(),
        json={"work_order": {"linked_inventory_items": inv_items}},
        context="Work Order Add Linked Inventory",
    )

    return _parse_response(
        response=response,
        key="messages",
        model=ResponseMessages,
        success_status_codes=[200],
    )


def work_order_routing_update(
    work_order_id: int,
    assigned_to_id: str,
    start_dttm: datetime,
    due_dttm: datetime,
    task_type_id: int = None,
    supervisor_id: str | None = None,
    reviewer_id: str | None = None,
) -> WorkOrder | None:
    """
    Update the assigned to user and start/end time of a workorder.
    Intended for use by an external routing system.

    :param work_order_id: User facing work order ID.
    :type work_order_id: int
    :param assigned_to_id: System ID of user to assign to work order.
    :type assigned_to_id: str
    :param task_type_id: Task type of the work order.
    :type task_type_id: int
    :param start_dttm: Start datetime of the work order.
    :type start_dttm: datetime
    :param due_dttm: Due datetime of the work order.
    :type due_dttm: datetime
    :param supervisor_id: Supervisor ID to assign the work order.
    :type supervisor_id: str, optional
    :param reviewer_id: Reviewer ID to assign the work order.
    :type reviewer_id: str, optional
    :return: Response from the EZ Office API endpoint.
    :rtype: WorkOrder | None
    """
    filter = {
        "assigned_to_id": assigned_to_id,
        "due_date": due_dttm.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "expected_start_date": start_dttm.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "secondary_assignee_ids": [],
    }

    if supervisor_id is not None:
        filter["supervisor_id"] = supervisor_id
        logger.info(f"Updating work order supervisor to: {supervisor_id}")

    if reviewer_id is not None:
        filter["reviewer_id"] = reviewer_id

    result = work_order_update(work_order_id=work_order_id, update_data=filter)

    return result


def work_order_add_component(
    work_order_id: int, components: list[Component]
) -> ResponseMessages | None:
    """
    Adds a component to a work order.

    :param work_order_id: The ID of the work order to add the component to.
    :type work_order_id: int
    :param components: A list of Component objects to add to the work order.
    :type components: list[Component]
    :return: Response messages from the API if any, else None.
    :rtype: ResponseMessages | None
    """
    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/add_components",
        json={"work_order": {"components": components}},
        context="Work Order Add Component",
    )

    return _parse_response(response=response, key="messages", model=ResponseMessages)


def work_order_mark_in_progress(
    work_order_id: int,
) -> ResponseMessages | None:
    """
    Start a work order.

    :param work_order_id: The ID of the work order to start.
    :type work_order_id: int
    :return: Response messages from the API if any, else None.
    :rtype: ResponseMessages | None
    """
    response = _http_request(
        method="PATCH",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/mark_in_progress",
        context="Work Order Mark In-Progress",
    )

    return _parse_response(response=response, key="messages", model=ResponseMessages)


def work_order_mark_on_hold(
    work_order_id: int, comment: str | None = None
) -> ResponseMessages | None:
    """
    Start a particular work order.

    :param work_order_id: The ID of the work order to mark on hold.
    :type work_order_id: int
    :param comment: An optional comment to add when marking the work order on hold.
    :type comment: str, optional
    :return: Response messages from the API if any, else None.
    :rtype: ResponseMessages | None
    """
    response = _http_request(
        method="PATCH",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/mark_on_hold",
        json={
            "work_order": {
                "comment": comment,
            }
        },
        context="Work Order Mark On-Hold",
    )

    return _parse_response(response=response, key="messages", model=ResponseMessages)


def work_order_force_complete(work_order_id: int) -> None:
    """
    Forces a work order into a completed state.
    Work order will have any checklists cleared, then be marked in-progress,
    then be marked completed.

    :param work_order_id (int): Work order to force to a state of completed.
    """
    wo = work_order_return(work_order_id=work_order_id)
    if wo is None:
        return

    for checklist in wo.associated_checklists:
        checklist_id = checklist["checklist_id"]
        logger.info(f"Removing checklist id: {checklist_id}")
        work_order_remove_checklist(
            work_order_id=work_order_id, checklist_id=checklist_id
        )

    # The assigned to field of the work order must have data before marking in-progress.
    if wo.assigned_to_id is None and wo.state == "Open":
        # Default assigned to dispatch department.
        update_data = {"assigned_to_id": 1336290}
        work_order_update(work_order_id=work_order_id, update_data=update_data)

    if wo.state == "Open":
        work_order_mark_in_progress(work_order_id=work_order_id)

    work_order_mark_complete(
        work_order_id=work_order_id, completed_on_dttm=datetime.now()
    )


def work_order_mark_complete(
    work_order_id: int, completed_on_dttm: datetime
) -> ResponseMessages | None:
    """
    Completes a particular work order.

    :param work_order_id: The ID of the work order to mark complete.
    :type work_order_id: int
    :param completed_on_dttm: The datetime the work order was completed.
    :type completed_on_dttm: datetime
    :return: Response messages from the API if any, else None.
    :rtype: ResponseMessages | None
    """
    response = _http_request(
        method="PATCH",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/mark_complete",
        headers=_get_ezo_headers(
            {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
                "Host": f"{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            }
        ),
        json={
            "work_order": {
                "completed_on_date": completed_on_dttm.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        },
        context="Work Order Mark Complete",
    )

    return _parse_response(response=response, key="messages", model=ResponseMessages)


def work_order_add_linked_wo(
    work_order_id: int, wo_ids_to_link: list[int]
) -> ResponseMessages | None:
    """
    Links one or more work orders to a particular work order.

    :param work_order_id: The ID of the work order to link other work orders to.
    :type work_order_id: int
    :param wo_ids_to_link: A list of work order IDs to link to the specified work order.
    :type wo_ids_to_link: list[int]
    :return: Response messages from the API if any, else None.
    :rtype: ResponseMessages | None
    """
    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/link_work_orders",
        json={"work_order": {"work_order_ids": wo_ids_to_link}},
        context="Work Order Link Work Order",
    )

    return _parse_response(response=response, key="messages", model=ResponseMessages)


def work_order_remove_linked_wo(
    work_order_id: int, wo_ids_to_link: list[int]
) -> ResponseMessages | None:
    """
    Unlinks one or more work orders from a particular work order.

    :param work_order_id: The ID of the work order to unlink other work orders from.
    :type work_order_id: int
    :param wo_ids_to_link: A list of work order IDs to unlink from the specified work order.
    :type wo_ids_to_link: list[int]
    :return: Response messages from the API if any, else None.
    :rtype: ResponseMessages | None
    """
    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/unlink_work_orders",
        headers=_get_ezo_headers(
            {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
                "Host": f"{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            }
        ),
        json={"work_order": {"work_order_ids": wo_ids_to_link}},
        context="Work Order Un-Link Work Order",
    )

    return _parse_response(response=response, key="messages", model=ResponseMessages)


def work_order_add_linked_po(
    work_order_id: int, po_ids_to_link: list[int]
) -> ResponseMessages | None:
    """
    Links one or more purchase orders to a particular work order.

    :param work_order_id: The ID of the work order to link other work orders to.
    :type work_order_id: int
    :param po_ids_to_link: A list of purchase order IDs to link to the specified work order.
    :type po_ids_to_link: list[int]
    :return: Response messages from the API if any, else None.
    :rtype: ResponseMessages | None
    """
    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/link_po",
        headers=_get_ezo_headers(
            {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
                "Host": f"{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            }
        ),
        json={"work_order": {"purchase_order_ids": po_ids_to_link}},
        context="Work Order Link PO",
    )

    return _parse_response(response=response, key="messages", model=ResponseMessages)


def work_order_remove_linked_po(
    work_order_id: int, po_ids_to_link: list[int]
) -> ResponseMessages | None:
    """
    Unlinks one or more purchase orders from a particular work order.

    :param work_order_id: The ID of the work order to unlink other work orders from.
    :type work_order_id: int
    :param po_ids_to_link: A list of purchase order IDs to unlink from the specified work order.
    :type po_ids_to_link: list[int]
    :return: Response messages from the API if any, else None.
    :rtype: ResponseMessages | None
    """
    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/unlink_po",
        headers=_get_ezo_headers(
            {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
                "Host": f"{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            }
        ),
        json={"work_order": {"purchase_order_ids": po_ids_to_link}},
        context="Work Order Un-Link PO",
    )

    return _parse_response(response=response, key="messages", model=ResponseMessages)


def work_orders_start_component_service(
    work_order_id: int, component_ids: list[int]
) -> ResponseMessages | None:
    """
    Starts service on one or more assets on a work order.

    :param work_order_id: The ID of the work order to start service on.
    :type work_order_id: int
    :param component_ids: A list of component IDs to start service on.
    :type component_ids: list[int]
    :return: Response messages from the API if any, else None.
    :rtype: ResponseMessages | None
    """
    response = _http_request(
        method="PATCH",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/start_components_service",
        json={"component_ids": component_ids},
        context="Work Order Start Component Service",
    )

    return _parse_response(response=response, key="messages", model=ResponseMessages)


def work_orders_end_component_service(
    work_order_id: int, component_ids: list[int]
) -> ResponseMessages | None:
    """
    Ends service on one or more assets on a work order.

    :param work_order_id: The ID of the work order to end service on.
    :type work_order_id: int
    :param component_ids: A list of component IDs to end service on.
    :type component_ids: list[int]
    :return: Response messages from the API if any, else None.
    :rtype: ResponseMessages | None
    """
    response = _http_request(
        method="PATCH",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/end_components_service",
        json={"component_ids": component_ids},
        context="Work Order End Component Service",
    )

    return _parse_response(response=response, key="messages", model=ResponseMessages)


def work_order_add_checklist(
    work_order_id: int, checklist_id: int, asset_id: int | None = None
) -> dict:
    """
    Add a single checklist to an existing work order.

    Note: Found this one via the browser console. So not positive on all the
    valid values for parameters or return values.

    :param work_order_id: The ID of the work order to add checklist to.
    :type work_order_id: int
    :param checklist_id: ID of checklist to link with work order.
    :type checklist_id: int
    :param asset_id: ID of asset to assign this checklist to.
    :type asset_id: int, optional
    :return: The response from the API endpoint.
    :rtype: dict
    """
    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/tasks/{work_order_id}/add_checklists.json",
        json={"checklist_ids": str(checklist_id), "asset_id": str(asset_id)},
        context="Work Order Add Checklist",
    )

    return response.json()


def work_order_update_checklist(
    work_order_id: int,
    checklist_id: int,
    checklist_values: list[dict],
    asset_id: int | None = None,
) -> ResponseMessages | None:
    """
    Updates an existing checklist in a work order.

    :param work_order_id: ID of the work order to update checklist on.
    :type work_order_id: int
    :param checklist_id: ID of checklist to update.
    :type checklist_id: int
    :param checklist_values: A list of dictionaries containing checklist item IDs and their new values.
    :type checklist_values: list[dict]
    :param asset_id: ID of asset to assign this checklist to.
    :type asset_id: int, optional
    :return: Response messages from the API if any, else None.
    :rtype: ResponseMessages | None
    """
    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/update_work_order_checklist",
        json={
            "work_order": {
                "checklist_id": checklist_id,
                "asset_id": asset_id,
                "checklist_values": checklist_values,
            }
        },
        context="Work Order Update Checklist",
    )

    return _parse_response(response=response, key="messages", model=ResponseMessages)


def work_order_remove_checklist(
    work_order_id: int, checklist_id: int
) -> ResponseMessages | None:
    """
    Removes a checklist from a work order.

    :param work_order_id: ID of the work order to remove checklist from.
    :type work_order_id: int
    :param checklist_id: ID of checklist to remove.
    :type checklist_id: int
    :return: Response messages from the API if any, else None.
    :rtype: ResponseMessages | None
    """
    response = _http_request(
        method="DELETE",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}/remove_checklist",
        json={"work_order": {"checklist_id": checklist_id}},
        context="Work Order Remove Checklist",
    )

    return _parse_response(response=response, key="messages", model=ResponseMessages)


def work_order_delete(work_order_id: int) -> WorkOrder | None:
    """
    Deletes a particular work order.

    :param work_order_id: The ID of the work order to delete.
    :type work_order_id: int
    :return: The deleted WorkOrder object if successful, else None.
    :rtype: WorkOrder | None
    """
    response = _http_request(
        method="DELETE",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/{work_order_id}",
        context="Work Order Delete",
    )

    return _parse_response(
        response=response, key="work_order", model=WorkOrder, success_status_codes=[200]
    )


def work_orders_delete(work_order_ids: list[int]) -> ResponseMessages | None:
    """
    Deletes multiple work orders.
    Note: Mass deletion must be enabled in company settings. Off by default.

    :param work_order_ids: A list of work order IDs to delete.
    :type work_order_ids: list[int]
    :return: Response messages from the API if any, else None.
    :rtype: ResponseMessages | None
    """
    response = _http_request(
        method="PATCH",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/work_orders/mass_delete",
        json={"work_order": {"ids": work_order_ids}},
        context="Work Orders Delete",
    )

    return _parse_response(
        response=response,
        key="messages",
        model=ResponseMessages,
        success_status_codes=[200],
    )
