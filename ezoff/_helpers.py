"""
Helper functions for ezoff
"""

import logging
import os

import requests
from tenacity import (
    after_log,
    before_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


def should_retry_http_or_network_error(exception: BaseException) -> bool:
    """
    Determines if an exception warrants a retry.
    Retries on ConnectionError, Timeout, or specific HTTP 5XX errors.
    """
    if isinstance(
        exception, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)
    ):
        return True
    if isinstance(exception, requests.exceptions.HTTPError):
        # Retry on 5XX server errors
        return 500 <= exception.response.status_code < 600
    return False


_basic_retry = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception(should_retry_http_or_network_error),
    before=before_log(logger, logging.DEBUG),
    after=after_log(logger, logging.DEBUG),
)


@_basic_retry
def _fetch_page(url, headers, params=None, data=None, json=None):
    """
    Wrapper around requests.get that retries on RequestException

    Exists as an alternative to the basic_retry decorator. For paginated functions,
    you don't want to retry the entire function, just the specific page call.
    """
    response = requests.get(
        url, headers=headers, params=params, data=data, json=json, timeout=60
    )
    response.raise_for_status()
    return response


@_basic_retry
def http_get(
    url: str,
    title: str,
    timeout: int = 60,
    headers: dict = None,
    payload: dict = None,
    params: dict = None,
) -> requests.Response:

    if headers is None:
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {os.environ['EZO_TOKEN']}",
        }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        msg = f"HTTP error while getting {title}: {e.response.status_code} - {e.response.content}"
        logger.error(msg)
        raise

    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        msg = f"Connection error while getting {title}: {e}"
        logger.error(msg)
        raise

    except requests.exceptions.RequestException as e:
        msg = f"Request error while getting {title}: {e}"
        logger.error(msg)
        raise

    return response


@_basic_retry
def http_post(
    url: str, payload: dict, title: str, timeout: int = 60, headers: dict = None
) -> requests.Response:

    if headers is None:
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {os.environ['EZO_TOKEN']}",
        }

    try:
        response = requests.put(
            url,
            headers=headers,
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        msg = f"HTTP error while posting {title}: {e.response.status_code} - {e.response.content}"
        logger.error(msg)
        logger.error(f"Payload: {payload}")
        raise

    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        msg = f"Connection error while posting {title}: {e}"
        logger.error(msg)
        logger.error(f"Payload: {payload}")
        raise

    except requests.exceptions.RequestException as e:
        msg = f"Request error while posting {title}: {e}"
        logger.error(msg)
        logger.error(f"Payload: {payload}")
        raise

    return response
