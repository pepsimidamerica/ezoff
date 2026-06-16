"""
Projects in EZOffice.

TODO: project_linked_items_return (API seems to just 500 internal server error)
"""

import logging
import os
from datetime import date
from typing import Literal

from ezoff._helpers import (
    _get_ezo_headers,
    _get_paginated,
    _http_request,
    _parse_response,
)
from ezoff.data_model import Project

logger = logging.getLogger(__name__)


def project_create(
    name: str,
    description: str | None = None,
    identifier: str | None = None,
    expected_start_date: date | None = None,
    expected_end_date: date | None = None,
    linked_modules: (
        Literal[
            "items",
            "checkouts",
            "reservations",
            "purchase_orders",
            "work_orders",
            "carts",
            "locations",
        ]
        | None
    ) = None,
    assigned_user_ids: list[int] | None = None,
) -> Project | None:
    """
    Creates a new project.

    :param name: Name of the project.
    :type name: str
    :param description: Description of the project.
    :type description: str, optional
    :param identifier: Identifier for the project.
    :type identifier: str, optional
    :param expected_start_date: Expected start date of the project.
    :type expected_start_date: date, optional
    :param expected_end_date: Expected end date of the project.
    :type expected_end_date: date, optional
    :param linked_modules: Modules to link to the project.
    :type linked_modules: str, optional
    :param assigned_user_ids: User IDs to assign to the project.
    :type assigned_user_ids: list of int, optional
    :return: The created project or None if creation failed.
    :rtype: Project | None
    """
    params = {k: v for k, v in locals().items() if v is not None}

    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/projects",
        json={"project": params},
        context="Project Create",
    )

    return _parse_response(
        response,
        "project",
        Project,
        success_status_codes=[200],
    )


def project_return(project_id: int) -> Project | None:
    """
    Returns a particular project.

    :param project_id: ID of the project to return.
    :type project_id: int
    :return: The requested project or None if not found.
    :rtype: Project | None
    """
    response = _http_request(
        method="GET",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/projects/{project_id}",
        context="Project Return",
    )

    return _parse_response(
        response=response,
        key="project",
        model=Project,
        success_status_codes=[200],
    )


def projects_return() -> list[Project]:
    """
    Returns all projects.

    :return: A list of all projects.
    :rtype: list[Project]
    """
    all_projects = _get_paginated(
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/projects",
        headers=_get_ezo_headers(),
        results_key="projects",
        context="Projects Return",
    )

    return [Project(**x) for x in all_projects]


def project_mark_complete(project_id: int) -> Project | None:
    """
    Mark a project as complete.

    :param project_id: ID of the project to mark as complete.
    :type project_id: int
    :return: The updated project or None if marking complete failed.
    :rtype: Project | None
    """
    response = _http_request(
        method="PATCH",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/projects/{project_id}/mark_complete",
        context="Project Mark Complete",
    )

    return _parse_response(
        response=response,
        key="project",
        model=Project,
        success_status_codes=[200],
    )


def project_mark_in_progress(project_id: int) -> Project | None:
    """
    Mark a project as in progress.

    :param project_id: ID of the project to mark as in progress.
    :type project_id: int
    :return: The updated project or None if marking in progress failed.
    :rtype: Project | None
    """
    response = _http_request(
        method="PATCH",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/projects/{project_id}/mark_in_progress",
        context="Project Mark In-Progress",
    )

    return _parse_response(
        response=response,
        key="project",
        model=Project,
        success_status_codes=[200],
    )
