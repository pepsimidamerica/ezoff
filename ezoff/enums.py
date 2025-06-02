# from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
# from datetime import datetime, date
from enum import Enum

class ResourceType(Enum):
    """Ez Office component (resource) type."""

    ASSET = "Asset"


class CustomFieldID(Enum):
    DEPOT = 739
    EST_SVC_MINUTES = 728
    RENT_FLAG = 70779
    TAX_JURISDICTION = 738
    NAT_ACCOUNT = 739
    CANTEEONE_CODE = 740
    PARENT_CUST_CODE = 771
    EXCLUDE_RENT_FEES = 823
    ASSET_SERIAL_NO = 66133
    ASSET_CLASS = 71024


class RentLoan(Enum):
    RENT = "Rent"
    LOAN = "Loan"

    