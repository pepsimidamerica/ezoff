"""
Projects in EZOffice
"""

import logging
import os
import time
from datetime import date
from typing import Literal

import requests
from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff.data_model import Project

logger = logging.getLogger(__name__)


@Decorators.check_env_vars
def project_create(
    name: str,
    description: str | None = None,
    identifier: str | None = None,
    expected_start_date: date | None = None,
    expected_end_date: date | None = None,
    linked_modules: Literal[
        "items",
        "checkouts",
        "reservations",
        "purchase_orders",
        "work_orders",
        "carts",
        "locations",
    ]
    | None = None,
    assigned_user_ids: list[int] | None = None,
) -> Project | None:
    """
    Creates a new project.
    """

    params = {k: v for k, v in locals().items() if v is not None}

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/projects"

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            data={"project": params},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error creating project: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error creating project: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating project: {e}")
        raise Exception(f"Error creating project: {e}")

    if response.status_code == 200 and "project" in response.json():
        return Project(**response.json()["project"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def project_return(project_id: int) -> Project | None:
    """
    Returns a particular project.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/projects/{project_id}"

    try:
        response = requests.get(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error getting project: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error getting project: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting project: {e}")
        raise Exception(f"Error getting project: {e}")

    if response.status_code == 200 and "project" in response.json():
        return Project(**response.json()["project"])
    else:
        return None


@Decorators.check_env_vars
def projects_return() -> list[Project]:
    """
    Returns all proects.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/projects"

    all_projects = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get projects: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get projects: {e}")
            raise

        data = response.json()

        if "projects" not in data:
            logger.error(f"Error, could not get projects: {response.content}")
            raise Exception(f"Error, could not get projects: {response.content}")

        all_projects.extend(data["projects"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [Project(**x) for x in all_projects]


# @Decorators.check_env_vars
# def project_linked_items_return(project_id: int):
#     """
#     Returns objects for a given module linked to a project.
#     # TODO API endpoint seems to just 500 internal server error
#     # in my testing in Postman.
#     """


@Decorators.check_env_vars
def project_mark_complete(project_id: int) -> Project | None:
    """
    Mark a project as complete.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/projects/{project_id}/mark_complete"

    try:
        response = requests.patch(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error marking project complete: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error marking project complete: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error marking project complete: {e}")
        raise Exception(f"Error marking project complete: {e}")

    if response.status_code == 200 and "project" in response.json():
        return Project(**response.json()["project"])
    else:
        return None


@Decorators.check_env_vars
def project_mark_in_progress(project_id: int) -> Project | None:
    """
    Mark a project as in progress.
    """

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/projects/{project_id}/mark_in_progress"

    try:
        response = requests.patch(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error marking project in progress: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error marking project in progress: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error marking project in progress: {e}")
        raise Exception(f"Error marking project in progress: {e}")

    if response.status_code == 200 and "project" in response.json():
        return Project(**response.json()["project"])
    else:
        return None
