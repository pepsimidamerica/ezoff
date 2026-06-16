"""
This module contains functions to interact with the checklist v2 API in EZOfficeInventory.
"""

import logging
import os

from ezoff._helpers import _get_ezo_headers, _get_paginated
from ezoff.data_model import Checklist

logger = logging.getLogger(__name__)


def checklists_return() -> dict[int, Checklist]:
    """
    Returns all checklists.

    :return: A dictionary of Checklist objects. Keyed by checklist id.
    :rtype: dict[int, Checklist]
    """
    all_checklists = _get_paginated(
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/checklists",
        headers=_get_ezo_headers(),
        results_key="checklists",
    )
    return {checklist["id"]: Checklist(**checklist) for checklist in all_checklists}
