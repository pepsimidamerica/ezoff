"""
Covers retire reason-related endpoints.
"""

import logging
import os

from ezoff._helpers import _get_ezo_headers, _get_paginated
from ezoff.data_model import RetireReason

logger = logging.getLogger(__name__)


def retire_reasons_return() -> list[RetireReason]:
    """
    Returns all retire reasons.

    :return: A list of all retire reasons.
    :rtype: list[RetireReason]
    """
    all_retire_reasons = _get_paginated(
        url=f"https://{os.environ['EZO_SUBDOMAIN']}.ezofficeinventory.com/api/v2/retire_reasons",
        headers=_get_ezo_headers(),
        results_key="retire_reasons",
        context="Retire Reasons Return",
    )

    return [RetireReason(**x) for x in all_retire_reasons]
