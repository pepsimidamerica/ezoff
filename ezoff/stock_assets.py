"""
Covers stock asset-related endpoints.

TODO: Quantity By Location
TODO: Line Item Locations
TODO: Current Checkouts
TODO: Custom Field History
TODO: Location Based Threshold
TODO: History
TODO: Reservations
TODO: Add stock
TODO: Transfer stock
TODO: checkout
TODO: checkin
TODO: update location
TODO: retire
TODO: activate
TODO: create reservation
TODO: Link to project
TODO: Unlink from project
"""

import logging
import os

from ezoff._helpers import (
    _get_ezo_headers,
    _get_paginated,
    _http_request,
    _parse_response,
)
from ezoff.data_model import ResponseMessages, StockAsset

logger = logging.getLogger(__name__)


def stock_asset_create(
    name: str,
    group_id: int,
    location_id: int,
    display_image: str | None = None,
    identifier: str | None = None,
    description: str | None = None,
    product_model_number: str | None = None,
    cost_price: float | None = None,
    vendor_id: int | None = None,
    salvage_value: float | None = None,
    sub_group_id: int | None = None,
    inventory_threshold: int | None = None,
    default_low_location_threshold: int | None = None,
    default_excess_location_threshold: int | None = None,
    initial_stock_quantity: int | None = None,
    line_item_attributes: list[dict] | None = None,
    location_thresholds_attributes: list[dict] | None = None,
    asset_detail_attributes: dict | None = None,
    custom_fields: list[dict] | None = None,
) -> StockAsset | None:
    """
    Creates a stock asset.

    :param name: Name of the stock asset.
    :type name: str
    :param group_id: ID of the group the stock asset belongs to.
    :type group_id: int
    :param location_id: ID of the location where the stock asset is stored.
    :type location_id: int
    :param display_image: URL of the display image for the stock asset.
    :type display_image: str, optional
    :param identifier: Identifier for the stock asset.
    :type identifier: str, optional
    :param description: Description of the stock asset.
    :type description: str, optional
    :param product_model_number: Product model number of the stock asset.
    :type product_model_number: str, optional
    :param cost_price: Cost price of the stock asset.
    :type cost_price: float, optional
    :param vendor_id: ID of the vendor for the stock asset.
    :type vendor_id: int, optional
    :param salvage_value: Salvage value of the stock asset.
    :type salvage_value: float, optional
    :param sub_group_id: ID of the sub-group the stock asset belongs to.
    :type sub_group_id: int, optional
    :param inventory_threshold: Inventory threshold for the stock asset.
    :type inventory_threshold: int, optional
    :param default_low_location_threshold: Default low location threshold for the stock asset.
    :type default_low_location_threshold: int, optional
    :param default_excess_location_threshold: Default excess location threshold for the stock asset.
    :type default_excess_location_threshold: int, optional
    :param initial_stock_quantity: Initial stock quantity of the stock asset.
    :type initial_stock_quantity: int, optional
    :param line_item_attributes: Line item attributes for the stock asset.
    :type line_item_attributes: list of dict, optional
    :param location_thresholds_attributes: Location thresholds attributes for the stock asset.
    :type location_thresholds_attributes: list of dict, optional
    :param asset_detail_attributes: Asset detail attributes for the stock asset.
    :type asset_detail_attributes: dict, optional
    :param custom_fields: Custom fields for the stock asset.
    :type custom_fields: list of dict, optional
    :return: The created stock asset or None if creation failed.
    :rtype: StockAsset | None
    """
    params = {k: v for k, v in locals().items() if v is not None}

    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/stock_assets",
        json={"asset_stock": params},
        context="Stock Asset Create",
    )

    return _parse_response(
        response=response,
        key="asset_stock",
        model=StockAsset,
        success_status_codes=[200],
    )


def stock_asset_return(stock_asset_id: int) -> StockAsset | None:
    """
    Returns a particular stock asset.

    :param stock_asset_id: ID of the stock asset to return.
    :type stock_asset_id: int
    :return: The requested stock asset or None if not found.
    :rtype: StockAsset | None
    """
    response = _http_request(
        method="GET",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/stock_assets/{stock_asset_id}",
        context="Stock Asset Return",
    )

    return _parse_response(
        response=response,
        key="asset_stock",
        model=StockAsset,
        success_status_codes=[200],
    )


def stock_assets_return(filter: dict | None = None) -> list[StockAsset]:
    """
    Returns all stock assets. Optionally, filter using one or more fields.

    :param filter: Dictionary of stock asset fields and the values to filter results by.
    :type filter: dict, optional
    :return: List of StockAsset objects.
    :rtype: list[StockAsset]
    """
    query_params = {}
    if filter:
        invalid = filter.keys() - StockAsset.model_fields.keys()
        if invalid:
            raise ValueError(f"Invalid filter fields: {', '.join(invalid)}")
        query_params = {f"filters[{k}]": v for k, v in filter.items()}

    url = f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/stock_assets"
    if query_params:
        url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])

    all_stock_assets = _get_paginated(
        url=url,
        headers=_get_ezo_headers(),
        results_key="asset_stock",
        context="Stock Assets Return",
    )

    return [StockAsset(**x) for x in all_stock_assets]


def stock_assets_search(search_term: str) -> list[StockAsset]:
    """
    Search for stock assets using some search term. Equivalent to using the search
    box in the UI. Generally recommended to use stock_assets_return with filters
    instead, if you have some specific criteria to go off of. Otherwise, this can
    also be useful if for example, taking user input to search.

    :param search_term: The term to search for.
    :type search_term: str
    :return: List of StockAsset objects matching the search term.
    :rtype: list[StockAsset]
    """
    all_stock_assets = _get_paginated(
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/stock_assets/search?search={search_term}",
        headers=_get_ezo_headers(),
        results_key="asset_stock",
        context="Stock Assets Search",
    )

    return [StockAsset(**x) for x in all_stock_assets]


def stock_asset_delete(stock_asset_id: int) -> ResponseMessages | None:
    """
    Deletes a particular stock asset.

    :param stock_asset_id: ID of the stock asset to delete.
    :type stock_asset_id: int
    :return: ResponseMessages object if there are any messages, else None.
    :rtype: ResponseMessages | None
    """
    response = _http_request(
        method="DELETE",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/stock_assets/{stock_asset_id}",
        context="Stock Asset Delete",
    )

    return _parse_response(
        response=response,
        key="messages",
        model=ResponseMessages,
        success_status_codes=[200],
    )
