# ezoff

Python package for interacting with the EZOffice API. Includes support for v1 and v2 EZ Office API endpoints.

Base URL for v1: https://{company name}.ezofficeinventory.com/
Base URL for v2: https://{company name}.ezofficeinventory.com/api/v2/

## Rewrite

There will be a number of breaking changes.

- Remove all v1 endoints where there is a corresponding v2 endpoint.
- Normalize function names for easier discoverability, e.g. get_asset_details -> asset_get_details
- ~~Rename some of the files so we don't have both hanging around. Consolidate v1 and v2 together.~~
- Perhaps add flag to each Get function to return either the pydantic object or the raw request response? Could be useful to have the option. Or just say fuck it and have pydantic models for everything.
- General cleanup of type hints and docstrings.
- Maybe just ask for the subdomain for the os env var, as opposed to base URL? Would be easier with regards to slashes and the v1 and v2 endpoints.

## Installation

`pip install ezoff`

## Usage

Several environment variables are required for ezo to function.

| Required? | Env Variable | Description |
| --------- | ------------ | ----------- |
| EZO_SUBDOMAIN | Yes | Should be your company name. Can be found in the URL of your EZO instance, https://{companyname}.ezofficeinventory.com/ |
| EZO_TOKEN | Yes | The access token used to authenticate requests |

## Project Structure

Project is split up into several files depending on what area of the EZOffice API is being dealt with. Purely for organizational purposes.

- Assets
- Checklists
- Groups
- Inventories
- Locations
- Members
- Projects
- Work Orders

## Notes

When wanting to clear a field out of its current value with an update function, generally the empty string ("") should be used.
