"""
Async-friendly HTTP transport for the ezoff client.

This module owns the low-level concerns of talking to the EZOffice API:
building URLs, attaching auth headers, retrying transient failures, and
turning requests into httpx2.Response objects.

Both a synchronous and an asynchronous transport are provided so the rest of
the client does not need to know which event loop it is running under.
"""

import logging
import random
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Literal

import httpx2 as httpx
from tenacity import (
    after_log,
    before_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
)

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60.0

HTTPMethod = Literal["GET", "POST", "PATCH", "DELETE", "PUT", "HEAD", "OPTIONS"]


def _should_retry(exception: BaseException) -> bool:
    """
    Determines if an exception warrants a retry.

    Retries on transport errors (connection, timeout, protocol) and on
    HTTP 429 (rate limit) or 5XX server errors.

    :param exception: The exception to evaluate.
    :type exception: BaseException
    :return: True if the exception warrants a retry, False otherwise.
    :rtype: bool
    """
    if isinstance(
        exception,
        (httpx.TimeoutException, httpx.NetworkError, httpx.ProtocolError),
    ):
        return True
    if isinstance(exception, httpx.HTTPStatusError):
        status = exception.response.status_code
        return status == 429 or 500 <= status < 600
    return False


def _wait_for_retry(retry_state) -> float:
    """
    Custom wait strategy for tenacity retries.

    On HTTP 429 (rate limit), respects the Retry-After header if present and
    falls back to a 60-second wait otherwise. For all other retryable errors,
    uses exponential backoff with jitter.

    :param retry_state: The current retry state from tenacity.
    :type retry_state: tenacity.RetryCallState
    :return: Number of seconds to wait before retrying.
    :rtype: float
    """
    if retry_state.outcome and retry_state.outcome.failed:
        exception = retry_state.outcome.exception()
        if isinstance(exception, httpx.HTTPStatusError):
            response = exception.response
            if response.status_code == 429:
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
                logger.info(
                    "Rate limited (429). No valid Retry-After header, waiting 60s."
                )
                return 60.0

    # Exponential backoff with jitter for all other retryable errors.
    base = min(2 ** (retry_state.attempt_number - 1) * 4, 120)
    jitter = base * 0.25 * (random.random() * 2 - 1)  # +-25%
    return max(0, base + jitter)


_retry = retry(
    stop=stop_after_attempt(5),
    wait=_wait_for_retry,
    retry=retry_if_exception(_should_retry),
    before=before_log(logger, logging.DEBUG),
    after=after_log(logger, logging.DEBUG),
)


def _log_error(
    method: str,
    url: str,
    headers: dict | None,
    kwargs: dict,
    message: str,
) -> None:
    """
    Logs the details of a failed request, redacting the bearer token.

    :param method: The HTTP method used for the request.
    :type method: str
    :param url: The full request URL.
    :type url: str
    :param headers: The request headers (may be None).
    :type headers: dict | None
    :param kwargs: The keyword arguments passed to the request.
    :type kwargs: dict
    :param message: The error message to log.
    :type message: str
    """
    logger.error("*" * 50)
    logger.error(message)
    logger.error(f"HTTP Method: {method}")
    logger.error(f"URL: {url}")

    if headers is not None:
        safe_headers = headers.copy()
        if "Authorization" in safe_headers:
            safe_headers["Authorization"] = "REDACTED"
        logger.error(f"Headers: {safe_headers}")

    if kwargs.get("json") is not None:
        logger.error(f"Payload: {kwargs['json']}")

    if kwargs.get("params") is not None:
        logger.error(f"Params: {kwargs['params']}")

    logger.error("*" * 50)


class BaseTransport:
    """
    Shared configuration for EZO transports.

    Holds the base URL and default auth headers. Concrete subclasses own the
    underlying httpx2 client and implement the request method in either
    a synchronous or asynchronous form.
    """

    def __init__(
        self,
        subdomain: str,
        token: str,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self._base_url = f"https://{subdomain}.ezofficeinventory.com"
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        self._timeout = timeout

    def _url(self, path: str) -> str:
        """
        Builds a full URL from a path, passing through already-full URLs.

        Pagination returns absolute next_page URLs, so this tolerates both
        a bare path and an absolute URL.

        :param path: A URL path or an absolute URL.
        :type path: str
        :return: The absolute URL.
        :rtype: str
        """
        if path.startswith(("http://", "https://")):
            return path
        return f"{self._base_url}{path}"

    def _headers_with(self, extra_headers: dict | None) -> dict:
        """
        Merges default auth headers with any per-request overrides.

        :param extra_headers: Additional headers to merge in.
        :type extra_headers: dict | None
        :return: The merged headers.
        :rtype: dict
        """
        if not extra_headers:
            return self._headers
        if "Authorization" in extra_headers:
            return extra_headers
        return {**self._headers, **extra_headers}


class SyncTransport(BaseTransport):
    """
    Synchronous EZO transport backed by httpx2.Client.
    """

    def __init__(
        self,
        subdomain: str,
        token: str,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        super().__init__(subdomain, token, timeout)
        self._client = httpx.Client(timeout=self._timeout)

    @_retry
    def request(
        self,
        method: HTTPMethod,
        path: str,
        headers: dict | None = None,
        context: str = "HTTP Request",
        **kwargs,
    ) -> httpx.Response:
        """
        Performs a synchronous HTTP request with standardized error handling.

        :param method: The HTTP method to use.
        :type method: HTTPMethod
        :param path: The URL path (or absolute URL) to request.
        :type path: str
        :param headers: Optional per-request headers.
        :type headers: dict, optional
        :param context: Human-readable context for error messages.
        :type context: str
        :param kwargs: Additional arguments passed to httpx2.Client.request.
        :return: The HTTP response.
        :rtype: httpx2.Response
        """
        url = self._url(path)
        headers = self._headers_with(headers)

        try:
            response = self._client.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            msg = (
                f"HTTP error {context}: {e.response.status_code} - {e.response.content}"
            )
            if e.response.status_code == 429:
                logger.info(msg)
            else:
                _log_error(method, url, headers, kwargs, msg)
            raise
        except httpx.TransportError as e:
            msg = f"Connection error calling {context} API endpoint: {e}"
            _log_error(method, url, headers, kwargs, msg)
            raise
        except httpx.RequestError as e:
            msg = f"Request error calling {context} API endpoint: {e}"
            _log_error(method, url, headers, kwargs, msg)
            raise

        return response

    def close(self) -> None:
        """
        Closes the underlying HTTP client.
        """
        self._client.close()

    def __enter__(self) -> "SyncTransport":
        return self

    def __exit__(self, *exc) -> None:
        self.close()


class AsyncTransport(BaseTransport):
    """
    Asynchronous EZO transport backed by httpx2.AsyncClient.
    """

    def __init__(
        self,
        subdomain: str,
        token: str,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        super().__init__(subdomain, token, timeout)
        self._client = httpx.AsyncClient(timeout=self._timeout)

    @_retry
    async def request(
        self,
        method: HTTPMethod,
        path: str,
        headers: dict | None = None,
        context: str = "HTTP Request",
        **kwargs,
    ) -> httpx.Response:
        """
        Performs an asynchronous HTTP request with standardized error handling.

        :param method: The HTTP method to use.
        :type method: HTTPMethod
        :param path: The URL path (or absolute URL) to request.
        :type path: str
        :param headers: Optional per-request headers.
        :type headers: dict, optional
        :param context: Human-readable context for error messages.
        :type context: str
        :param kwargs: Additional arguments passed to httpx2.AsyncClient.request.
        :return: The HTTP response.
        :rtype: httpx2.Response
        """
        url = self._url(path)
        headers = self._headers_with(headers)

        try:
            response = await self._client.request(
                method, url, headers=headers, **kwargs
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            msg = (
                f"HTTP error {context}: {e.response.status_code} - {e.response.content}"
            )
            if e.response.status_code == 429:
                logger.info(msg)
            else:
                _log_error(method, url, headers, kwargs, msg)
            raise
        except httpx.TransportError as e:
            msg = f"Connection error calling {context} API endpoint: {e}"
            _log_error(method, url, headers, kwargs, msg)
            raise
        except httpx.RequestError as e:
            msg = f"Request error calling {context} API endpoint: {e}"
            _log_error(method, url, headers, kwargs, msg)
            raise

        return response

    async def close(self) -> None:
        """
        Closes the underlying async HTTP client.
        """
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncTransport":
        return self

    async def __aexit__(self, *exc) -> None:
        await self.close()
