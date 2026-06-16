"""
Covers purchase order-related endpoints.

TODO: Update
TODO: Mark void
TODO: Add items
TODO: Receive items
TODO: Mark Confirmed
TODO: Delete
"""

import logging
import os

from ezoff._helpers import (
    _get_ezo_headers,
    _get_paginated,
    _http_request,
    _parse_response,
)
from ezoff.data_model import PurchaseOrder

logger = logging.getLogger(__name__)


def purchase_order_create(title: str, vendor_id: int) -> PurchaseOrder | None:
    """
    Creates a new purchase order.

    :param title: Title of the purchase order.
    :type title: str
    :param vendor_id: ID of the vendor for the purchase order.
    :type vendor_id: int
    :return: The created purchase order or None if creation failed.
    :rtype: PurchaseOrder | None
    """
    params = {k: v for k, v in locals().items() if v is not None}

    response = _http_request(
        method="POST",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/purchase_orders",
        json={"purchase_order": params},
        context="Purchase Order Create",
    )

    return _parse_response(
        response=response,
        key="purchase_order",
        model=PurchaseOrder,
        success_status_codes=[200],
    )


def purchase_order_return(purchase_order_id: int) -> PurchaseOrder | None:
    """
    Returns a particular purchase order.

    :param purchase_order_id: ID of the purchase order to return.
    :type purchase_order_id: int
    :return: The requested purchase order or None if not found.
    :rtype: PurchaseOrder | None
    """
    response = _http_request(
        method="GET",
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/purchase_orders/{purchase_order_id}",
        context="Purchase Order Return",
    )

    return _parse_response(
        response=response,
        key="purchase_order",
        model=PurchaseOrder,
        success_status_codes=[200],
    )


def purchase_orders_return() -> list[PurchaseOrder]:
    """
    Returns all purchase orders.

    :return: A list of all purchase orders.
    :rtype: list[PurchaseOrder]
    """
    all_purchase_orders = _get_paginated(
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/purchase_orders",
        headers=_get_ezo_headers(),
        results_key="purchase_orders",
        context="Purchase Orders Return",
    )

    return [PurchaseOrder(**x) for x in all_purchase_orders]
