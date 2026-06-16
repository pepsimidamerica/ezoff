"""
Helper functions for ezoff.
"""

import logging
import os
import random
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Literal, TypeVar

import pydantic
import requests
from tenacity import (
    after_log,
    before_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
)

logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 60


def _should_retry_http_or_network_error(exception: BaseException) -> bool:
    """
    Determines if an exception warrants a retry.

    Retries on ConnectionError, Timeout, HTTP 429 (rate limit),
    or HTTP 5XX server errors.

    :param exception: The exception to evaluate.
    :type exception: BaseException
    :return: True if the exception warrants a retry, False otherwise.
    :rtype: bool
    """
    if isinstance(
        exception,
        (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.ChunkedEncodingError,
        ),
    ):
        return True
    # SSLError is a subclass of ConnectionError in some requests versions,
    # but not all.
    if isinstance(exception, requests.exceptions.SSLError):
        return True
    if isinstance(exception, requests.exceptions.HTTPError):
        status = exception.response.status_code
        return status == 429 or 500 <= status < 600
    return False


def _wait_for_retry(retry_state) -> float:
    """
    Custom wait strategy for tenacity retries.

    On HTTP 429 (rate limit), respects the Retry-After header if present.
    Falls back to a 60-second wait if the header is missing or unparseable.
    For all other retryable errors, uses exponential backoff.

    :param retry_state: The current retry state from tenacity.
    :type retry_state: tenacity.RetryCallState
    :return: Number of seconds to wait before retrying.
    :rtype: float
    """
    if retry_state.outcome and retry_state.outcome.failed:
        exception = retry_state.outcome.exception()
        if isinstance(exception, requests.exceptions.HTTPError):
            response = getattr(exception, "response", None)
            if response is not None and response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                if retry_after is not None:
                    # Retry-After can be a plain integer (seconds).
                    try:
                        seconds = int(retry_after)
                        logger.info(
                            "Rate limited (429). Retrying after %ds (Retry-After header).",
                            seconds,
                        )
                        return float(seconds)
                    except ValueError:
                        pass
                    # Retry-After can also be an HTTP-date.
                    try:
                        retry_time = parsedate_to_datetime(retry_after)
                        wait = (retry_time - datetime.now(timezone.utc)).total_seconds()
                        if wait > 0:
                            logger.info(
                                "Rate limited (429). Retrying after %.0fs (Retry-After header).",
                                wait,
                            )
                            return wait
                    except (ValueError, TypeError, OverflowError):
                        pass
                # No parseable Retry-After header.
                logger.info(
                    "Rate limited (429). No valid Retry-After header, waiting 60s."
                )
                return 60.0

    # Exponential backoff with jitter for all other retryable errors.
    base = min(2 ** (retry_state.attempt_number - 1) * 4, 120)
    jitter = base * 0.25 * (random.random() * 2 - 1)  # ±25%
    return max(0, base + jitter)


_basic_retry = retry(
    stop=stop_after_attempt(5),
    wait=_wait_for_retry,
    retry=retry_if_exception(_should_retry_http_or_network_error),
    before=before_log(logger, logging.DEBUG),
    after=after_log(logger, logging.DEBUG),
)


def _check_env_vars() -> None:
    """
    Raises an exception if required env vars have not been set before
    a quest to EZO is made.
    """
    if "EZO_SUBDOMAIN" not in os.environ:
        raise Exception("EZO_SUBDOMAIN not found in environment variables.")
    if "EZO_TOKEN" not in os.environ:
        raise Exception("EZO_TOKEN not found in environment variables.")


def _get_ezo_headers(extra_headers: dict | None = None) -> dict:
    """
    Returns EZO API headers with bearer token.

    :param extra_headers: Additional headers to merge in
    :type extra_headers: dict | None
    :return: Complete headers dict for Graph API requests
    :rtype: dict
    """
    headers = {
        "Authorization": "Bearer " + os.environ["EZO_TOKEN"],
        "Accept": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)
    return headers


M = TypeVar("M", bound=pydantic.BaseModel)


def _parse_response(
    response: requests.Response,
    key: str,
    model: type[M],
    success_status_codes: list[int] | None = None,
) -> M | None:
    """
    Parses a response and returns a model instance if response was successful.

    :param response: The HTTP response to parse.
    :type response: requests.Response
    :param key: The JSON key to extract from the response body.
    :type key: str
    :param model: A Pydantic model class to deserialize the response data into.
    :type model: type[M]
    :param success_status_codes: One or more status codes that would indicate a successful response.
    :type success_status_codes: list[int] | None
    :return: An instance of model if parsing succeeded, otherwise None.
    :rtype: M | None
    """
    # Optionally, check if response code is not in list of known successful codes.
    if (
        success_status_codes is not None
        and response.status_code not in success_status_codes
    ):
        return None

    if key in response.json():
        return model(**response.json()[key])

    return None


# def create_query_params_from_filter(
#     filter: dict | None = None,
#     valid_keys: list[str] | None = None,
# ) -> str:
#     """
#     EZOffice GET endpoints accept a number of parameters. We accept a general
#     filter dictionary that the user can use to filter the results. We first check
#     that the filters they have provided are valid. We then convert them into the format
#     EZOffice expects and return them as a query string that can be appended to the base URL.

#     {"status": "active"} -> "?filters[status]=active"
#     {} or None -> ""
#     {"invalid_key": } -> ""
#     """
#     query_params = {}


@_basic_retry
def _http_request(
    method: Literal["GET", "POST", "PATCH", "DELETE", "PUT", "HEAD", "OPTIONS"],
    url: str,
    headers: dict | None = None,
    context: str = "HTTP Request",
    **kwargs,
) -> requests.Response:
    """
    Generic HTTP request handler with consistent error handling.

    Wraps requests.request() with standardized error handling,
    logging, and timeout management.

    :param method: HTTP method (GET, POST, PATCH, DELETE, etc.)
    :type method: str
    :param url: Target URL
    :type url: str
    :param headers: HTTP headers
    :type headers: dict
    :param context: Human-readable context for error messages
    :type context: str
    :param kwargs: Additional arguments passed to requests.request()
                   (json, data, params, timeout, etc.)
    :return: Response object
    :rtype: requests.Response
    :raises Exception: For HTTP errors or general request failures
    """
    _check_env_vars()

    def _log_request(error_msg: str) -> None:
        """
        Prints request details to the error log.
        Called if an error occurs as a result of the HTTP request.

        :param error_msg: The error message to log.
        :type error_msg: str
        """
        logger.error("*" * 50)
        logger.error(error_msg)
        logger.error(f"HTTP Method: {method}")
        logger.error(f"URL: {url}")

        # Redact bearer token before logging headers.
        if headers is not None:
            safe_headers = headers.copy()
            if "Authorization" in headers:
                safe_headers["Authorization"] = "REDACTED"
            logger.error(f"Headers: {safe_headers}")

        if kwargs.get("payload") is not None:
            logger.error(f"Payload: {kwargs['payload']}")

        if kwargs.get("params") is not None:
            logger.error(f"Params: {kwargs['params']}")

        logger.error("*" * 50)

    # Default EZO headers (Bearer and Accept JSON), if not provided.
    if headers is None:
        headers = _get_ezo_headers()

    # If Bearer token not provided, add on the default EZO headers.
    # Required for any endpoints we're hitting.
    if "Authorization" not in headers:
        headers = _get_ezo_headers(headers)

    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            timeout=kwargs.pop("timeout", DEFAULT_TIMEOUT),
            **kwargs,
        )
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        msg = f"HTTP error {context}: {e.response.status_code} - {e.response.content}"
        # 429 is retried by the tenacity
        if e.response.status_code == 429:
            logger.info(msg)
        else:
            _log_request(msg)
        raise
    except (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
        requests.exceptions.ChunkedEncodingError,
        requests.exceptions.SSLError,
    ) as e:
        msg = f"Connection error calling {context} API endpoint: {e}"
        _log_request(msg)
        raise
    except requests.exceptions.RequestException as e:
        msg = f"Request error calling {context} API endpoint: {e}"
        _log_request(msg)
        raise

    return response


def _get_paginated(
    url: str,
    headers: dict,
    results_key: str,
    context: str = "API request",
) -> list[dict]:
    """
    Fetches paginated results from an API endpoint.

    Handles pagination and applies retry logic to handle transient failures.

    :param url: The initial API endpoint URL
    :type url: str
    :param headers: HTTP headers including Authorization
    :type headers: dict
    :param results_key: The key to use for extracting results from the response JSON
    :type results_key: str
    :param context: Description for logging (e.g., "get lists", "fetch users")
    :type context: str
    :return: Flattened list of all results across pages
    :rtype: list[dict]
    """
    all_results = []

    while True:
        try:
            response = _http_request(
                method="GET",
                url=url,
                context=context,
                headers=headers,
            )
        except requests.exceptions.HTTPError:
            # Let tenacity-retried HTTP errors (429, 5XX) propagate naturally.
            raise
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.ChunkedEncodingError,
            requests.exceptions.SSLError,
        ):
            raise
        except requests.exceptions.RequestException as e:
            raise Exception(f"Pagination failed during {context}: {e}") from e

        data = response.json()
        all_results.extend(data.get(results_key, []))

        # Check for next page
        if (
            "metadata" not in data
            or "next_page" not in data["metadata"]
            or data["metadata"]["next_page"] is None
        ):
            break

        url = data["metadata"]["next_page"]

    return all_results
