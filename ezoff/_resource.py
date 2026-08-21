"""
Base classes for the object-oriented ezoff resources.

A Resource represents a collection of API resources (list/create) while a
BoundResource represents a single, already-identified resource (get/update/
delete). Both have synchronous and asynchronous variants so the client can be
used in either an ordinary or an event-loop context.

Concrete resources subclass these and only need to declare their path,
model, results_key, and resource_key, plus any resource-specific
endpoints that do not fit the generic CRUD shape.
"""

import logging
from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Generic, TypeVar

import httpx2 as httpx
from ezoff._cache import _canonical_filter_key
from ezoff.data_model import ResponseMessages
from pydantic import BaseModel

if TYPE_CHECKING:
    from ezoff.client import AsyncEZOClient, EZOClient

logger = logging.getLogger(__name__)

M = TypeVar("M", bound=BaseModel)


def _parse(
    response: httpx.Response,
    key: str,
    model: type[M],
    success_status_codes: list[int] | None = None,
) -> M | None:
    """
    Deserializes a response body into a Pydantic model.

    :param response: The HTTP response to parse.
    :type response: httpx2.Response
    :param key: The JSON key to extract from the response body.
    :type key: str
    :param model: The Pydantic model to instantiate.
    :type model: type[M]
    :param success_status_codes: Status codes considered successful. If the
        response status is not in this list, returns None.
    :type success_status_codes: list[int], optional
    :return: A model instance, or None if parsing failed.
    :rtype: M | None
    """
    if (
        success_status_codes is not None
        and response.status_code not in success_status_codes
    ):
        return None

    data = response.json()
    if key in data:
        return model(**data[key])

    return None


class _ResourceConfig(Generic[M]):
    """
    Resource-specific configuration shared by sync and async resources.

    Subclasses set these class attributes to describe a single EZO API
    resource. delete_results_key and delete_model describe the shape of
    the DELETE response, which is uniform across the API.
    """

    path: str = ""
    model: type[M]
    results_key: str = ""
    resource_key: str = ""
    delete_results_key: str = "messages"
    delete_model: type[ResponseMessages] = ResponseMessages

    def _collection_url(self) -> str:
        """
        Returns the collection path for this resource.
        """
        return self.path

    def _item_url(self, item_id: int) -> str:
        """
        Returns the path for a single identified resource.
        """
        return f"{self.path}/{item_id}"

    def _validate_fields(self, data: dict) -> None:
        """
        Raises if any key is not a valid field on the resource's model.
        """
        for field in data:
            if field not in self.model.model_fields:
                raise ValueError(f"'{field}' is not a valid field for this resource.")

    def _build_filter_url(self, filter: dict | None) -> str:
        """
        Builds the collection URL, appending filters[...] query params.
        """
        if not filter:
            return self._collection_url()
        self._validate_fields(filter)
        query = "&".join(f"filters[{k}]={v}" for k, v in filter.items())
        return f"{self._collection_url()}?{query}"


class Resource(_ResourceConfig[M]):
    """
    Synchronous collection resource.
    """

    def __init__(self, client: "EZOClient") -> None:
        """
        Initializes the resource with the given client.
        """
        self._client = client

    def __call__(self, item_id: int) -> "BoundResource[M]":
        """
        Returns a bound resource for a single identified item.
        """
        return BoundResource(self._client, self, item_id)

    def list(
        self,
        filter: dict | None = None,
        force: bool = False,
    ) -> list[M]:
        """
        Returns all resources as a list, optionally filtered.

        :param filter: A dictionary of fields to filter by.
        :type filter: dict, optional
        :param force: If True, bypasses the cache and fetches from the API.
        :type force: bool
        :return: The list of resource models.
        :rtype: list[M]
        """
        if not self._client._caching:
            return list(self.iter(filter))

        path = self._collection_url()
        key = _canonical_filter_key(filter)

        if not force:
            cached = self._client.cache.get_collection(path, key)
            if cached is not None:
                return cached

        results = list(self.iter(filter))
        self._client.cache.set_collection(path, key, results)
        return results

    def iter(self, filter: dict | None = None) -> Iterator[M]:
        """
        Lazily yields resources across all pages, optionally filtered.
        """
        url = self._build_filter_url(filter)
        while url:
            response = self._client._transport.request(
                "GET", url, context="Resource List"
            )
            data = response.json()
            for item in data.get(self.results_key, []):
                yield self.model(**item)
            url = data.get("metadata", {}).get("next_page")

    def create(self, data: dict) -> M | None:
        """
        Creates a new resource and returns the created model.
        """
        response = self._client._transport.request(
            "POST",
            self._collection_url(),
            json={self.resource_key: data},
            context="Resource Create",
        )
        model = _parse(
            response,
            self.resource_key,
            self.model,
            success_status_codes=[200],
        )
        if self._client._caching and model is not None:
            item_id = getattr(model, "id", None)
            if isinstance(item_id, int):
                self._client.cache.set_single(self._item_url(item_id), item_id, model)
            self._client.cache.clear_collections(self._collection_url())
        return model


class BoundResource(Generic[M]):
    """
    Synchronous, identified single resource.
    """

    def __init__(
        self,
        client: "EZOClient",
        resource: Resource[M],
        item_id: int,
    ) -> None:
        """
        Initializes the resource with the given client, resource, and item ID.
        """
        self._client = client
        self._resource = resource
        self.id = item_id

    def get(self, force: bool = False) -> M | None:
        """
        Fetches this resource and returns the model.

        :param force: If True, bypasses the cache and fetches from the API.
        :type force: bool
        :return: The resource model, or None.
        :rtype: M | None
        """
        path = self._resource._item_url(self.id)
        if not force and self._client._caching:
            cached = self._client.cache.get_single(path, self.id)
            if cached is not None:
                return cached

        response = self._client._transport.request("GET", path, context="Resource Get")
        model = _parse(
            response,
            self._resource.resource_key,
            self._resource.model,
            success_status_codes=[200],
        )
        if self._client._caching and model is not None:
            self._client.cache.set_single(path, self.id, model)
        return model

    def update(self, data: dict) -> M | None:
        """
        Updates this resource with the given fields and returns the result.
        """
        self._resource._validate_fields(data)
        response = self._client._transport.request(
            "PATCH",
            self._resource._item_url(self.id),
            json={self._resource.resource_key: data},
            context="Resource Update",
        )
        model = _parse(
            response,
            self._resource.resource_key,
            self._resource.model,
            success_status_codes=[200],
        )
        if model is not None and self._client._caching:
            self._client.cache.set_single(
                self._resource._item_url(self.id), self.id, model
            )
            self._client.cache.clear_collections(self._resource._collection_url())
        return model

    def delete(self) -> ResponseMessages | None:
        """
        Deletes this resource and returns any response messages.
        """
        response = self._client._transport.request(
            "DELETE", self._resource._item_url(self.id), context="Resource Delete"
        )
        result = _parse(
            response,
            self._resource.delete_results_key,
            self._resource.delete_model,
            success_status_codes=[200],
        )
        if self._client._caching:
            self._client.cache.pop_single(self._resource._item_url(self.id), self.id)
            self._client.cache.clear_collections(self._resource._collection_url())
        return result

    def refresh(self) -> M | None:
        """
        Re-fetches this resource and returns the latest model, bypassing cache.
        """
        return self.get(force=True)


class AsyncResource(_ResourceConfig[M]):
    """
    Asynchronous collection resource.
    """

    def __init__(self, client: "AsyncEZOClient") -> None:
        """
        Initializes the resource with the given client.
        """
        self._client = client

    def __call__(self, item_id: int) -> "AsyncBoundResource[M]":
        """
        Returns a bound resource for a single identified item.
        """
        return AsyncBoundResource(self._client, self, item_id)

    async def alist(
        self,
        filter: dict | None = None,
        force: bool = False,
    ) -> list[M]:
        """
        Returns all resources as a list, optionally filtered.

        :param filter: A dictionary of fields to filter by.
        :type filter: dict, optional
        :param force: If True, bypasses the cache and fetches from the API.
        :type force: bool
        :return: The list of resource models.
        :rtype: list[M]
        """
        if not self._client._caching:
            return [item async for item in self.aiter(filter)]

        path = self._collection_url()
        key = _canonical_filter_key(filter)

        if not force:
            cached = self._client.cache.get_collection(path, key)
            if cached is not None:
                return cached

        results = [item async for item in self.aiter(filter)]
        self._client.cache.set_collection(path, key, results)
        return results

    async def aiter(self, filter: dict | None = None) -> AsyncIterator[M]:
        """
        Asynchronously yields resources across all pages, optionally filtered.
        """
        url = self._build_filter_url(filter)
        while url:
            response = await self._client._transport.request(
                "GET", url, context="Resource List"
            )
            data = response.json()
            for item in data.get(self.results_key, []):
                yield self.model(**item)
            url = data.get("metadata", {}).get("next_page")

    async def acreate(self, data: dict) -> M | None:
        """
        Creates a new resource and returns the created model.
        """
        response = await self._client._transport.request(
            "POST",
            self._collection_url(),
            json={self.resource_key: data},
            context="Resource Create",
        )
        model = _parse(
            response,
            self.resource_key,
            self.model,
            success_status_codes=[200],
        )
        if self._client._caching and model is not None:
            item_id = getattr(model, "id", None)
            if isinstance(item_id, int):
                self._client.cache.set_single(self._item_url(item_id), item_id, model)
            self._client.cache.clear_collections(self._collection_url())
        return model


class AsyncBoundResource(Generic[M]):
    """
    Asynchronous, identified single resource.
    """

    def __init__(
        self,
        client: "AsyncEZOClient",
        resource: AsyncResource[M],
        item_id: int,
    ) -> None:
        """
        Initializes the resource with the given client, resource, and item ID.
        """
        self._client = client
        self._resource = resource
        self.id = item_id

    async def aget(self, force: bool = False) -> M | None:
        """
        Fetches this resource and returns the model.

        :param force: If True, bypasses the cache and fetches from the API.
        :type force: bool
        :return: The resource model, or None.
        :rtype: M | None
        """
        path = self._resource._item_url(self.id)
        if not force and self._client._caching:
            cached = self._client.cache.get_single(path, self.id)
            if cached is not None:
                return cached

        response = await self._client._transport.request(
            "GET", path, context="Resource Get"
        )
        model = _parse(
            response,
            self._resource.resource_key,
            self._resource.model,
            success_status_codes=[200],
        )
        if self._client._caching and model is not None:
            self._client.cache.set_single(path, self.id, model)
        return model

    async def aupdate(self, data: dict) -> M | None:
        """
        Updates this resource with the given fields and returns the result.
        """
        self._resource._validate_fields(data)
        response = await self._client._transport.request(
            "PATCH",
            self._resource._item_url(self.id),
            json={self._resource.resource_key: data},
            context="Resource Update",
        )
        model = _parse(
            response,
            self._resource.resource_key,
            self._resource.model,
            success_status_codes=[200],
        )
        if model is not None and self._client._caching:
            self._client.cache.set_single(
                self._resource._item_url(self.id), self.id, model
            )
            self._client.cache.clear_collections(self._resource._collection_url())
        return model

    async def adelete(self) -> ResponseMessages | None:
        """
        Deletes this resource and returns any response messages.
        """
        response = await self._client._transport.request(
            "DELETE", self._resource._item_url(self.id), context="Resource Delete"
        )
        result = _parse(
            response,
            self._resource.delete_results_key,
            self._resource.delete_model,
            success_status_codes=[200],
        )
        if self._client._caching:
            self._client.cache.pop_single(self._resource._item_url(self.id), self.id)
            self._client.cache.clear_collections(self._resource._collection_url())
        return result

    async def arefresh(self) -> M | None:
        """
        Re-fetches this resource and returns the latest model, bypassing cache.
        """
        return await self.aget(force=True)
