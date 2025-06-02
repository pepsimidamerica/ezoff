from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Optional, Any
from datetime import datetime, date

from .enums import *


class AssetV2(BaseModel):
    active_sub_checkout: Optional[Any] = Field(default=None)
    arbitration: int
    audit_pending: bool
    bulk_import_id: Optional[int] = Field(default=None)
    checkin_due_on: Optional[datetime] = Field(default=None)
    checkout_on: Optional[datetime] = Field(default=None)
    comments_count: int
    cost_price: float
    created_at: Optional[datetime] = Field(default=None)
    custom_fields: Optional[list] = Field(default=[])
    custom_substate_id: Optional[int] = Field(default=None)
    depreciation_calculation_required: bool
    description: Optional[str] = Field(default="")
    display_image: str
    documents_count: int
    group_id: int
    id: int
    identifier: str
    item_audit_id: Optional[int] = Field(default=None)
    last_assigned_to_id: Optional[int] = Field(default=None)
    last_checked_in_at: Optional[datetime] = Field(default=None)
    last_checked_out_at: Optional[datetime] = Field(default=None)
    last_history_id: Optional[int] = Field(default=None)
    latest_contract_id: Optional[int] = Field(default=None)
    location_id: Optional[int] = Field(default=None)
    manufacturer: Optional[str] = Field(default="")
    name: str
    package_id: Optional[int] = Field(default=None)
    pending_verification: bool
    primary_user: Optional[int] = Field(default=None)
    product_model_number: Optional[str] = Field(default="")
    purchase_order_id: Optional[int] = Field(default=None)
    purchased_on: Optional[date] = Field(default=None)
    retire_comments: Optional[str] = Field(default="")
    retire_reason_id: Optional[int] = Field(default=None)
    retired_by_id: Optional[int] = Field(default=None)
    retired_on: Optional[datetime] = Field(default=None)
    salvage_value: str
    services_count: Optional[int] = Field(default=None)
    state: str
    sub_checked_out_to_id: Optional[int] = Field(default=None)
    sub_group_id: Optional[int] = Field(default=None)
    sunshine_id: Optional[int] = Field(default=None)
    synced_with_jira_at: Optional[date] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    vendor_id: Optional[int] = Field(default=None)

    # Custom fields, parsed from the custom_fields attribute.
    rent: Optional[bool] = Field(default=None)
    serial_number: Optional[str] = Field(default=None)
    asset_class: Optional[AssetClass] = Field(default=None)

    def model_post_init(self, __context: Any) -> None:
        """Parse custom fields."""

        for field in self.custom_fields:

            # Assign Rent Flag
            if "id" in field and field["id"] == CustomFieldID.RENT_FLAG.value:
                if field["value"] is not None and isinstance(field["value"], list):
                    if len(field["value"]) > 0:
                        self.rent = True
                    else:
                        self.rent = False

            # Assign Serial Number
            if "id" in field and field["id"] == CustomFieldID.ASSET_SERIAL_NO.value:
                if field["value"] is not None and isinstance(field["value"], str):
                    self.serial_number = field["value"]

            # Assign Asset Class
            if "id" in field and field["id"] == CustomFieldID.ASSET_CLASS.value:
                if field["value"] is not None and isinstance(field["value"], list):
                    try:
                        self.asset_class = AssetClass(field["value"][0])
                    except ValueError as e:
                        raise ValueError(
                            (
                                f'Invalid asset class in asset {self.id}: {field["value"][0]}'
                            )
                        )


class ChecklistV2(BaseModel):
    id: int
    name: str
    created_by_id: int
    line_items: list


class Component(BaseModel):
    resource_id: int
    resource_type: ResourceType

    class Config:
        use_enum_values = True


class LocationV2(BaseModel):
    apply_default_return_date_to_child_locations: Optional[bool] = Field(default=None)
    checkout_indefinitely: Optional[bool] = Field(default=None)
    city: Optional[str] = Field(default=None)
    comments_count: int
    country: Optional[str] = Field(default="")
    created_at: Optional[datetime] = Field(default=None)
    custom_fields: Optional[list] = Field(default=[])
    default_return_duration: Optional[int] = Field(default=None)
    default_return_duration_unit: Optional[str] = Field(default=None)
    default_return_time: Optional[datetime] = Field(default=None)
    description: Optional[str] = Field(default=None)
    documents_count: int
    hidden_on_webstore: bool
    id: int
    identification_number: Optional[str] = Field(default=None)
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    manual_coordinates_provided: Optional[bool] = Field(default=None)
    name: str
    parent_id: Optional[int] = Field(default=None)
    secure_code: str
    state: Optional[str] = Field(default=None)
    status: str
    street1: Optional[str] = Field(default=None)
    street2: Optional[str] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    visible_on_webstore: bool
    zip_code: Optional[str] = Field(default=None)

    # Custom fields
    parent_cust_code: Optional[str] = Field(default=None)
    exclude_rent_fees: Optional[bool] = Field(default=None)

    def model_post_init(self, __context: Any) -> None:
        # Parse custom fields.
        for field in self.custom_fields:

            # Assign 'Exclude Rent Fees'
            if "id" in field and field["id"] == CustomFieldID.EXCLUDE_RENT_FEES.value:
                if field["value"] is not None and isinstance(field["value"], str):
                    if field["value"].lower() == "yes":
                        self.exclude_rent_fees = True
                    else:
                        self.exclude_rent_fees = False

            # Assign 'Parent Customer Code'
            if "id" in field and field["id"] == CustomFieldID.PARENT_CUST_CODE.value:
                if field["value"] is not None and isinstance(field["value"], str):
                    self.parent_cust_code = field["value"]

        # Clear out custom field list, to save space.
        self.custom_fields = None


class MemberV2(BaseModel):
    account_name: Optional[str] = Field(default=None)
    address_name: Optional[str] = Field(default=None)
    alert_type: Optional[str] = Field(default=None)
    auto_sync_with_ldap: Optional[bool] = Field(default=None)
    billing_address_id: Optional[int] = Field(default=None)
    category_id: Optional[int] = Field(default=None)
    collect_tax: Optional[str] = Field(default=None)
    comments_count: Optional[int] = Field(default=None)
    company_default_payment_terms: Optional[bool] = Field(default=None)
    contact_owner: Optional[str] = Field(default=None)
    contact_type: Optional[str] = Field(default=None)
    country: Optional[str] = Field(default=None)
    created_at: datetime
    created_by_id: Optional[int] = Field(default=None)
    creation_source: Optional[str] = Field(default=None)
    credit_memo_amount: Optional[float] = Field(default=None)
    custom_fields: Optional[List[dict]] = Field(default=[])
    deactivated_at: Optional[datetime] = Field(default=None)
    default_address_id: Optional[int] = Field(default=None)
    default_triage_setting_id: Optional[int] = Field(default=None)
    department: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    documents_count: Optional[int] = Field(default=None)
    email: Optional[str] = Field(default=None)
    employee_id: Optional[str] = Field(default=None)
    employee_identification_number: Optional[str] = Field(default=None)
    fax: Optional[str] = Field(default=None)
    full_name: Optional[str] = Field(default=None)
    hourly_rate: Optional[float] = Field(default=None)
    id: int
    inactive_by_id: Optional[int] = Field(default=None)
    jira_account_id: Optional[str] = Field(default=None)
    last_sync_date: Optional[datetime] = Field(default=None)
    last_sync_source: Optional[str] = Field(default=None)
    manager_id: Optional[int] = Field(default=None)
    offboarding_date: Optional[date] = Field(default=None)
    otp_required_for_login: Optional[bool] = Field(default=None)
    password_changed_at: Optional[datetime] = Field(default=None)
    payment_term_id: Optional[int] = Field(default=None)
    phone_number: Optional[str] = Field(default=None)
    role_id: Optional[int] = Field(default=None)
    salesforce_id: Optional[int] = Field(default=None)
    secure_code: Optional[str] = Field(default=None)
    services_count: Optional[int] = Field(default=None)
    settings_access: Optional[bool] = Field(default=None)
    show_announcement: Optional[bool] = Field(default=None)
    show_app_updates: Optional[bool] = Field(default=None)
    status: int
    stock_asset_current_checkout_view: Optional[bool] = Field(default=None)
    subscribed_to_emails: Optional[bool] = Field(default=None)
    team_id: Optional[int] = Field(default=None)
    time_zone: Optional[str] = Field(default=None)
    unseen_app_updates_count: Optional[int] = Field(default=None)
    unsubscribed_by_id: Optional[int] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    user_listing_id: Optional[int] = Field(default=None)
    zendesk_account_id: Optional[int] = Field(default=None)


class WorkOrderV2(BaseModel):
    approver_id: Optional[int] = Field(default=None)
    assigned_to_id: Optional[int] = Field(default=None)
    assigned_to_type: str
    associated_checklists: list
    base_cost: float
    completed_on: Optional[str] = Field(default=None)
    create_one_task_for_all_items: bool
    create_recurring_service_zendesk_tickets: bool
    created_at: Optional[datetime] = Field(default=None)
    created_by_id: Optional[int] = Field(default=None)
    creation_source: Optional[str] = Field(default=None)
    custom_fields: Optional[List[dict]]
    description: Optional[str] = Field(default=None)
    display_next_service_immediately: bool
    due_date: Optional[datetime] = Field(default=None)
    expected_start_date: Optional[datetime] = Field(default=None)
    id: int
    inventory_cost: float
    inventory_cost_method: Optional[str] = Field(default=None)
    is_item_component: bool
    is_triage: bool
    location_id: Optional[int] = Field(default=None)
    mark_items_unavailable: bool
    preventive_maintenance: bool
    priority: str
    project_id: Optional[int] = Field(default=None)
    recurrence_based_on_completion_date: bool
    recurrence_task_id: Optional[int | None]
    repeat_every_basis: Optional[str] = Field(default=False)
    repeat_every_value: int
    repetition_end_date: Optional[str] = Field(default=None)
    repetition_starting: Optional[str] = Field(default=None)
    requested_by_id: Optional[int] = Field(default=None)
    require_approval_from_reviewer: bool
    reviewer_id: Optional[int] = Field(default=None)
    service_for_sub_groups_only: bool
    service_type_id: Optional[int] = Field(default=None)
    shipping_address_id: Optional[int] = Field(default=None)
    start_work_on_all_assets: bool
    started_on: Optional[str] = Field(default=None)
    state: str
    supervisor_id: Optional[int] = Field(default=None)
    task_type: str
    task_type_id: Optional[int] = Field(default=None)
    template_id: Optional[int] = Field(default=None)
    time_spent: float
    # time_to_respond:
    time_to_start: int
    title: str
    total_cost: float
    track_progress: float
    updated_at: str
    warranty: Optional[bool] = Field(default=False)
    work_logs_cost: float
    work_type_name: Optional[str] = Field(default=None)
    zendesk_ticket_id: Optional[int]

    # Custom fields
    depot: Optional[str] = Field(default=None)
    depot_id: Optional[int] = Field(default=None)

    def model_post_init(self, __context: Any) -> None:
        # Parse custom fields.
        for field in self.custom_fields:
            # Assign Depot and Depot ID
            if "id" in field and field["id"] == CustomFieldID.DEPOT.value:
                if field["value"] is not None:
                    self.depot = field["value"]
                    self.depot_id = int(field["value"][:2])
