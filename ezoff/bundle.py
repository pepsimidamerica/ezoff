"""
This module contains functions for interacting with bundles in EZOfficeInventory.
"""

import logging
import os

from ezoff._helpers import (
    _get_ezo_headers,
    _get_paginated,
    _http_request,
    _parse_response,
)
from ezoff.data_model import Bundle

logger = logging.getLogger(__name__)


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

    :param name: The name of the bundle.
    :type name: str
    :param description: A description of the bundle.
    :type description: str
    :param identification_number: A unique identification number for the bundle.
    :type identification_number: str
    :param location_id: The ID of the location the bundle is associated with.
    :type location_id: int
    :param enable_items_restricted_by_location: Whether to enable items restricted by location.
    :type enable_items_restricted_by_location: bool
    :param bundle_line_items: A list of dictionaries representing the items in the bundle.
    :type bundle_line_items: list[dict]
    :param allow_add_bundle_without_specifying_items: Whether to allow adding the bundle without specifying items.
    :type allow_add_bundle_without_specifying_items: bool
    :return: The created Bundle object if successful, else None.
    :rtype: Bundle | None
    """
    params = {k: v for k, v in locals().items() if v is not None}

    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/bundles",
        json={"bundle": params},
        context="Bundle Create",
    )

    return _parse_response(
        response=response,
        key="bundle",
        model=Bundle,
        success_status_codes=[200],
    )


def bundle_return(bundle_id: int) -> Bundle | None:
    """
    Returns a particular bundle.

    :param bundle_id: The ID of the bundle to retrieve.
    :type bundle_id: int
    :return: The Bundle object if found, else None.
    :rtype: Bundle | None
    """
    response = _http_request(
        method="GET",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/bundles/{bundle_id}",
        context="Bundle Return",
    )

    return _parse_response(
        response=response,
        key="bundle",
        model=Bundle,
        success_status_codes=[200],
    )


def bundles_return(filter: dict | None = None) -> list[Bundle]:
    """
    Returns all bundles.

    :param filter: A dictionary of bundle fields and the values to filter by.
    :type filter: dict, optional
    :return: A list of Bundle objects.
    :rtype: list[Bundle]
    """
    query_params = {}
    if filter:
        invalid = filter.keys() - Bundle.model_fields.keys()
        if invalid:
            raise ValueError(f"Invalid fields: {', '.join(invalid)}")
        query_params = {f"filters[{k}]": v for k, v in filter.items()}

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/bundles"
    if query_params:
        url += "?" + "&".join(f"{k}={v}" for k, v in query_params.items())

    all_bundles = _get_paginated(
        url=url,
        headers=_get_ezo_headers(),
        results_key="bundles",
    )

    return [Bundle(**x) for x in all_bundles]
