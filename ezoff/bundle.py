import logging
import os
import time

import requests
from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff.data_model import Bundle

logger = logging.getLogger(__name__)


@Decorators.check_env_vars
def bundle_create(
    name: str,
    description: str,
    identification_number: str,
    location_id: int,
    enable_items_restricted_by_location: bool,
    bundle_line_items: list[dict],
    allow_add_bundle_without_specifying_items: bool,
) -> Bundle | None:
    """
    Creates a new bundle of items.
    """
    params = {k: v for k, v in locals().items() if v is not None}

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/bundles"

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            json={"bundle": params},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error creating bundle: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error creating bundle: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating bundle: {e}")
        raise Exception(f"Error creating bundle: {e}")

    if response.status_code == 200 and "bundle" in response.json():
        return Bundle(**response.json()["bundle"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def bundle_return(bundle_id: int) -> Bundle | None:
    """
    Returns a particular bundle
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/bundles/{bundle_id}"

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
            f"Error getting bundle: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error getting bundle: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting bundle: {e}")
        raise Exception(f"Error getting bundle: {e}")

    if response.status_code == 200 and "bundle" in response.json():
        return Bundle(**response.json()["bundle"])
    else:
        return None


@Decorators.check_env_vars
def bundles_return(filter: dict | None = None) -> list[Bundle]:
    """
    Returns all bundles. Optionally, filter by one or more of the bundle fields.
    """
    if filter:
        for field in filter:
            if field not in Bundle.model_fields:
                raise ValueError(f"'{field}' is not a valid field for a bundle.")
        filter = {"filters": filter}
    else:
        filter = None

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/bundles"

    all_bundles = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                json=filter,
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get bundles: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get bundles: {e}")
            raise

        data = response.json()

        if "bundles" not in data:
            logger.error(f"Error, could not get bundles: {response.content}")
            raise Exception(f"Error, could not get bundles: {response.content}")

        all_bundles.extend(data["bundles"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [Bundle(**x) for x in all_bundles]
