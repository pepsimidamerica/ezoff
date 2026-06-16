"""
Covers package-related endpoints.
"""

import logging
import os
from datetime import datetime

from ezoff._helpers import (
    _get_ezo_headers,
    _get_paginated,
    _http_request,
    _parse_response,
)
from ezoff.data_model import Package, ResponseMessages

logger = logging.getLogger(__name__)


def package_create(
    name: str,
    description: str | None = None,
    asset_ids: list[int] | None = None,
    arbitration: str | None = None,
) -> Package | None:
    """
    Create a new asset package.

    :param name: Name of the package
    :type name: str
    :param description: Description of the package
    :type description: str, optional
    :param asset_ids: List of asset IDs to include in the package
    :type asset_ids: list[int], optional
    :param arbitration: Arbitration details for the package
    :type arbitration: str, optional
    :return: The created package if successful, else None
    :rtype: Package | None
    """
    params = {k: v for k, v in locals().items() if v is not None}

    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/packages",
        json={"package": params},
        context="Package Create",
    )

    return _parse_response(
        response=response, key="package", model=Package, success_status_codes=[200]
    )


def package_return(package_id: int) -> Package | None:
    """
    Returns a particular package.

    :param package_id: The ID of the package to retrieve
    :return: The package if found, else None
    :rtype: Package | None
    """
    response = _http_request(
        method="GET",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/packages/{package_id}",
        context="Package Return",
    )

    return _parse_response(
        response=response, key="package", model=Package, success_status_codes=[200]
    )


def packages_return() -> list[Package]:
    """
    Returns all packages.

    :return: List of all packages
    :rtype: list[Package]
    """
    all_packages = _get_paginated(
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/packages",
        headers=_get_ezo_headers(),
        results_key="packages",
        context="Packages Return",
    )

    return [Package(**x) for x in all_packages]


def package_checkin(
    package_id: int, comments: str, location_id: int, checkin_date: datetime
) -> ResponseMessages | None:
    """
    Checks in an asset package.

    :param package_id: The ID of the package to check in
    :type package_id: int
    :param comments: Comments regarding the check-in
    :type comments: str
    :param location_id: The ID of the location where the package is being checked in
    :type location_id: int
    :param checkin_date: The date and time of the check-in
    :type checkin_date: datetime
    :return: Response messages if successful, else None
    :rtype: ResponseMessages | None
    """
    response = _http_request(
        method="PUT",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/packages/{package_id}/checkin",
        json={
            "package": {
                "comments": comments,
                "location_id": location_id,
                "checkin_date": checkin_date,
            }
        },
        context="Package Checkin",
    )

    return _parse_response(
        response=response,
        key="messages",
        model=ResponseMessages,
        success_status_codes=[200],
    )
