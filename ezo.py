import json
import os
from datetime import datetime, timedelta
from pprint import pprint
from typing import Optional

import requests


def get_members(filter: Optional[dict]) -> list[dict]:
    """
    Get members from EZOfficeInventory
    Optionally filter by email, employee_identification_number, or status
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

    if "EZO_BASE_URL" not in os.environ:
        raise Exception("EZO_BASE_URL not found in environment variables.")
    if "EZO_TOKEN" not in os.environ:
        raise Exception("EZO_TOKEN not found in environment variables.")

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


def get_member_details(member_id: int) -> dict:
    """
    Get member from EZOfficeInventory by member_id
    """

    if "EZO_BASE_URL" not in os.environ:
        raise Exception("EZO_BASE_URL not found in environment variables.")
    if "EZO_TOKEN" not in os.environ:
        raise Exception("EZO_TOKEN not found in environment variables.")

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


def create_member(member: dict) -> dict:
    """
    Create a new member
    """
    if "EZO_BASE_URL" not in os.environ:
        raise Exception("EZO_BASE_URL not found in environment variables.")
    if "EZO_TOKEN" not in os.environ:
        raise Exception("EZO_TOKEN not found in environment variables.")

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


def get_locations(filter: Optional[dict]) -> list[dict]:
    """
    Get locations
    Optionally filter by status
    """
    if filter is not None:
        if "status" not in filter:
            raise ValueError("filter must have 'status' key")
        if filter["status"] not in ["all", "active", "inactive"]:
            raise ValueError(
                "filter['status'] must be one of 'all', 'active', 'inactive'"
            )

    if "EZO_BASE_URL" not in os.environ:
        raise Exception("EZO_BASE_URL not found in environment variables.")
    if "EZO_TOKEN" not in os.environ:
        raise Exception("EZO_TOKEN not found in environment variables.")

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


def get_location_details(location_num: int) -> dict:
    """
    Get location details
    """
    if "EZO_BASE_URL" not in os.environ:
        raise Exception("EZO_BASE_URL not found in environment variables")
    if "EZO_TOKEN" not in os.environ:
        raise Exception("EZO_TOKEN not found in environment variables")

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


def create_location(location: dict) -> dict:
    """
    Create a location
    """
    if "EZO_BASE_URL" not in os.environ:
        raise Exception("EZO_BASE_URL not found in environment variables")
    if "EZO_TOKEN" not in os.environ:
        raise Exception("EZO_TOKEN not found in environment variables")

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


def get_all_assets() -> list[dict]:
    """
    Get assets
    Recommended to use endpoint that takes a filter instead.
    This endpoint can be slow as it returns all assets in the system. Potentially
    several hundred pages of assets.
    """

    if "EZO_BASE_URL" not in os.environ:
        raise Exception("EZO_BASE_URL not found in environment variables.")
    if "EZO_TOKEN" not in os.environ:
        raise Exception("EZO_TOKEN not found in environment variables.")

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


def get_filtered_assets(filter: dict) -> list[dict]:
    """
    Get assets via filtering. Recommended to use this endpoint rather than
    returning all assets.
    """
    if "status" not in filter:
        raise ValueError("filter must have 'status' key")

    if "EZO_BASE_URL" not in os.environ:
        raise Exception("EZO_BASE_URL not found in environment variables.")
    if "EZO_TOKEN" not in os.environ:
        raise Exception("EZO_TOKEN not found in environment variables.")

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


def search_for_asset(search_term: str) -> list[dict]:
    """
    Search for an asset. Similar to filtering but more flexible.
    The equivalent of the search bar in the EZOfficeInventory UI.
    May not return all assets that match the search term. Better to use
    get_filtered_assets if you want to return all assets that match a filter.
    """

    if "EZO_BASE_URL" not in os.environ:
        raise Exception("EZO_BASE_URL not found in environment variables.")
    if "EZO_TOKEN" not in os.environ:
        raise Exception("EZO_TOKEN not found in environment variables.")

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

    # Get assets
    assets = search_for_asset("laptop")

    pass
