"""
Helper functions for ezoff
"""

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

_basic_retry = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
)


@_basic_retry
def _fetch_page(url, headers, params):
    """
    Wrapper around requests.get that retries on RequestException
    """
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response