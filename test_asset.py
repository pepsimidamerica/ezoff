from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff import *
from pprint import pprint

asset = get_asset_v2(asset_id=35824)

pprint(asset)

pd_asset = get_asset_v2_pd(asset_id=35824)

pprint(pd_asset.model_dump())


assets = get_assets_v2_pd(filter={})

