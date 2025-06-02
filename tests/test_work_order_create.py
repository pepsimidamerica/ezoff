from ezoff._auth import Decorators
from ezoff._helpers import _basic_retry, _fetch_page
from ezoff import *


work_order = {
    "title": "EMO - In Transit to Marion",
    "work_type_name": "EMO",
    "priority": "medium",
    "state": "Open",
    "location_id": 12388,
    "description": "Asset has been picked up and is being transferred to Marion Vending Warehouse.",
    "assigned_to_id": 497695,
    "assigned_to_type": "User",
    "reviewer_id": 497695,
    "supervisor_id": 497695,
    "custom_fields": [{"id": 739, "value": "11 Marion"}],
}

result = ezoff.create_work_order_v2(work_order=work_order)
work_order_id = result["work_order"]["id"]

components = []
components.append(Component(resource_id=27325, resource_type=ResourceType.ASSET))
# components.append(Component(resource_id=14753, resource_type=ResourceType.ASSET))

ezoff.add_work_order_component_v2(work_order_id=work_order_id, components=components)
