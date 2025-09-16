"""
Module for interacting with the EZO API

Developer Documentation
API v1: https://ezo.io/ezofficeinventory/developers/
API v2: https://www.ezofficeinventory.com/api-docs/index.html
"""

from .assets import (
    asset_activate,
    asset_checkin,
    asset_checkout,
    asset_create,
    asset_delete,
    asset_history_return,
    asset_retire,
    asset_return,
    asset_update,
    asset_verification_request,
    assets_return,
    assets_search,
    assets_token_input_return,
)
from .bundle import bundle_create, bundle_return, bundles_return
from .checklists import checklists_return
from .data_model import *
from .enums import AssetClass, CustomFieldID, LocationClass, RentLoan, ResourceType
from .ezo_cache import AssetCache, EzoCache, LocationCache, MemberCache, WorkOrderCache
from .groups import (
    group_create,
    group_delete,
    group_return,
    group_update,
    groups_return,
    subgroup_create,
    subgroup_delete,
    subgroup_return,
    subgroup_update,
    subgroups_return,
)
from .inventory import (
    inventories_return,
    inventories_search,
    inventory_activate,
    inventory_add_stock,
    inventory_create,
    inventory_custom_field_history_return,
    inventory_delete,
    inventory_history_return,
    inventory_link_to_project,
    inventory_quantity_by_location_return,
    inventory_remove_stock,
    inventory_reservations_return,
    inventory_retire,
    inventory_return,
    inventory_transfer_stock,
    inventory_unlink_from_project,
    inventory_update_location,
)
from .locations import (
    location_activate,
    location_create,
    location_deactivate,
    location_return,
    location_update,
    locations_return,
)
from .members import (
    custom_role_update,
    custom_roles_return,
    member_activate,
    member_create,
    member_deactivate,
    member_return,
    member_update,
    members_create,
    members_return,
    teams_return,
    user_listings_return,
)
from .packages import package_checkin, package_create, package_return, packages_return
from .projects import (
    project_create,
    project_mark_complete,
    project_mark_in_progress,
    project_return,
    projects_return,
)
from .purchase_orders import (
    purchase_order_create,
    purchase_order_return,
    purchase_orders_return,
)
from .retire_reasons import retire_reasons_return
from .stock_assets import *
from .vendors import vendor_create, vendor_return, vendor_update, vendors_return
from .work_orders import *

__all__ = []
