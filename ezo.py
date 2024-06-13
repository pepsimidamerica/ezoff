import json
import os
from datetime import datetime, timedelta
from pprint import pprint
from typing import Optional

import requests

# Members Functions


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


# Locations Functions
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
        params = {"page": page}
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


# Assets Functions
# TODO

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

    # members = get_members(
    #     {"filter": "employee_identification_number", "filter_val": "10431"}
    # )
    locations = get_locations({"status": "active"})
    pass
