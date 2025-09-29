"""
Module contains any enums used throughout the package.
"""

from enum import Enum


class AssetClass(Enum):
    BILL_CHANGER = "Bill Changer"
    BULK_CO2 = "Bulk CO2"
    COFFEE = "Coffee"
    COOLER = "Cooler"
    FOUNTAIN = "Fountain"
    MICRO_MARKET = "Micro Market"
    REMOVE = "Remove"
    SLUSH = "Slush"
    TEA = "Tea"
    TEST = "Test"
    VENDOR = "Vendor"
    WATER = "Water"


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
    LOCATION_CLASS = 845
    BC_VENDOR_ID = 1229
    BC_VENDOR_NAME = 1228
    BC_VENDOR_REMIT_ADDR_CODE = 1230
    BC_DEPT_ID = 1231
    PEPSICO_PARENT_OUTLET_ID = 1308


class LocationClass(Enum):
    NONE = "None"
    MARKET = "Micro Market"


class RentLoan(Enum):
    RENT = "Rent"
    LOAN = "Loan"


class ResourceType(Enum):
    """Ez Office component (resource) type."""

    ASSET = "Asset"
