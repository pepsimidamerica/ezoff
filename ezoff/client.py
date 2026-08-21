"""
Object-oriented, async-friendly entry point for the ezoff client.

EZOClient and AsyncEZOClient expose resources as attributes
(e.g. client.vendors) and provide ergonomic accessors for a single
identified resource (e.g. client.vendor(3)).
"""

import os
from pathlib import Path

from ezoff._cache import Cache
from ezoff._http import DEFAULT_TIMEOUT, AsyncTransport, SyncTransport
from ezoff._resource import AsyncBoundResource, BoundResource
from ezoff.assets import AssetResource, AsyncAssetResource
from ezoff.bundle import AsyncBundleResource, BundleResource
from ezoff.data_model import Asset, Bundle, Vendor
from ezoff.vendors import AsyncVendorResource, VendorResource


class EZOClient:
    """
    Synchronous EZOffice API client.

    Subdomain and token are read from EZO_SUBDOMAIN and EZO_TOKEN
    environment variables unless provided explicitly.
    """

    def __init__(
        self,
        subdomain: str | None = None,
        token: str | None = None,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        caching: bool = False,
        cache_path: Path | None = None,
    ) -> None:
        """
        Initializes the EZOClient.
        """
        subdomain = subdomain or os.environ.get("EZO_SUBDOMAIN")
        token = token or os.environ.get("EZO_TOKEN")
        if not subdomain:
            raise ValueError("EZO_SUBDOMAIN not found in environment variables.")
        if not token:
            raise ValueError("EZO_TOKEN not found in environment variables.")

        self._transport = SyncTransport(subdomain, token, timeout=timeout)

        self._caching = caching
        self._cache_path = cache_path
        self.cache = Cache()
        if caching or cache_path is not None:
            self._caching = True
        if cache_path is not None and cache_path.exists():
            self.cache.load(cache_path)

        # Resources
        self.assets: AssetResource = AssetResource(self)
        self.bundles: BundleResource = BundleResource(self)
        self.vendors: VendorResource = VendorResource(self)

    def asset(self, asset_id: int) -> BoundResource[Asset]:
        """
        Returns a bound resource for a single asset.
        """
        return self.assets(asset_id)

    def bundle(self, bundle_id: int) -> BoundResource[Bundle]:
        """
        Returns a bound resource for a single bundle.
        """
        return self.bundles(bundle_id)

    def vendor(self, vendor_id: int) -> BoundResource[Vendor]:
        """
        Returns a bound resource for a single vendor.
        """
        return self.vendors(vendor_id)

    def close(self) -> None:
        """
        Closes the underlying HTTP client.
        """
        if self._cache_path is not None:
            self.cache.save(self._cache_path)
        self._transport.close()

    def __enter__(self) -> "EZOClient":
        """
        Enters the context manager, returning the client instance.
        """
        return self

    def __exit__(self, *exc) -> None:
        """
        Exits the context manager, closing the client.
        """
        self.close()


class AsyncEZOClient:
    """
    Asynchronous EZOffice API client.

    Subdomain and token are read from EZO_SUBDOMAIN and EZO_TOKEN
    environment variables unless provided explicitly.
    """

    def __init__(
        self,
        subdomain: str | None = None,
        token: str | None = None,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        caching: bool = False,
        cache_path: Path | None = None,
    ) -> None:
        subdomain = subdomain or os.environ.get("EZO_SUBDOMAIN")
        token = token or os.environ.get("EZO_TOKEN")
        if not subdomain:
            raise ValueError("EZO_SUBDOMAIN not found in environment variables.")
        if not token:
            raise ValueError("EZO_TOKEN not found in environment variables.")

        self._transport = AsyncTransport(subdomain, token, timeout=timeout)

        self._caching = caching
        self._cache_path = cache_path
        self.cache = Cache()
        if caching or cache_path is not None:
            self._caching = True
        if cache_path is not None and cache_path.exists():
            self.cache.load(cache_path)

        # EZoffice Resources
        self.assets: AsyncAssetResource = AsyncAssetResource(self)
        self.bundles: AsyncBundleResource = AsyncBundleResource(self)
        self.vendors: AsyncVendorResource = AsyncVendorResource(self)

    def asset(self, asset_id: int) -> AsyncBoundResource[Asset]:
        """
        Returns a bound resource for a single asset.
        """
        return self.assets(asset_id)

    def bundle(self, bundle_id: int) -> AsyncBoundResource[Bundle]:
        """
        Returns a bound resource for a single bundle.
        """
        return self.bundles(bundle_id)

    def vendor(self, vendor_id: int) -> AsyncBoundResource[Vendor]:
        """
        Returns a bound resource for a single vendor.
        """
        return self.vendors(vendor_id)

    async def close(self) -> None:
        """
        Closes the underlying async HTTP client.
        """
        if self._cache_path is not None:
            self.cache.save(self._cache_path)
        await self._transport.close()

    async def __aenter__(self) -> "AsyncEZOClient":
        return self

    async def __aexit__(self, *exc) -> None:
        await self.close()
