"""
Projects in EZOffice
"""

import os
import time

import requests
from pprint import pprint

from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page



@Decorators.check_env_vars
def project_link_asset(options: dict) -> dict:
    """
    Link a Fixed Asset to a Project
    https://ezo.io/ezofficeinventory/developers/#api-link-unlink-project
    """

    # Required fields
    if "seqs" not in options:
        raise ValueError("asset must have 'fixed_asset[name]' key")

    if "project_id" not in options:
        raise ValueError("asset must have 'fixed_asset[group_id]' key")

    # Remove any keys that are not valid
    valid_keys = [
        "seqs",
        "project_id",
    ]

    options = {
        k: v for k, v in options.items() if k in valid_keys or k.startswith("cust_attr")
    }

    url = os.environ["EZO_BASE_URL"] + "assets/link_to_project.api"

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data=options,
            timeout=60,
        )
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        raise Exception(
            f"Error, could not assign asset to project: {e.response.status_code} - {e.response.content}"
        )
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error, could not assign asset to project: {e}")

    return response.json()
