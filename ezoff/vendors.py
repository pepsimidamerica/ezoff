import logging
import os
import time

import requests
from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff.data_model import Vendor

logger = logging.getLogger(__name__)


@Decorators.check_env_vars
def vendor_create(
    name: str,
    address: str | None = None,
    description: str | None = None,
    email: str | None = None,
    fax: str | None = None,
    phone: str | None = None,
    website: str | None = None,
    contact_person_name: str | None = None,
    status: bool | None = None,
    custom_fields: list[dict] | None = None,
) -> Vendor | None:
    """
    Creates a new vendor.
    """
    params = {k: v for k, v in locals().items() if v is not None}

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/vendors"

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            data={"vendor": params},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error creating vendor: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error creating vendor: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating vendor: {e}")
        raise Exception(f"Error creating vendor: {e}")

    if response.status_code == 200 and "vendor" in response.json():
        return Vendor(**response.json()["vendor"])
    else:
        return None


@_basic_retry
@Decorators.check_env_vars
def vendor_return(vendor_id: int) -> Vendor | None:
    """
    Returns a particular vendor.
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/vendors/{vendor_id}"

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
            f"Error getting vendor: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error getting vendor: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting vendor: {e}")
        raise Exception(f"Error getting vendor: {e}")

    if response.status_code == 200 and "vendor" in response.json():
        return Vendor(**response.json()["vendor"])
    else:
        return None


@Decorators.check_env_vars
def vendors_return() -> list[Vendor]:
    """
    Returns all vendors
    """
    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/vendors"

    all_vendors = []

    while True:
        try:
            response = _fetch_page(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                data=filter,
            )
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get vendors: {e.response.status_code} - {e.response.content}"
            )
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get vendors: {e}")
            raise

        data = response.json()

        if "vendors" not in data:
            logger.error(f"Error, could not get vendors: {response.content}")
            raise Exception(f"Error, could not get vendors: {response.content}")

        all_vendors.extend(data["vendors"])

        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        # Get the next page's url from the current page of data.
        url = data["metadata"]["next_page"]

        time.sleep(1)

    return [Vendor(**x) for x in all_vendors]


@Decorators.check_env_vars
def vendor_update(vendor_id: int, update_data: dict) -> Vendor | None:
    """
    Updates a particular vendor.
    """
    for field in update_data:
        if field not in Vendor.model_fields:
            raise ValueError(f"'{field}' is not a valid field for a vendor.")

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/vendors/{vendor_id}"

    try:
        response = requests.patch(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
                "Accept": "application/json",
            },
            data={"vendor": update_data},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error updating vendor: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error updating vendor: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error updating vendor: {e}")
        raise Exception(f"Error updating vendor: {e}")

    if response.status_code == 200 and "vendor" in response.json():
        return Vendor(**response.json()["vendor"])
    else:
        return None
