import logging
import os
import time
from datetime import datetime

import requests
from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff.data_model import Package, ResponseMessages

logger = logging.getLogger(__name__)


@Decorators.check_env_vars
def package_create(
    name: str,
    description: str | None = None,
    asset_ids: list[int] | None = None,
    arbitration: str | None = None,
) -> Package | None:
    """
    Create a new asset package.
    """
    params = {k: v for k, v in locals().items() if v is not None}

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/packages"

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            data={"package": params},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error creating package: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error creating package: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating package: {e}")
        raise Exception(f"Error creating package: {e}")

    if response.status_code == 200 and "package" in response.json():
        return Package(**response.json()["package"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def package_return(package_id: int) -> Package | None:
    """
    Returns a particular package.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/packages/{package_id}"

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
            f"Error getting package: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error getting package: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting package: {e}")
        raise Exception(f"Error getting package: {e}")

    if response.status_code == 200 and "package" in response.json():
        return Package(**response.json()["package"])
    else:
        return None


@Decorators.check_env_vars
def packages_return() -> list[Package]:
    """
    Returns all packages.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/packages"

    all_packages = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                data=filter,
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get packages: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get packages: {e}")
            raise

        data = response.json()

        if "packages" not in data:
            logger.error(f"Error, could not get packages: {response.content}")
            raise Exception(f"Error, could not get packages: {response.content}")

        all_packages.extend(data["packages"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [Package(**x) for x in all_packages]


@Decorators.check_env_vars
def package_checkin(
    package_id: int, comments: str, location_id: int, checkin_date: datetime
) -> ResponseMessages | None:
    """
    Checks in an asset package.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/packages/{package_id}/checkin"

    try:
        response = requests.put(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data={
                "package": {
                    "comments": comments,
                    "location_id": location_id,
                    "checkin_date": checkin_date,
                }
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error checking in asset: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error checking in asset: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking in asset: {e}")
        raise Exception(f"Error checking in asset: {e}")

    if response.status_code == 200:
        return ResponseMessages(**response.json()["messages"])
    else:
        return None
