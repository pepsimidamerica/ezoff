from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff import *


def update_asset_rent(asset: AssetV2, rent: bool):
    current_rent_value = False

    # print(asset.custom_fields)
    for cust in asset.custom_fields:
        # print(cust)
        if cust['id'] == 70779 and cust['value'] == ['Rent']:
            current_rent_value = True
            print('Has rent currently.')

    if current_rent_value != rent:
        payload = {
            "asset": {
                "name": asset.name,
                "purchased_on": asset.purchased_on.strftime('%Y-%m-%dT%H:%M:%S'),
                "group_id": asset.group_id,
                "custom_fields": [{"id": 70779}],
            }
        }

        if rent:
            payload['asset']['custom_fields'][0]['value'] = ['Rent']

        pprint(payload)

        result = update_asset_v2(asset_id=asset.id, payload=payload)
        # print(result)


asset = get_asset_v2_pd(26933)
update_asset_rent(asset=asset, rent=True)
