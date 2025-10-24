"""
This module contains functions to interact with the checklist v2 API in EZOfficeInventory.
"""

import logging
import os
import time
from typing import Dict

import requests
from ezoff._auth import Decorators
from ezoff._helpers import _fetch_page
from ezoff.data_model import Checklist, ChecklistLineItem
from ezoff.exceptions import NoDataReturned

logger = logging.getLogger(__name__)


@Decorators.check_env_vars
def checklists_return() -> Dict[int, Checklist]:
    """
    Returns all checklists.

    :return: A dictionary of Checklist objects. Keyed by checklist id.
    :rtype: Dict[int, Checklist]
    """

    url = (
        f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/checklists"
    )

    all_checklists = {}

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error getting checklists: {e.response.status_code} - {e.response.content}"
            )
            raise Exception(
                f"Error getting checklists: {e.response.status_code} - {e.response.content}"
            )
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting checklists: {e}")
            raise Exception(f"Error getting checklists: {e}")

        data = response.json()

        if "checklists" not in data:
            raise NoDataReturned(f"No checklists found: {response.content}")

        for checklist in data['checklists']:
            all_checklists[checklist['id']] = Checklist(**checklist)

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return all_checklists
