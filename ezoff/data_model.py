from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class ChecklistV2(BaseModel):
    id: int
    name: str
    created_by_id: int
    line_items: list


class MemberV2(BaseModel):
    name: str
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    employee_identification_number: str
    fax: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    phone_number: int
    # time_zone: 
    address: Optional[str] = Field(default=None)
    city: Optional[str] = Field(default=None)
    state: Optional[str] = Field(default=None)
    country: Optional[str] = Field(default=None)
    zip_code: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    display_picture_url: Optional[str] = Field(default=None)
    department: Optional[str] = Field(default=None)

class WorkOrderV2(BaseModel):
    approver_id: Optional[int] = Field(default=None)
    assigned_to_id: Optional[int] = Field(default=None)
    assigned_to_type: str
    associated_checklists: list
    base_cost: float
    completed_on: Optional[str] = Field(default=None)
    create_one_task_for_all_items: bool
    create_recurring_service_zendesk_tickets: bool
    created_at: str
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
