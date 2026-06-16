"""
Covers vendor-related endpoints.
"""

import logging
import os

from ezoff._helpers import (
    _get_ezo_headers,
    _get_paginated,
    _http_request,
    _parse_response,
)
from ezoff.data_model import Vendor

logger = logging.getLogger(__name__)


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

    :param name: The name of the vendor.
    :type name: str
    :param address: The address of the vendor.
    :type address: str, optional
    :param description: A description of the vendor.
    :type description: str, optional
    :param email: The email address of the vendor.
    :type email: str, optional
    :param fax: The fax number of the vendor.
    :type fax: str, optional
    :param phone: The phone number of the vendor.
    :type phone: str, optional
    :param website: The website of the vendor.
    :type website: str, optional
    :param contact_person_name: The name of the contact person for the vendor.
    :type contact_person_name: str, optional
    :param status: The status of the vendor. True for active, False for inactive.
    :type status: bool, optional
    :param custom_fields: List of custom fields to set on the vendor. Each item in
        the list should be a dictionary with 'id' and 'value' keys.
    :type custom_fields: list[dict], optional
    :return: The created vendor object if successful, else None.
    :rtype: Vendor | None
    """
    params = {k: v for k, v in locals().items() if v is not None}

    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/vendors",
        json={"vendor": params},
        context="Vendor Create",
    )

    return _parse_response(
        response=response,
        key="vendor",
        model=Vendor,
        success_status_codes=[200],
    )


def vendor_return(vendor_id: int) -> Vendor | None:
    """
    Returns a particular vendor.

    :param vendor_id: The ID of the vendor to return.
    :type vendor_id: int
    :return: The vendor object if found, else None.
    :rtype: Vendor | None
    """
    response = _http_request(
        method="GET",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/vendors/{vendor_id}",
        context="Vendor Return",
    )

    return _parse_response(
        response=response,
        key="vendor",
        model=Vendor,
        success_status_codes=[200],
    )


def vendors_return() -> list[Vendor]:
    """
    Returns all vendors.

    :return: List of all vendor objects.
    :rtype: list[Vendor]
    """
    all_vendors = _get_paginated(
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/vendors",
        headers=_get_ezo_headers(),
        results_key="vendors",
        context="Vendors Return",
    )

    return [Vendor(**x) for x in all_vendors]


def vendor_update(vendor_id: int, update_data: dict) -> Vendor | None:
    """
    Updates a particular vendor.

    :param vendor_id: The ID of the vendor to update.
    :type vendor_id: int
    :param update_data: A dictionary of fields to update on the vendor.
    :type update_data: dict
    :return: The updated vendor object if successful, else None.
    :rtype: Vendor | None
    """
    for field in update_data:
        if field not in Vendor.model_fields:
            raise ValueError(f"'{field}' is not a valid field for a vendor.")

    response = _http_request(
        method="PATCH",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/vendors/{vendor_id}",
        json={"vendor": update_data},
        context="Vendor Update",
    )

    return _parse_response(
        response=response,
        key="vendor",
        model=Vendor,
        success_status_codes=[200],
    )
