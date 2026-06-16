"""
Module contains any pydantic models used throughout the package.
"""

from datetime import date, datetime
from typing import Any, Literal

from ezoff.enums import AssetClass, CustomFieldID, LocationClass, ResourceType
from pydantic import BaseModel, Field


class ResponseMessages(BaseModel):
    """
    Some API responses come in the form of a list or string of either successes or errors.
    """

    success: list[str] | str | None = None
    errors: list[str] | str | None = None


class Asset(BaseModel):
    """
    Model representing a fixed asset. Some individual item that could be identified with
    a serial number or some unique identifier.
    """

    active_sub_checkout: Any | None = Field(default=None)
    arbitration: int
    audit_pending: bool
    bulk_import_id: int | None = Field(default=None)
    checkin_due_on: datetime | None = Field(default=None)
    checkout_on: datetime | None = Field(default=None)
    comments_count: int
    cost_price: float
    created_at: datetime | None = Field(default=None)
    custom_fields: list | None = Field(default=[])
    custom_substate_id: int | None = Field(default=None)
    depreciation_calculation_required: bool
    description: str | None = Field(default="")
    display_image: str
    documents_count: int
    group_id: int
    id: int
    identifier: str
    item_audit_id: int | None = Field(default=None)
    assigned_to_id: int | None = Field(default=None)
    last_assigned_to_id: int | None = Field(default=None)
    last_checked_in_at: datetime | None = Field(default=None)
    last_checked_out_at: datetime | None = Field(default=None)
    last_history_id: int | None = Field(default=None)
    latest_contract_id: int | None = Field(default=None)
    location_id: int | None = Field(default=None)
    manufacturer: str | None = Field(default="")
    name: str
    package_id: int | None = Field(default=None)
    pending_verification: bool
    primary_user: int | None = Field(default=None)
    product_model_number: str | None = Field(default="")
    purchase_order_id: int | None = Field(default=None)
    purchased_on: date | None = Field(default=None)
    retire_comments: str | None = Field(default="")
    retire_reason_id: int | None = Field(default=None)
    retired_by_id: int | None = Field(default=None)
    retired_on: datetime | None = Field(default=None)
    salvage_value: str
    services_count: int | None = Field(default=None)
    state: str
    sub_checked_out_to_id: int | None = Field(default=None)
    sub_group_id: int | None = Field(default=None)
    sunshine_id: int | None = Field(default=None)
    synced_with_jira_at: date | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)
    vendor_id: int | None = Field(default=None)

    # Custom fields, parsed from the custom_fields attribute.
    rent: bool | None = Field(default=None)
    serial_number: str | None = Field(default=None)
    telemetry_serial_number: str | None = Field(default=None)
    pma_number: str | None = Field(default=None)
    acquired_from: str | None = Field(default=None)
    manufactured_date: str | None = Field(default=None)
    mfr_part_number: str | None = Field(default=None)
    asset_class: AssetClass | None = Field(default=None)

    def model_post_init(self, __context: Any) -> None:
        """
        Parse custom fields.
        """
        if self.custom_fields:
            # Create lookup dictionary
            field_values = {
                field.get("id"): field.get("value")
                for field in self.custom_fields
                if "id" in field
            }

            # Process Rent Flag
            if CustomFieldID.RENT_FLAG.value in field_values:
                value = field_values[CustomFieldID.RENT_FLAG.value]
                if value is not None and isinstance(value, list):
                    if len(value) > 0:
                        self.rent = True
                    else:
                        self.rent = False

            # Process Serial Number
            if CustomFieldID.ASSET_SERIAL_NO.value in field_values:
                value = field_values[CustomFieldID.ASSET_SERIAL_NO.value]
                if value and isinstance(value, str):
                    self.serial_number = value

            # Process Telemetry Serial Number
            if CustomFieldID.TELEMETRY_SERIAL_NO.value in field_values:
                value = field_values[CustomFieldID.TELEMETRY_SERIAL_NO.value]
                if value and isinstance(value, str):
                    self.telemetry_serial_number = value

            # Process PMA Number
            if CustomFieldID.PMA_NO.value in field_values:
                value = field_values[CustomFieldID.PMA_NO.value]
                if value and isinstance(value, str):
                    self.pma_number = value

            # Process Acquired From
            if CustomFieldID.ACQUIRED_FROM.value in field_values:
                value = field_values[CustomFieldID.ACQUIRED_FROM.value]
                if value and isinstance(value, str):
                    self.acquired_from = value

            # Process Manufactured Date
            if CustomFieldID.MANUFACTURED_DATE.value in field_values:
                value = field_values[CustomFieldID.MANUFACTURED_DATE.value]
                if value and isinstance(value, str):
                    self.manufactured_date = value

            # Process MFR Part Number
            if CustomFieldID.MFR_PART_NO.value in field_values:
                value = field_values[CustomFieldID.MFR_PART_NO.value]
                if value and isinstance(value, str):
                    self.mfr_part_number = value

            # Process Asset Class
            if CustomFieldID.ASSET_CLASS.value in field_values:
                value = field_values[CustomFieldID.ASSET_CLASS.value]
                if value is not None and isinstance(value, list):
                    if len(value) > 0:
                        try:
                            self.asset_class = AssetClass(value[0])
                        except ValueError as e:
                            raise ValueError(
                                f"Invalid asset class in asset {self.id}: {value[0]}"
                            )


class Inventory(BaseModel):
    """
    An inventory or "volatile asset" in EZO represents some item that are
    consumed upon checkout, i.e. will not be returned. So, we only track
    the stock level and quantity of these types of assets.
    """

    arbitration: int | None = None
    asset_detail_attributes: dict | None = None
    audit_pending: bool
    available_quantity: int | None = None
    average_cost_per_unit: str | None = None
    bulk_import_id: int | None = None
    checkin_due_on: datetime | None = None
    checkout_on: datetime | None = None
    comments_count: int
    cost_price: float
    created_at: datetime
    custom_fields: list[dict] | None = None
    custom_substate_id: int | None = None
    default_excess_location_threshold: int
    default_low_location_threshold: int | None = None
    depreciation_calculation_required: bool
    description: str | None = None
    display_image: str | None = None
    documents_count: int
    group_id: int | None = None
    id: int
    identifier: str
    initial_stock_quantity: int
    inventory_threshold: int
    item_audit_id: int | None = None
    last_assigned_to_id: int | None = None
    last_checked_in_at: datetime | None = None
    last_checked_out_at: datetime | None = None
    last_history_id: int | None = None
    latest_contract_id: int | None = None
    line_items_attributes: list | None = None
    location_based_threshold: int | None = None
    location_id: int | None = None
    location_thresholds_attributes: list | None = None
    # Manufacturer coming through on API but is null for everything. Not seeing
    # it in the web UI, so not sure if used. Leaving in case it becomes populated in future.
    manufacturer: Any | None = None
    name: str
    net_quantity: int | None = None
    package_id: int | None = None
    pending_verification: bool
    primary_user: int | None = None
    product_model_number: str | None = None
    purchase_order_id: int | None = None
    purchased_on: datetime | None = None
    retire_comments: str | None = None
    retire_reason_id: int | None = None
    retired_by_id: int | None = None
    retired_on: datetime | None = None
    sale_price: str | None = None
    salvage_value: float
    state: str | None = None
    sub_checked_out_to_id: int | None = None
    sub_group_id: int | None = None
    sunshine_id: int | None = None
    synced_with_jira_at: datetime | None = None
    updated_at: datetime
    vendor_id: int | None = None


class ChecklistLineItem(BaseModel):
    """
    A line item in a checklist.
    """

    title: str
    type: str


class Checklist(BaseModel):
    """
    Checklists are assignable to work orders. They contain line items
    that can represent tasks to be completed as part of the work order or
    information to be collected.
    """

    id: int
    name: str
    created_by_id: int
    line_items: list[ChecklistLineItem]


class Component(BaseModel):
    """
    A component is a reference to a resource (e.g. a work order or asset)
    that is associated with a work order or asset.
    """

    resource_id: int
    resource_type: ResourceType

    class Config:
        use_enum_values = True


class Location(BaseModel):
    """
    A location in EZO represents some physical place that assets can
    be stored in or checked out to. Locations are hierarchical, so you can
    have parent locations with child sub-locations beneath them.
    """

    # Class attribute to control custom fields clearing behavior
    _clear_custom_fields: bool = True

    apply_default_return_date_to_child_locations: bool | None = Field(default=None)
    checkout_indefinitely: bool | None = Field(default=None)
    city: str | None = Field(default=None)
    comments_count: int
    country: str | None = Field(default="")
    created_at: datetime | None = Field(default=None)
    custom_fields: list | None = Field(default=[])
    default_return_duration: int | None = Field(default=None)
    default_return_duration_unit: str | None = Field(default=None)
    default_return_time: datetime | None = Field(default=None)
    description: str | None = Field(default=None)
    documents_count: int
    hidden_on_webstore: bool
    id: int
    identification_number: str | None = Field(default=None)
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)
    manual_coordinates_provided: bool | None = Field(default=None)
    name: str
    parent_id: int | None = Field(default=None)
    secure_code: str
    state: str | None = Field(default=None)
    status: str
    street1: str | None = Field(default=None)
    street2: str | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)
    visible_on_webstore: bool
    zip_code: str | None = Field(default=None)

    # Custom fields
    parent_cust_code: str | None = Field(default=None)
    exclude_rent_fees: bool | None = Field(default=None)
    location_class: LocationClass | None = Field(default=LocationClass.NONE)
    tax_jurisdiction: str | None = Field(default=None)

    def model_post_init(self, __context: Any) -> None:
        """
        Parse custom fields into specific model attributes.
        """
        if self.custom_fields:
            # Create lookup dictionary
            field_values = {
                field.get("id"): field.get("value")
                for field in self.custom_fields
                if "id" in field
            }

            # Process 'Exclude Rent Fees'
            if CustomFieldID.EXCLUDE_RENT_FEES.value in field_values:
                value = field_values[CustomFieldID.EXCLUDE_RENT_FEES.value]
                if value and isinstance(value, str):
                    self.exclude_rent_fees = value.lower() == "yes"

            # Process 'Parent Customer Code'
            if CustomFieldID.PARENT_CUST_CODE.value in field_values:
                value = field_values[CustomFieldID.PARENT_CUST_CODE.value]
                if value and isinstance(value, str):
                    self.parent_cust_code = value

            # Process 'Location Class'
            if CustomFieldID.LOCATION_CLASS.value in field_values:
                value = field_values[CustomFieldID.LOCATION_CLASS.value]
                self.location_class = LocationClass(value or LocationClass.NONE)

            # Process 'Tax Jurisdiction'
            if CustomFieldID.TAX_JURISDICTION.value in field_values:
                value = field_values[CustomFieldID.TAX_JURISDICTION.value]
                if value and isinstance(value, str):
                    self.tax_jurisdiction = value

            # Clear out custom field list, to save space (if enabled).
            if self._clear_custom_fields:
                self.custom_fields = None


class Member(BaseModel):
    """
    Model representing a member (user).
    """

    account_name: str | None = Field(default=None)
    address_name: str | None = Field(default=None)
    alert_type: str | None = Field(default=None)
    auto_sync_with_ldap: bool | None = Field(default=None)
    billing_address_id: int | None = Field(default=None)
    category_id: int | None = Field(default=None)
    collect_tax: str | None = Field(default=None)
    comments_count: int | None = Field(default=None)
    company_default_payment_terms: bool | None = Field(default=None)
    contact_owner: str | None = Field(default=None)
    contact_type: str | None = Field(default=None)
    country: str | None = Field(default=None)
    created_at: datetime
    created_by_id: int | None = Field(default=None)
    creation_source: str | None = Field(default=None)
    credit_memo_amount: float | None = Field(default=None)
    custom_fields: list[dict] | None = Field(default=[])
    deactivated_at: datetime | None = Field(default=None)
    default_address_id: int | None = Field(default=None)
    default_triage_setting_id: int | None = Field(default=None)
    department: str | None = Field(default=None)
    description: str | None = Field(default=None)
    documents_count: int | None = Field(default=None)
    email: str
    employee_id: str | None = Field(default=None)
    employee_identification_number: str | None = Field(default=None)
    fax: str | None = Field(default=None)
    first_name: str | None = None
    full_name: str | None = None
    hourly_rate: float | None = Field(default=None)
    id: int
    inactive_by_id: int | None = Field(default=None)
    jira_account_id: str | None = Field(default=None)
    last_name: str | None = None
    last_sync_date: datetime | None = Field(default=None)
    last_sync_source: str | None = Field(default=None)
    manager_id: int | None = Field(default=None)
    offboarding_date: date | None = Field(default=None)
    otp_required_for_login: bool | None = Field(default=None)
    password_changed_at: datetime | None = Field(default=None)
    payment_term_id: int | None = Field(default=None)
    phone_number: str | None = Field(default=None)
    role_id: int
    salesforce_id: int | None = Field(default=None)
    secure_code: str | None = Field(default=None)
    services_count: int | None = Field(default=None)
    settings_access: bool | None = Field(default=None)
    show_announcement: bool | None = Field(default=None)
    show_app_updates: bool | None = Field(default=None)
    status: int
    stock_asset_current_checkout_view: bool | None = Field(default=None)
    subscribed_to_emails: bool | None = Field(default=None)
    # Note: team is weird. Used to be just an int. Now, appears to be a multi-value
    # situation where you get a list of values back. However, API is inconsistent.
    # Sometimes you'll get back team_id, sometimes team_ids.
    team_id: int | list[int] | None = None
    team_ids: int | list[int] | None = None
    time_zone: str | None = Field(default=None)

    def model_post_init(self, __context: Any) -> None:
        """
        Normalize team_id / team_ids inconsistencies from API responses.
        Ensures team_ids is always a list[int], even if API returns a single int or null.
        """
        # Prefer team_ids if present
        if self.team_ids is not None:
            if isinstance(self.team_ids, int):
                self.team_ids = [self.team_ids]
            elif isinstance(self.team_ids, list):
                self.team_ids = [int(x) for x in self.team_ids if x is not None]
        elif self.team_id is not None:
            # Handle team_id if team_ids not provided
            if isinstance(self.team_id, int):
                self.team_ids = [self.team_id]
            elif isinstance(self.team_id, list):
                self.team_ids = [int(x) for x in self.team_id if x is not None]
            else:
                self.team_ids = []
        else:
            # Neither provided
            self.team_ids = []

        # Ensure consistency: keep team_id as first element if exists
        if self.team_ids:
            self.team_id = self.team_ids[0]
        else:
            self.team_id = None

    unseen_app_updates_count: int | None = Field(default=None)
    unsubscribed_by_id: int | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)
    user_listing_id: int | None = Field(default=None)
    work_location: int | None = Field(default=None)
    zendesk_account_id: int | None = Field(default=None)


class MemberCreate(BaseModel):
    """
    A model representing the data required to create a new member.
    """

    first_name: str | None = None
    last_name: str
    role_id: int
    email: str
    employee_identification_number: str | None = None
    department: str | None = None
    description: str | None = None
    team_ids: list[int] | None = None
    user_listing_id: int | None = None
    login_enabled: bool | None = None
    subscribed_to_emails: bool | None = None
    skip_confirmation_email: bool | None = None
    address_name: str | None = None
    address: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country: str | None = None
    fax: str | None = None
    phone_number: str | None = None
    image_url: str | None = None
    work_location: int | None = None
    custom_fields: list[dict] | None = None


class CustomRole(BaseModel):
    """
    A custom role represents some non-default set of permissions that
    can be assigned to members.
    """

    id: int
    name: str
    description: str
    created_by_id: int
    base_role_id: int
    visibility: str
    users_visibility: str
    system_generated: bool
    group_ids: list[int] | None = None
    team_ids: list[int] | None = None
    location_ids: list[int] | None = None


class UserListing(BaseModel):
    id: int
    name: str
    default: bool
    include_sub_locations: bool
    created_at: datetime
    updated_at: datetime


class WorkOrder(BaseModel):
    """
    A work order represents some assignment to be given. Can be attached
    to a particular item or a location. Repairing something, cleaning, maintenance, etc.
    """

    class AssociatedAsset(BaseModel):
        name: str
        id: int

    approver_id: int | None = Field(default=None)
    assigned_to_id: int | None = Field(default=None)
    assigned_to_type: str
    asset_id: int | None = None
    associated_assets: list[AssociatedAsset] | None = None
    associated_checklists: list
    base_cost: float
    completed_on: str | None = Field(default=None)
    create_one_task_for_all_items: bool
    create_recurring_service_zendesk_tickets: bool
    created_at: datetime | None = Field(default=None)
    created_by_id: int | None = Field(default=None)
    creation_source: str | None = Field(default=None)
    custom_fields: list[dict] | None
    description: str | None = Field(default=None)
    display_next_service_immediately: bool
    due_date: datetime | None = Field(default=None)
    expected_start_date: datetime | None = Field(default=None)
    id: int
    inventory_cost: float
    inventory_cost_method: str | None = Field(default=None)
    is_item_component: bool
    is_triage: bool
    location_id: int | None = Field(default=None)
    mark_items_unavailable: bool
    preventive_maintenance: bool
    priority: str
    project_id: int | None = Field(default=None)
    recurrence_based_on_completion_date: bool
    recurrence_task_id: int | None = Field(default=None)
    repeat_every_basis: int | None = Field(default=None)
    repeat_every_value: int
    repetition_end_date: str | None = Field(default=None)
    repetition_starting: str | None = Field(default=None)
    requested_by_id: int | None = Field(default=None)
    require_approval_from_reviewer: bool
    reviewer_id: int | None = Field(default=None)
    secondary_assignee_ids: list[int] = Field(default=[])
    service_for_sub_groups_only: bool
    service_type_id: int | None = Field(default=None)
    shipping_address_id: int | None = Field(default=None)
    start_work_on_all_assets: bool
    started_on: str | None = Field(default=None)
    state: str
    supervisor_id: int | None = Field(default=None)
    task_type: str
    task_type_id: int | None = Field(default=None)
    template_id: int | None = Field(default=None)
    time_spent: float
    # time_to_respond:
    time_to_start: int
    title: str
    total_cost: float
    track_progress: float
    updated_at: str
    warranty: bool | None = Field(default=False)
    work_logs_cost: float
    work_type_name: str | None = Field(default=None)
    zendesk_ticket_id: int | None

    # Custom fields
    depot: str | None = Field(default=None)
    depot_id: int | None = Field(default=None)

    def model_post_init(self, __context: Any) -> None:
        # Parse custom fields.
        if self.custom_fields:
            # Create lookup dictionary
            field_values = {
                field.get("id"): field.get("value")
                for field in self.custom_fields
                if "id" in field
            }

            # Process Depot
            if CustomFieldID.DEPOT.value in field_values:
                value = field_values[CustomFieldID.DEPOT.value]
                if value and isinstance(value, str):
                    self.depot = value
                    self.depot_id = int(value[:2])


class WorkLog(BaseModel):
    """
    Work orders can have one or more logs of work attached to them.
    Each representing some block of time spent working on the work order along
    with any details.
    """

    user_id: int
    time_spent: str | None = None
    work_detail: str | None = None
    associated_to_asset_id: int | None = None
    started_on: datetime | None = None
    ended_on: datetime | None = None


class DepreciationRate(BaseModel):
    """
    A depreciation rate is how quickly assets depreciate in value over time.
    Some more quickly than others.
    """

    id: int
    depreciation_method_id: int
    depreciation_method_name: str
    rate: str | None = None
    useful_life: int | None = None


class Group(BaseModel):
    """
    A group in EZO is a way of categorizing assets. You can have groups, as well
    as subgroups that exist in a hierarchy beneath their parent group.
    """

    id: int
    name: str
    description: str | None = None
    enable_service_triage: bool
    triage_completion_period: int | None = None
    triage_completion_period_basis: str | None = None
    allow_staff_to_set_checkout_duration: bool
    staff_checkout_duration_months: int
    staff_checkout_duration_weeks: int
    staff_checkout_duration_days: int
    staff_checkout_duration_hours: int
    staff_checkout_duration_mins: int
    available_assets_count: int
    visible_on_webstore: bool
    hidden_on_webstore: bool
    created_at: datetime
    documents_count: int
    asset_depreciation_mode: str
    comments_count: int | None = None
    depreciation_rates: list[DepreciationRate] | None = None
    parent_id: int | None = None
    group_id: int | None = None


class Team(BaseModel):
    """
    A team is a way of categorizing members. Previously, a member could be on
    a single team. Now, a member can be assigned to multiple.
    """

    id: int
    name: str
    description: str
    parent_id: int | None = None
    identification_number: str
    documents_count: int
    comments_count: int


class Project(BaseModel):
    """
    A project is a higher-level categorization. Can be attached to various events and assets.
    Typically would be used for reporting on expenses or what have you on temporary projects.
    """

    id: int
    name: str
    description: str | None = None
    created_by_id: int
    state: str
    documents_count: int
    comments_count: int
    identifier: str
    linked_modules: list[
        Literal[
            "items",
            "checkouts",
            "reservations",
            "purchase_orders",
            "work_orders",
            "carts",
            "locations",
        ]
    ]


class CustomFieldHistoryItem(BaseModel):
    id: int
    value: str | None = None
    number_value: int | float | None = None
    date_value: date | None
    options_value: Any | None
    date_time_value: datetime | None = None
    line_item_id: int | None = None
    linkable_resource_value: Any | None
    created_at: datetime
    updated_at: datetime


class StockHistoryItem(BaseModel):
    id: int
    quantity: int
    price: str
    comments: str | None = None
    created_by_id: int
    basket_id: int | None = None
    is_transfer: bool
    is_custody_transfer: bool
    retire_reason_id: int | None = None
    quantity_after_transaction: int
    order_type: str
    remaining_quantity: int | None = None
    retire_reason: str | None = None
    checked_out_to_location_id: int | None = None
    checked_in_from_location_id: int | None = None
    vendor_id: int | None = None
    checkout_line_item_id: int | None = None
    purchase_order_id: int | None = None
    basket_asset_id: int | None = None
    service_id: int | None = None
    cost_price: str | None = None
    unit_cost_price: list[dict] | None
    task_id: int | None = None
    check_out_to_asset_id: int | None = None
    paired_transfer_line_item_id: int | None = None
    project_id: int | None = None
    original_quantity: int | None = None
    signed_by_name: str | None = None
    transfer_from_location_id: int | None = None
    transition_to_substate_id: int | None = None
    action_source: str | None = None
    cost_valuation_method: str | None = None
    signature_image_id: int | None = None
    item_audit_id: int | None = None
    linked_inventory_item_id: int | None = None
    parent_id: int | None = None
    agreement_document_id: int | None = None
    agreement_accepted: bool | None = None
    user_full_name: str | None = None
    for_retiring_checked_out_stock: bool | None = None
    asset_name: str | None = None
    transition_from_substate_id: int | None = None
    checkout_on: datetime | None = None
    checkin_on: datetime | None = None
    purchased_on: datetime | None = None
    checkin_due_on: datetime | None = None
    created_at: datetime
    updated_at: datetime


class Reservation(BaseModel):
    id: int
    resource_id: int
    reservable_id: int
    reservable_type: str
    from_date: datetime
    note: str | None = None
    status: str
    to_date: datetime | None = None
    action_taken_by_id: int
    created_by_id: int
    quantity: int
    location_id: int
    price: float | None = None
    package_id: int | None = None
    basket_id: int | None = None
    baskets_asset_id: int | None = None
    signature_image_id: int | None = None
    reserved_to_location_id: int | None = None
    denied_reason: str | None = None
    recurring_reservation_id: int | None = None
    transition_from_substate_id: int | None = None
    signed_by_name: str | None = None
    project_id: int | None = None
    resource_type: str | None = None
    creation_source: str | None = None
    approved_or_denied_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TokenInput(BaseModel):
    id: int
    name: str


class AssetHistoryItem(BaseModel):
    id: int
    assigned_to_id: int
    created_by_id: int
    is_checkout: bool | None = None
    location_id: int | None = None
    comments_count: int | None = None
    package_id: int
    basket_id: int | None = None
    is_transfer: bool | None = None
    checked_out_duration_in_seconds: int
    rent_collected: str | None = None
    signed_by_name: str | None = None
    signature_image_id: str | None = None
    action_source: str | None = None
    past_checkout: bool
    assigned_to_type: str
    basket_asset_id: int | None = None
    agreement_document_id: int | None = None
    agreement_accepted: bool | None = None
    assigned_to_name: str | None = None
    assigned_asset: str | None = None
    project_id: int | None = None
    checkin_due_on: datetime | str | None = None
    actual_checkin_on: datetime | str | None = None
    checkin_on: datetime | str | None = None
    checkout_on: datetime | None = None
    created_at: datetime
    updated_at: datetime


class Bundle(BaseModel):
    id: int
    name: str
    description: str | None = None
    identification_number: str | None = None
    location_id: int | None = None
    documents_count: int | None = None
    comments_count: int | None = None
    state: str
    enable_items_restricted_by_location: bool
    allow_add_bundle_without_specifying_items: bool
    created_at: datetime
    updated_at: datetime
    line_items: list[dict]
    custom_fields: list[dict]


class PurchaseOrder(BaseModel):
    id: int
    description: str | None = None
    title: str | None = None
    identification_number: str | None = None
    requested_by_id: int | None = None
    created_by_id: int | None = None
    approved_by_id: int | None = None
    approver_type: str | None = None
    approver_id: int | None = None
    payment_terms: str | None = None
    notes: str | None = None
    shipment_terms: str | None = None
    vendor_id: int | None = None
    state: str | None = None
    net_amount: str | None = None
    payable_amount: str | None = None
    paid_amount: str | None = None
    documents_count: int | None = None
    comments_count: int | None = None
    tax_amounts: dict | None = None
    po_type: str | None = None
    project_id: int | None = None
    contract_id: int | None = None
    receiving_notes: str | None = None
    invoice_number: str | None = None
    time_to_respond: int | None = None
    currency_id: int | None = None
    delivery_location_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    confirmed_at: datetime | None = None
    requested_on: datetime | None = None
    completed_on: datetime | None = None
    delivery_date: datetime | None = None
    custom_fields: list[dict]
    line_items: list[dict]


class Package(BaseModel):
    package_id: int
    name: str
    asset_ids: list[int]
    description: str | None = None
    arbitration: str | None = None


class RetireReason(BaseModel):
    id: int
    name: str
    active: bool
    system_generated: bool
    include_in_shrinkage: bool
    created_at: datetime
    updated_at: datetime


class Vendor(BaseModel):
    id: int
    name: str
    address: str | None = None
    contact_person_name: str | None = None
    website: str | None = None
    description: str | None = None
    email: str | None = None
    fax: str | None = None
    phone: str | None = None
    status: bool
    custom_fields: list[dict]


class StockAsset(BaseModel):
    """
    A stock asset represents some non-unique asset (i.e. not serialized).
    Similar to an Inventory,however you can both check asset stock in or out.
    Whereas an Inventory will only ever be checked out.
    """

    name: str
    description: str | None = None
    cost_price: str | None = None
    identifier: str | None = None
    audit_pending: bool
    product_model_number: str | None = None
    documents_count: int
    pending_verification: bool
    comments_count: int
    state: str | None = None
    salvage_value: str | None = None
    vendor_id: int | None = None
    group_id: int
    bulk_import_id: int | None = None
    location_id: int | None = None
    depreciation_calculation_required: bool
    package_id: int | None = None
    purchase_order_id: int | None = None
    retire_comments: str | None = None
    retire_reason_id: int | None = None
    sub_group_id: int | None = None
    arbitration: int | None = None
    last_history_id: int | None = None
    retired_by_id: int | None = None
    item_audit_id: int | None = None
    sub_checked_out_to_id: int | None = None
    last_assigned_to_id: int | None = None
    manufacturer: str | None = None
    sunshine_id: int | None = None
    latest_contract_id: int | None = None
    custom_substate_id: int | None = None
    id: int
    display_image: str | None = None
    primary_user: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    checkin_due_on: datetime | None = None
    retired_on: datetime | None = None
    checkout_on: datetime | None = None
    purchased_on: datetime | None = None
    last_checked_out_at: datetime | None = None
    last_checked_in_at: datetime | None = None
    synced_with_jira_at: datetime | None = None
    custom_fields: list[dict]
    net_quantity: int | None = None
    available_quantity: int | None = None
    inventory_threshold: int | None = None
    location_based_threshold: int | None = None
    initial_stock_quantity: int | None = None
    default_excess_location_threshold: int | None = None
    average_cost_per_unit: str | None = None


class LinkedInventory(BaseModel):
    inventory_id: int
    quantity: int
    id: int | None = None
    location_id: int | None = None
    work_order_id: int | None = None
    asset_id: int | None = None
    cost_price: str | None = None
    original_quantity: int | None = None
    resource_id: int | None = None
    resource_type: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ResourceDocument(BaseModel):
    """
    EZOffice allows attaching files onto various resources. Such as on assets, locations, etc.
    Resource document seems fairly open-ended in terms of what type of file it can be. Referred
    to in the API as document as a generality.
    """

    can_show: bool
    id: int
    description: str | None = None
    content_type: str | None = Field(alias="attachment-content-type", default=None)
    file_name: str | None = Field(alias="attachment-file-name", default=None)
    thumbnail_path: str | None = Field(alias="attachment-thumbnail-path", default=None)
    path: str | None = Field(alias="attachment-path", default=None)
    url: str | None = Field(alias="attachment-url", default=None)
    updated_at: datetime | None = Field(alias="attachment-updated-at", default=None)
    created_at: datetime | None = Field(alias="created-at", default=None)
