"""
In-memory cache for ezoff client resources.

The cache is keyed first by each resource's URL path and then by either a
resource id (for single resources) or a canonicalized filter dictionary (for
collection lookups). Persistence to disk is provided via pickle for local
development and testing workflows.
"""

import json
import logging
import pickle
from pathlib import Path

from pydantic import BaseModel

logger = logging.getLogger(__name__)


def _canonical_filter_key(filter: dict | None) -> str:
    """
    Canonicalizes a filter dictionary into a stable string key.

    The empty string represents "no filter". Otherwise the filter is serialized
    with sorted keys so that dictionaries that differ only in key ordering map
    to the same cache entry.

    :param filter: The filter dictionary to canonicalize, or None.
    :type filter: dict | None
    :return: A stable string key for the filter.
    :rtype: str
    """
    if not filter:
        return ""
    return json.dumps(filter, sort_keys=True, default=str)


class Cache:
    """
    Stores API resources keyed by path, id, and canonicalized filter.

    Single resources are stored as path -> {id: model} while collection
    results are stored as path -> {filter_key: [models]}.
    """

    def __init__(self) -> None:
        """
        Initializes an empty cache.
        """
        self._singles: dict[str, dict[int, BaseModel]] = {}
        self._collections: dict[str, dict[str, list[BaseModel]]] = {}

    # ------------------------------------------------------------------
    # Single-resource access
    # ------------------------------------------------------------------
    def get_single(self, path: str, item_id: int) -> BaseModel | None:
        """
        Returns a cached single resource, or None if not present.

        :param path: The resource's URL path.
        :type path: str
        :param item_id: The resource id.
        :type item_id: int
        :return: The cached model, or None.
        :rtype: BaseModel | None
        """
        return self._singles.get(path, {}).get(item_id)

    def set_single(self, path: str, item_id: int, model: BaseModel) -> None:
        """
        Stores a single resource in the cache.

        :param path: The resource's URL path.
        :type path: str
        :param item_id: The resource id.
        :type item_id: int
        :param model: The model to cache.
        :type model: BaseModel
        """
        self._singles.setdefault(path, {})[item_id] = model

    def pop_single(self, path: str, item_id: int) -> BaseModel | None:
        """
        Removes and returns a cached single resource.

        :param path: The resource's URL path.
        :type path: str
        :param item_id: The resource id.
        :type item_id: int
        :return: The removed model, or None if not present.
        :rtype: BaseModel | None
        """
        return self._singles.get(path, {}).pop(item_id, None)

    # ------------------------------------------------------------------
    # Collection access
    # ------------------------------------------------------------------
    def get_collection(self, path: str, filter_key: str) -> list[BaseModel] | None:
        """
        Returns a cached collection, or None if not present.

        :param path: The resource's URL path.
        :type path: str
        :param filter_key: The canonicalized filter key.
        :type filter_key: str
        :return: The cached list of models, or None.
        :rtype: list[BaseModel] | None
        """
        return self._collections.get(path, {}).get(filter_key)

    def set_collection(
        self,
        path: str,
        filter_key: str,
        models: list[BaseModel],
    ) -> None:
        """
        Stores a collection result in the cache.

        :param path: The resource's URL path.
        :type path: str
        :param filter_key: The canonicalized filter key.
        :type filter_key: str
        :param models: The list of models to cache.
        :type models: list[BaseModel]
        """
        self._collections.setdefault(path, {})[filter_key] = models

    def clear_collections(self, path: str) -> None:
        """
        Drops all cached collections for a single resource path.

        Called whenever a mutation (create/update/delete) could invalidate a
        filtered result.

        :param path: The resource's URL path.
        :type path: str
        """
        self._collections.pop(path, None)

    # ------------------------------------------------------------------
    # Whole-cache operations and persistence
    # ------------------------------------------------------------------
    def clear(self) -> None:
        """
        Clears all cached single and collection entries.
        """
        self._singles.clear()
        self._collections.clear()

    def save(self, path: Path) -> None:
        """
        Writes the cache to disk as a pickle file.

        Parent directories are created if they do not already exist.

        :param path: The file path to write to.
        :type path: Path
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as f:
            pickle.dump(
                {"singles": self._singles, "collections": self._collections},
                f,
            )
        logger.info("Saved cache to %s", path)

    def load(self, path: Path) -> None:
        """
        Loads a cache previously written by :meth:`save`.

        Existing cache entries are preserved and any loaded entries that share
        a key will overwrite them.

        :param path: The file path to load from.
        :type path: Path
        """
        path = Path(path)
        with path.open("rb") as f:
            data = pickle.load(f)
        self._singles.update(data.get("singles", {}))
        self._collections.update(data.get("collections", {}))
        logger.info("Loaded cache from %s", path)
