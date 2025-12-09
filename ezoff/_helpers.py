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


def _log_request(msg: str, headers: dict = {}, params: dict = {}, payload: dict = {}):
    """Prints request details to the error log.
    Called after an error occurrs during an HTTP transaction.

    Args:
        msg (str): Message describing the API call that failed.
        headers (dict, optional): HTTP headers of failed request. Defaults to {}.
        params (dict, optional): HTTP parameters of failed request. Defaults to {}.
        payload (dict, optional): HTTP payload of failed request. Defaults to {}.
    """

    # Redact bearer token before logging headers.
    if "Authorization" in headers:
        headers["Authorization"] = "REDACTED"

    logger.error(msg)
    logger.error(f"Headers: {headers}")
    logger.error(f"Payload: {payload}")
    logger.error(f"Params: {params}")


@_basic_retry
def http_delete(
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
        response = requests.delete(
            url,
            headers=headers,
            params=params,
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        msg = f"HTTP error while deleting {title}: {e.response.status_code} - {e.response.content}"
        _log_request(msg=msg, headers=headers, params=params, payload=payload)
        raise

    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        msg = f"Connection error while deleting {title}: {e}"
        _log_request(msg=msg, headers=headers, params=params, payload=payload)
        raise

    except requests.exceptions.RequestException as e:
        msg = f"Request error while deleting {title}: {e}"
        _log_request(msg=msg, headers=headers, params=params, payload=payload)
        raise

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
        _log_request(msg=msg, headers=headers, params=params, payload=payload)
        raise

    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        msg = f"Connection error while getting {title}: {e}"
        _log_request(msg=msg, headers=headers, params=params, payload=payload)
        raise

    except requests.exceptions.RequestException as e:
        msg = f"Request error while getting {title}: {e}"
        _log_request(msg=msg, headers=headers, params=params, payload=payload)
        raise

    return response


@_basic_retry
def http_patch(
    url: str, title: str, timeout: int = 60, headers: dict = None, payload: dict = None
) -> requests.Response:

    if headers is None:
        headers = {
            # "Accept": "application/json",
            "Authorization": f"Bearer {os.environ['EZO_TOKEN']}",
        }

    try:
        response = requests.patch(
            url,
            headers=headers,
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        msg = f"HTTP error while patching {title}: {e.response.status_code} - {e.response.content}"
        _log_request(msg=msg, headers=headers, payload=payload)
        raise

    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        msg = f"Connection error while patching {title}: {e}"
        _log_request(msg=msg, headers=headers, payload=payload)
        raise

    except requests.exceptions.RequestException as e:
        msg = f"Request error while patching {title}: {e}"
        _log_request(msg=msg, headers=headers, payload=payload)
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
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        msg = f"HTTP error while posting {title}: {e.response.status_code} - {e.response.content}"
        _log_request(msg=msg, headers=headers, payload=payload)
        raise

    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        msg = f"Connection error while posting {title}: {e}"
        _log_request(msg=msg, headers=headers, payload=payload)
        raise

    except requests.exceptions.RequestException as e:
        msg = f"Request error while posting {title}: {e}"
        _log_request(msg=msg, headers=headers, payload=payload)
        raise

    return response


@_basic_retry
def http_put(
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
        msg = f"HTTP error while putting {title}: {e.response.status_code} - {e.response.content}"
        _log_request(msg=msg, headers=headers, payload=payload)
        raise

    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        msg = f"Connection error while putting {title}: {e}"
        _log_request(msg=msg, headers=headers, payload=payload)
        raise

    except requests.exceptions.RequestException as e:
        msg = f"Request error while putting {title}: {e}"
        _log_request(msg=msg, headers=headers, payload=payload)
        raise

    return response
