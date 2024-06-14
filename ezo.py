import json
import os
from datetime import datetime, timedelta
from pprint import pprint
from tabnanny import check
from typing import Literal, Optional

import requests


class Decorators:

    @staticmethod
    def check_env_vars(decorated):
        """
        Decorator to check if the required environment variables are set
        """

        def wrapper(*args, **kwargs):
            """
            Wrapper function
            """
            if "EZO_BASE_URL" not in os.environ:
                raise Exception("EZO_BASE_URL not found in environment variables.")
            if "EZO_TOKEN" not in os.environ:
                raise Exception("EZO_TOKEN not found in environment variables.")
            return decorated(*args, **kwargs)

        wrapper.__name__ = decorated.__name__
        return wrapper


@Decorators.check_env_vars
def get_members(filter: Optional[dict]) -> list[dict]:
    """
    Get members from EZOfficeInventory
    Optionally filter by email, employee_identification_number, or status
    https://ezo.io/ezofficeinventory/developers/#api-retrieve-members
    """

    if filter is not None:
        if "filter" not in filter or "filter_val" not in filter:
            raise ValueError("filter must have 'filter' and 'filter_val' keys")
        if filter["filter"] not in [
            "email",
            "employee_identification_number",
            "status",
        ]:
            raise ValueError(
                "filter['filter'] must be one of 'email', 'employee_identification_number', 'status'"
            )

    url = os.environ["EZO_BASE_URL"] + "members.api"

    page = 1
    all_members = []

    while True:
        params = {"page": page, "include_custom_fields": "true"}
        if filter is not None:
            params.update(filter)

        try:
            response = requests.get(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params=params,
                timeout=10,
            )
        except Exception as e:
            print("Error, could not get members from EZOfficeInventory: ", e)
            raise Exception(
                "Error, could not get members from EZOfficeInventory: " + str(e)
            )

        if response.status_code != 200:
            print(
                f"Error {response.status_code}, could not get members from EZOfficeInventory: ",
                response.content,
            )
            break

        data = response.json()
        if "members" not in data:
            print(
                f"Error, could not get members from EZOfficeInventory: ",
                response.content,
            )
            raise Exception(
                f"Error, could not get members from EZOfficeInventory: "
                + str(response.content)
            )

        all_members.extend(data["members"])

        if "total_pages" not in data:
            print("Error, could not get total_pages from EZOfficeInventory: ", data)
            break

        if page >= data["total_pages"]:
            break

        page += 1

    return all_members


@Decorators.check_env_vars
def get_member_details(member_id: int) -> dict:
    """
    Get member from EZOfficeInventory by member_id
    https://ezo.io/ezofficeinventory/developers/#api-member-details
    """

    url = os.environ["EZO_BASE_URL"] + "members/" + str(member_id) + ".api"

    try:
        response = requests.get(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            params={"include_custom_fields": "true"},
            timeout=10,
        )
    except Exception as e:
        print("Error, could not get member from EZOfficeInventory: ", e)
        raise Exception("Error, could not get member from EZOfficeInventory: " + str(e))

    if response.status_code != 200:
        print(
            f"Error {response.status_code}, could not get member from EZOfficeInventory: ",
            response.content,
        )
        raise Exception(
            f"Error {response.status_code}, could not get member from EZOfficeInventory: "
            + str(response.content)
        )

    return response.json()


@Decorators.check_env_vars
def create_member(member: dict) -> dict:
    """
    Create a new member
    https://ezo.io/ezofficeinventory/developers/#api-create-member
    """

    # Required fields
    if "user[email]" not in member:
        raise ValueError("member must have 'user[email]' key")
    if "user[first_name]" not in member:
        raise ValueError("member must have 'user[first_name]' key")
    if "user[last_name]" not in member:
        raise ValueError("member must have 'user[last_name]' key")
    if "user[role_id]" not in member:
        raise ValueError("member must have 'user[role_id]' key")

    # Remove any keys that are not valid
    valid_keys = [
        "user[email]",
        "user[employee_id]",
        "user[role_id]",
        "user[team_id]",
        "user[user_listing_id]",
        "user[first_name]",
        "user[last_name]",
        "user[address_name]",
        "user[address]",
        "user[address_line_2]",
        "user[city]",
        "user[state]",
        "user[country]",
        "user[phone_number]",
        "user[fax]",
        "user[login_enabled]",
        "user[subscribed_to_emails]",
        "skip_confirmation_email",
    ]

    # Check for custom attributes
    member = {
        k: v
        for k, v in member.items()
        if k in valid_keys or k.startswith("user[custom_attributes]")
    }

    url = os.environ["EZO_BASE_URL"] + "members.api"

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data=member,
            timeout=10,
        )
    except Exception as e:
        print("Error, could not create member in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not create member in EZOfficeInventory: " + str(e)
        )

    return response.json()


@Decorators.check_env_vars
def update_member(member_id: int, member: dict) -> dict:
    """
    Update a member
    https://ezo.io/ezofficeinventory/developers/#api-update-member
    """

    # Remove any keys that are not valid
    valid_keys = [
        "user[email]",
        "user[employee_id]",
        "user[role_id]",
        "user[team_id]",
        "user[user_listing_id]",
        "user[first_name]",
        "user[last_name]",
        "user[phone_number]",
        "user[fax]",
        "skip_confirmation_email",
    ]

    # Check for custom attributes
    member = {
        k: v
        for k, v in member.items()
        if k in valid_keys or k.startswith("user[custom_attributes]")
    }

    url = os.environ["EZO_BASE_URL"] + "members/" + str(member_id) + ".api"

    try:
        response = requests.put(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data=member,
            timeout=10,
        )
    except Exception as e:
        print("Error, could not update member in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not update member in EZOfficeInventory: " + str(e)
        )

    return response.json()


@Decorators.check_env_vars
def get_custom_roles() -> list[dict]:
    """
    Get list of custom roles
    Results are technically paginated but the number of custom roles
    is usually small enough that it can be returned in one page.
    https://ezo.io/ezofficeinventory/developers/#api-retrieve-roles
    """

    url = os.environ["EZO_BASE_URL"] + "custom_roles.api"

    pages = 1
    all_custom_roles = []

    while True:
        try:
            response = requests.get(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params={"page": pages},
                timeout=10,
            )
        except Exception as e:
            print("Error, could not get custom roles from EZOfficeInventory: ", e)
            raise Exception(
                "Error, could not get custom roles from EZOfficeInventory: " + str(e)
            )

        if response.status_code != 200:
            print(
                f"Error {response.status_code}, could not get custom roles from EZOfficeInventory: ",
                response.content,
            )
            break

        data = response.json()

        if "custom_roles" not in data:
            print(
                f"Error, could not get custom roles from EZOfficeInventory: ",
                response.content,
            )
            raise Exception(
                f"Error, could not get custom roles from EZOfficeInventory: "
                + str(response.content)
            )

        all_custom_roles.extend(data["custom_roles"])

        if "total_pages" not in data:
            print("Error, could not get total_pages from EZOfficeInventory: ", data)
            break

        if pages >= data["total_pages"]:
            break

        pages += 1

    return all_custom_roles


@Decorators.check_env_vars
def get_teams() -> list[dict]:
    """
    Get teams
    https://ezo.io/ezofficeinventory/developers/#api-retrieve-teams
    """

    url = os.environ["EZO_BASE_URL"] + "teams.api"

    page = 1
    all_teams = []

    while True:
        try:
            response = requests.get(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params={"page": page},
                timeout=10,
            )
        except Exception as e:
            print("Error, could not get teams from EZOfficeInventory: ", e)
            raise Exception(
                "Error, could not get teams from EZOfficeInventory: " + str(e)
            )

        if response.status_code != 200:
            print(
                f"Error {response.status_code}, could not get teams from EZOfficeInventory: ",
                response.content,
            )
            break

        data = response.json()

        if "teams" not in data:
            print(
                f"Error, could not get teams from EZOfficeInventory: ",
                response.content,
            )
            raise Exception(
                f"Error, could not get teams from EZOfficeInventory: "
                + str(response.content)
            )

        all_teams.extend(data["teams"])

        if "total_pages" not in data:
            print("Error, could not get total_pages from EZOfficeInventory: ", data)
            break

        if page >= data["total_pages"]:
            break

        page += 1

    return all_teams


@Decorators.check_env_vars
def get_locations(filter: Optional[dict]) -> list[dict]:
    """
    Get locations
    Optionally filter by status
    https://ezo.io/ezofficeinventory/developers/#api-retreive-locations
    """
    if filter is not None:
        if "status" not in filter:
            raise ValueError("filter must have 'status' key")
        if filter["status"] not in ["all", "active", "inactive"]:
            raise ValueError(
                "filter['status'] must be one of 'all', 'active', 'inactive'"
            )

    url = os.environ["EZO_BASE_URL"] + "locations/get_line_item_locations.api"

    page = 1
    all_locations = []

    while True:
        params = {"page": page, "include_custom_fields": "true"}
        if filter is not None:
            params.update(filter)

        try:
            response = requests.get(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params=params,
                timeout=10,
            )
        except Exception as e:
            print("Error, could not get locations from EZOfficeInventory: ", e)
            raise Exception(
                "Error, could not get locations from EZOfficeInventory: " + str(e)
            )

        if response.status_code != 200:
            print(
                f"Error {response.status_code}, could not get locations from EZOfficeInventory: ",
                response.content,
            )
            break

        data = response.json()
        if "locations" not in data:
            print(
                f"Error, could not get locations from EZOfficeInventory: ",
                response.content,
            )
            raise Exception(
                f"Error, could not get locations from EZOfficeInventory: "
                + str(response.content)
            )

        all_locations.extend(data["locations"])

        if "total_pages" not in data:
            print("Error, could not get total_pages from EZOfficeInventory: ", data)
            break

        if page >= data["total_pages"]:
            break

        page += 1

    return all_locations


@Decorators.check_env_vars
def get_location_details(location_num: int) -> dict:
    """
    Get location details
    https://ezo.io/ezofficeinventory/developers/#api-location-details
    """

    url = os.environ["EZO_BASE_URL"] + "locations/" + str(location_num) + ".api"

    try:
        response = requests.get(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            params={"include_custom_fields": "true"},
            timeout=10,
        )
    except Exception as e:
        print("Error, could not get location from EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not get location from EZOfficeInventory: " + str(e)
        )

    if response.status_code != 200:
        print(
            f"Error {response.status_code}, could not get location from EZOfficeInventory: ",
            response.content,
        )
        raise Exception(
            f"Error {response.status_code}, could not get location from EZOfficeInventory: "
            + str(response.content)
        )

    return response.json()


@Decorators.check_env_vars
def create_location(location: dict) -> dict:
    """
    Create a location
    https://ezo.io/ezofficeinventory/developers/#api-create-location
    """

    # Required fields
    if "location[name]" not in location:
        raise ValueError("location must have 'location[name]' key")

    # Remove any keys that are not valid
    valid_keys = [
        "location[parent_id]",
        "location[name]",
        "location[city]",
        "location[state]",
        "location[zipcode]",
        "location[street1]",
        "location[street2]",
        "location[status]",
        "location[description]",
    ]

    location = {k: v for k, v in location.items() if k in valid_keys}

    if "location[status]" in location:
        if location["location[status]"] not in ["active", "inactive"]:
            raise ValueError(
                "location['location[status]'] must be one of 'active', 'inactive'"
            )

    url = os.environ["EZO_BASE_URL"] + "locations.api"

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data=location,
        )
    except Exception as e:
        print("Error, could not create location in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not create location in EZOfficeInventory: " + str(e)
        )

    return response.json()


@Decorators.check_env_vars
def get_all_assets() -> list[dict]:
    """
    Get assets
    Recommended to use endpoint that takes a filter instead.
    This endpoint can be slow as it returns all assets in the system. Potentially
    several hundred pages of assets.
    https://ezo.io/ezofficeinventory/developers/#api-retrive-assets
    """

    url = os.environ["EZO_BASE_URL"] + "assets.api"

    page = 1
    all_assets = []

    while True:
        params = {"page": page}

        try:
            response = requests.get(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params=params,
                data={
                    "include_custom_fields": "true",
                    "show_document_urls": "true",
                    "show_image_urls": "true",
                },
                timeout=10,
            )
        except Exception as e:
            print("Error, could not get assets from EZOfficeInventory: ", e)
            raise Exception(
                "Error, could not get assets from EZOfficeInventory: " + str(e)
            )

        if response.status_code != 200:
            print(
                f"Error {response.status_code}, could not get assets from EZOfficeInventory: ",
                response.content,
            )
            break

        data = response.json()

        if "assets" not in data:
            print(
                f"Error, could not get assets from EZOfficeInventory: ",
                response.content,
            )
            raise Exception(
                f"Error, could not get assets from EZOfficeInventory: "
                + str(response.content)
            )

        all_assets.extend(data["assets"])

        if "total_pages" not in data:
            print("Error, could not get total_pages from EZOfficeInventory: ", data)
            break

        if page >= data["total_pages"]:
            break

        page += 1

    return all_assets


@Decorators.check_env_vars
def get_filtered_assets(filter: dict) -> list[dict]:
    """
    Get assets via filtering. Recommended to use this endpoint rather than
    returning all assets.
    """
    if "status" not in filter:
        raise ValueError("filter must have 'status' key")

    url = os.environ["EZO_BASE_URL"] + "assets/filter.api"

    page = 1
    all_assets = []

    while True:
        params = {"page": page}
        params.update(filter)

        try:
            response = requests.get(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params=params,
                data={
                    "include_custom_fields": "true",
                    "show_document_urls": "true",
                    "show_image_urls": "true",
                },
                timeout=10,
            )
        except Exception as e:
            print("Error, could not get assets from EZOfficeInventory: ", e)
            raise Exception(
                "Error, could not get assets from EZOfficeInventory: " + str(e)
            )

        if response.status_code != 200:
            print(
                f"Error {response.status_code}, could not get assets from EZOfficeInventory: ",
                response.content,
            )
            break

        data = response.json()

        if "assets" not in data:
            print(
                f"Error, could not get assets from EZOfficeInventory: ",
                response.content,
            )
            raise Exception(
                f"Error, could not get assets from EZOfficeInventory: "
                + str(response.content)
            )

        all_assets.extend(data["assets"])

        if "total_pages" not in data:
            print("Error, could not get total_pages from EZOfficeInventory: ", data)
            break

        if page >= data["total_pages"]:
            break

        page += 1

    return all_assets


@Decorators.check_env_vars
def search_for_asset(search_term: str) -> list[dict]:
    """
    Search for an asset.
    The equivalent of the search bar in the EZOfficeInventory UI.
    May not return all assets that match the search term. Better to use
    get_filtered_assets if you want to return all assets that match a filter.
    https://ezo.io/ezofficeinventory/developers/#api-search-name
    """

    url = os.environ["EZO_BASE_URL"] + "search.api"

    page = 1
    all_assets = []

    while True:
        data = {
            "page": page,
            "search": search_term,
            "facet": "FixedAsset",
            "include_custom_fields": "true",
            "show_document_urls": "true",
            "show_image_urls": "true",
            "show_document_details": "true",
        }

        try:
            response = requests.get(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                data=data,
                timeout=10,
            )
        except Exception as e:
            print("Error, could not get assets from EZOfficeInventory: ", e)
            raise Exception(
                "Error, could not get assets from EZOfficeInventory: " + str(e)
            )

        if response.status_code != 200:
            print(
                f"Error {response.status_code}, could not get assets from EZOfficeInventory: ",
                response.content,
            )
            break

        data = response.json()

        if "assets" not in data:
            print(
                f"Error, could not get assets from EZOfficeInventory: ",
                response.content,
            )
            raise Exception(
                f"Error, could not get assets from EZOfficeInventory: "
                + str(response.content)
            )

        all_assets.extend(data["assets"])

        if "total_pages" not in data:
            break

        if page >= data["total_pages"]:
            break

        page += 1

    return all_assets


@Decorators.check_env_vars
def create_asset(asset: dict) -> dict:
    """
    Create an asset
    https://ezo.io/ezofficeinventory/developers/#api-create-asset
    """

    # Required fields
    if "fixed_asset[name]" not in asset:
        raise ValueError("asset must have 'fixed_asset[name]' key")
    if "fixed_asset[group_id]" not in asset:
        raise ValueError("asset must have 'fixed_asset[group_id]' key")
    if "fixed_asset[purchased_on]" not in asset:
        raise ValueError("asset must have 'fixed_asset[purchased_on]' key")
        # Also check that the date is in the correct format mm/dd/yyyy
        try:
            datetime.strptime(asset["fixed_asset[purchased_on]"], "%m/%d/%Y")
        except ValueError:
            raise ValueError(
                "asset['fixed_asset[purchased_on]'] must be in the format mm/dd/yyyy"
            )

    # Remove any keys that are not valid
    valid_keys = [
        "fixed_asset[name]",
        "fixed_asset[group_id]",
        "fixed_asset[sub_group_id]" "fixed_asset[purchased_on]",
        "fixed_asset[location_id]",
        "fixed_asset[image_url]",
        "fixed_asset[document_urls][]",
        "fixed_asset[identifier]",
    ]

    asset = {
        k: v for k, v in asset.items() if k in valid_keys or k.startswith("cust_attr")
    }

    url = os.environ["EZO_BASE_URL"] + "assets.api"

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data=asset,
            timeout=10,
        )
    except Exception as e:
        print("Error, could not create asset in EZOfficeInventory: ", e)
        raise Exception("Error, could not create asset in EZOfficeInventory: " + str(e))

    return response.json()


@Decorators.check_env_vars
def update_asset(asset_id: int, asset: dict) -> dict:
    """
    Update an asset's details
    https://ezo.io/ezofficeinventory/developers/#api-update-asset
    """

    # Remove any keys that are not valid
    valid_keys = [
        "fixed_asset[name]",
        "fixed_asset[group_id]",
        "fixed_asset[sub_group_id]",
        "fixed_asset[purchased_on]",
        "fixed_asset[location_id]",
        "fixed_asset[image_url]",
        "fixed_asset[document_urls][]",
    ]

    asset = {
        k: v for k, v in asset.items() if k in valid_keys or k.startswith("cust_attr")
    }

    url = os.environ["EZO_BASE_URL"] + "assets/" + str(asset_id) + ".api"

    try:
        response = requests.put(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data=asset,
            timeout=10,
        )
    except Exception as e:
        print("Error, could not update asset in EZOfficeInventory: ", e)
        raise Exception("Error, could not update asset in EZOfficeInventory: " + str(e))

    return response.json()


@Decorators.check_env_vars
def delete_asset(asset_id: int) -> dict:
    """
    Delete an asset
    https://ezo.io/ezofficeinventory/developers/#api-delete-asset
    """

    url = os.environ["EZO_BASE_URL"] + "assets/" + str(asset_id) + ".api"

    try:
        response = requests.delete(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=10,
        )
    except Exception as e:
        print("Error, could not delete asset in EZOfficeInventory: ", e)
        raise Exception("Error, could not delete asset in EZOfficeInventory: " + str(e))

    return response.json()


@Decorators.check_env_vars
def checkin_asset(asset_id: int, checkin: dict) -> dict:
    """
    Check in an asset to a location
    https://ezo.io/ezofficeinventory/developers/#api-checkin-asset
    """

    # Required fields
    if "checkin[location_id]" not in checkin:
        raise ValueError("checkin must have 'checkin[location_id]' key")

    # Remove any keys that are not valid
    valid_keys = [
        "checkin[location_id]",
        "checkin[comments]",
    ]

    checkin = {
        k: v
        for k, v in checkin.items()
        if k in valid_keys or k.startswith("checkin_values[c_attr_vals]")
    }

    url = os.environ["EZO_BASE_URL"] + "assets/" + str(asset_id) + "/checkin.api"

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data=checkin,
            timeout=10,
        )
    except Exception as e:
        print("Error, could not checkin asset in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not checkin asset in EZOfficeInventory: " + str(e)
        )

    return response.json()


@Decorators.check_env_vars
def checkout_asset(asset_id: int, user_id: int, checkout: dict) -> dict:
    """
    Check out an asset to a member
    https://ezo.io/ezofficeinventory/developers/#api-checkout-asset
    """

    # Remove any keys that are not valid
    valid_keys = [
        "checkout_values[location_id]",
        "checkout_values[comments]",
        "till",
        "till_time",
        "checkout_values[override_conflicting_reservations]",
        "checkout_values[override_my_conflicting_reservations]",
    ]

    checkout = {
        k: v
        for k, v in checkout.items()
        if k in valid_keys or k.startswith("checkout_values[c_attr_vals]")
    }

    url = os.environ["EZO_BASE_URL"] + "assets/" + str(asset_id) + "/checkout.api"

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            params={"user_id": user_id},
            data=checkout,
            timeout=10,
        )
    except Exception as e:
        print("Error, could not checkout asset in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not checkout asset in EZOfficeInventory: " + str(e)
        )

    return response.json()


@Decorators.check_env_vars
def get_asset_history(asset_id: int) -> list[dict]:
    """
    Get asset history
    https://ezo.io/ezofficeinventory/developers/#api-checkin-out-history
    """

    url = (
        os.environ["EZO_BASE_URL"] + "assets/" + str(asset_id) + "/history_paginate.api"
    )

    page = 1
    all_history = []

    while True:
        try:
            response = requests.get(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params={"page": page},
                timeout=10,
            )
        except Exception as e:
            print("Error, could not get asset history from EZOfficeInventory: ", e)
            raise Exception(
                "Error, could not get asset history from EZOfficeInventory: " + str(e)
            )

        if response.status_code != 200:
            print(
                f"Error {response.status_code}, could not get asset history from EZOfficeInventory: ",
                response.content,
            )
            break

        data = response.json()

        if "history" not in data:
            print(
                f"Error, could not get asset history from EZOfficeInventory: ",
                response.content,
            )
            raise Exception(
                f"Error, could not get asset history from EZOfficeInventory: "
                + str(response.content)
            )

        all_history.extend(data["history"])

        if "total_pages" not in data:
            print("Error, could not get total_pages from EZOfficeInventory: ", data)
            break

        if page >= data["total_pages"]:
            break

        page += 1

    return all_history


@Decorators.check_env_vars
def get_work_orders(
    filter: Literal["complete", "in_progress", "review_pending", "open"]
) -> dict:
    """
    Get filtered work orders (complete, in_progress, review_pending, or open)
    https://ezo.io/ezofficeinventory/developers/#api-get-filtered-task
    """

    url = os.environ["EZO_BASE_URL"] + "tasks.api"

    page = 1
    all_work_orders = {}

    while True:

        try:
            response = requests.get(
                url,
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params={"page": page, "filter": filter},
                timeout=10,
            )
        except Exception as e:
            print("Error, could not get work orders from EZOfficeInventory: ", e)
            raise Exception(
                "Error, could not get work orders from EZOfficeInventory: " + str(e)
            )

        if response.status_code != 200:
            print(
                f"Error {response.status_code}, could not get work orders from EZOfficeInventory: ",
                response.content,
            )
            break

        data = response.json()

        if "work_orders" not in data:
            print(
                f"Error, could not get work orders from EZOfficeInventory: ",
                response.content,
            )
            raise Exception(
                f"Error, could not get work orders from EZOfficeInventory: "
                + str(response.content)
            )

        all_work_orders.update(data["work_orders"])

        if "total_pages" not in data:
            print("Error, could not get total_pages from EZOfficeInventory: ", data)
            break

        if page >= data["total_pages"]:
            break

        page += 1

    return all_work_orders


@Decorators.check_env_vars
def get_work_order_details(work_order_id: int) -> dict:
    """
    Get work order details
    https://ezo.io/ezofficeinventory/developers/#api-retrive-task-details
    """

    url = os.environ["EZO_BASE_URL"] + "tasks/" + str(work_order_id) + ".api"

    try:
        response = requests.get(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=10,
        )
    except Exception as e:
        print("Error, could not get work order from EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not get work order from EZOfficeInventory: " + str(e)
        )

    if response.status_code != 200:
        print(
            f"Error {response.status_code}, could not get work order from EZOfficeInventory: ",
            response.content,
        )
        raise Exception(
            f"Error, could not get work order from EZOfficeInventory: "
            + str(response.content)
        )

    return response.json()


@Decorators.check_env_vars
def get_work_order_types() -> list[dict]:
    """
    Get work order types
    Function doesn't appear to be paginated even though most other similar
    functions are.
    https://ezo.io/ezofficeinventory/developers/#api-get-task-types
    """

    url = os.environ["EZO_BASE_URL"] + "task_types.api"

    try:
        response = requests.get(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=10,
        )
    except Exception as e:
        print("Error, could not get work order types from EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not get work order types from EZOfficeInventory: " + str(e)
        )

    if response.status_code != 200:
        print(
            f"Error {response.status_code}, could not get work order types from EZOfficeInventory: ",
            response.content,
        )
        raise Exception(
            f"Error, could not get work order types from EZOfficeInventory: "
            + str(response.content)
        )

    if "work_order_types" not in response.json():
        print(
            f"Error, could not get work order types from EZOfficeInventory: ",
            response.content,
        )
        raise Exception(
            f"Error, could not get work order types from EZOfficeInventory: "
            + str(response.content)
        )

    return response.json()["work_order_types"]


@Decorators.check_env_vars
def create_work_order(work_order: dict) -> dict:
    """
    Create a work order
    https://ezo.io/ezofficeinventory/developers/#api-create-task
    """

    # Required fields
    if "task[title]" not in work_order:
        raise ValueError("work_order must have 'task[title]' key")
    if "task[task_type]" not in work_order:
        raise ValueError("work_order must have 'task[task_type]' key")
    if "due_date" not in work_order:
        raise ValueError("work_order must have 'due_date' key")
        # Also check that the date is in the correct format mm/dd/yyyy
        try:
            datetime.strptime(work_order["due_date"], "%m/%d/%Y")
        except ValueError:
            raise ValueError("work_order['due_date'] must be in the format mm/dd/yyyy")

    # Remove any keys that are not valid
    valid_keys = [
        "task[title]",
        "task[task_type]",
        "task[task_type_id]",
        "task[priority]",
        "task[assigned_to_id]",
        "task[reviewer_id]",
        "task[mark_items_unavailable]",
        "expected_start_date",
        "expected_start_time",
        "due_date",
        "start_time",
        "base_cost",
        "inventory_ids",
        "checklist_ids",
        "associated_assets",
        "custom_field_names",
    ]

    work_order = {
        k: v
        for k, v in work_order.items()
        if k in valid_keys
        or k.startswith("task[custom_attributes]")
        or k.startswith("linked_inventory_items")
        or k.startswith("associated_checklists")
    }

    url = os.environ["EZO_BASE_URL"] + "tasks.api"

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data=work_order,
            timeout=10,
        )
    except Exception as e:
        print("Error, could not create work order in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not create work order in EZOfficeInventory: " + str(e)
        )

    return response.json()


@Decorators.check_env_vars
def start_work_order(work_order_id: int) -> dict:
    """
    Start a work order
    https://ezo.io/ezofficeinventory/developers/#api-start-task
    """

    url = (
        os.environ["EZO_BASE_URL"]
        + "tasks/"
        + str(work_order_id)
        + "/mark_in_progress.api"
    )

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=10,
        )
    except Exception as e:
        print("Error, could not start work order in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not start work order in EZOfficeInventory: " + str(e)
        )

    return response.json()


@Decorators.check_env_vars
def end_work_order(work_order_id: int) -> dict:
    """
    End a work order
    https://ezo.io/ezofficeinventory/developers/#api-end-task
    """

    url = (
        os.environ["EZO_BASE_URL"]
        + "tasks/"
        + str(work_order_id)
        + "/mark_complete.api"
    )

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            timeout=10,
        )
    except Exception as e:
        print("Error, could not end work order in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not end work order in EZOfficeInventory: " + str(e)
        )

    return response.json()


@Decorators.check_env_vars
def add_work_log_to_work_order(work_order_id: int, work_log: dict) -> dict:
    """
    Add a work log to a work order
    resource id and resource type vary depending on type of component
    work log is being added against. Asset vs Group vs Member etc. Docu has a table
    https://ezo.io/ezofficeinventory/developers/#api-add-work-log-to-task
    """

    # Required fields
    if "task_work_log[time_spent]" not in work_log:
        raise ValueError("work_log must have 'task_work_log[time_spent]' key")
    if "task_work_log[user_id]" not in work_log:
        raise ValueError("work_log must have 'task_work_log[user_id]' key")

    # Remove any keys that are not valid
    valid_keys = [
        "task_work_log[time_spent]",
        "task_work_log[user_id]",
        "task_work_log[description]",
        "task_work_log[resource_id]",
        "task_work_log[resource_type]",
        "started_on_date",
        "started_on_time",
        "ended_on_date",
        "ended_on_time",
    ]

    work_log = {k: v for k, v in work_log.items() if k in valid_keys}

    url = (
        os.environ["EZO_BASE_URL"]
        + "tasks/"
        + str(work_order_id)
        + "/task_work_logs.api"
    )

    try:
        response = requests.post(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data=work_log,
            timeout=10,
        )
    except Exception as e:
        print("Error, could not add work log to work order in EZOfficeInventory: ", e)
        raise Exception(
            "Error, could not add work log to work order in EZOfficeInventory: "
            + str(e)
        )

    return response.json()


@Decorators.check_env_vars
def add_linked_inv_to_work_order(work_order_id: int, linked_inv: dict) -> dict:
    """
    Add linked inventory items to a work order
    resource id and resource type vary depending on type of component
    linked inventory is being added against. Asset vs Group vs Member etc. Docu has a table
    https://ezo.io/ezofficeinventory/developers/#api-add-linked-inventory-to-task
    """

    # Required fields
    if "inventory_id" not in linked_inv:
        raise ValueError("linked_inv must have 'inventory_id' key")
    if not any(
        key.startswith("linked_inventory_items[") and key.endswith("][quantity]")
        for key in linked_inv.keys()
    ):
        raise ValueError(
            "linked_inv must have a key that matches the format linked_inventory_items[{Inventory#}][quantity]"
        )

    # Remove any keys that are not valid
    valid_keys = ["inventory_id"]

    linked_inv = {
        k: v
        for k, v in linked_inv.items()
        if k in valid_keys
        or (k.startswith("linked_inventory_items[") and k.endswith("][quantity]"))
        or (k.startswith("linked_inventory_items[") and k.endswith("][location_id]"))
        or (k.startswith("linked_inventory_items[") and k.endswith("][resource_id]"))
        or (k.startswith("linked_inventory_items[") and k.endswith("][resource_type]"))
    }

    url = (
        os.environ["EZO_BASE_URL"]
        + "tasks/"
        + str(work_order_id)
        + "/link_inventory.api"
    )

    try:
        response = requests.patch(
            url,
            headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
            data=linked_inv,
            timeout=10,
        )
    except Exception as e:
        print(
            "Error, could not add linked inventory items to work order in EZOfficeInventory: ",
            e,
        )
        raise Exception(
            "Error, could not add linked inventory items to work order in EZOfficeInventory: "
            + str(e)
        )

    return response.json()


@Decorators.check_env_vars
def get_checklists() -> list[dict]:
    """
    Get checklists
    https://ezo.io/ezofficeinventory/developers/#api-retrieve-checklists
    """

    page = 1
    all_checklists = []

    while True:
        try:
            response = requests.get(
                os.environ["EZO_BASE_URL"] + "checklists.api",
                headers={"Authorization": "Bearer " + os.environ["EZO_TOKEN"]},
                params={"page": page},
                timeout=10,
            )
        except Exception as e:
            print("Error, could not get checklists from EZOfficeInventory: ", e)
            raise Exception(
                "Error, could not get checklists from EZOfficeInventory: " + str(e)
            )

        if response.status_code != 200:
            print(
                f"Error {response.status_code}, could not get checklists from EZOfficeInventory: ",
                response.content,
            )
            break

        data = response.json()

        if "checklists" not in data:
            print(
                f"Error, could not get checklists from EZOfficeInventory: ",
                response.content,
            )
            raise Exception(
                f"Error, could not get checklists from EZOfficeInventory: "
                + str(response.content)
            )

        all_checklists.extend(data["checklists"])

        if "total_pages" not in data:
            print("Error, could not get total_pages from EZOfficeInventory: ", data)
            break

        if page >= data["total_pages"]:
            break

        page += 1

    return all_checklists


if __name__ == "__main__":
    """
    Testing
    """
    # Import JSON config file
    try:
        with open("config.json") as json_file:
            config = json.load(json_file)
    except Exception as e:
        print("Error, could not open config file: ", e)
        exit(1)
    os.environ["EZO_BASE_URL"] = config["EZO_BASE_URL"]
    os.environ["EZO_TOKEN"] = config["EZO_TOKEN"]

    result = get_work_order_details(1652)
    pprint(result)
