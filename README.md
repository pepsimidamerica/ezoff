# ezoff

Python package for interacting with the EZOffice API. Includes support for v1 and v2 EZ Office API endpoints.

Base URL for v1: https://{company name}.ezofficeinventory.com/
Base URL for v2: https://{company name}.ezofficeinventory.com/api/v2/

## Rewrite

There will be a number of breaking changes.

- General cleanup of type hints and docstrings.

## Installation

`pip install ezoff`

## Usage

Several environment variables are required for ezo to function.

| Required? | Env Variable | Description |
| --------- | ------------ | ----------- |
| EZO_SUBDOMAIN | Yes | Should be your company name. Can be found in the URL of your EZO instance, https://{companyname}.ezofficeinventory.com/ |
| EZO_TOKEN | Yes | The access token used to authenticate requests |

## Project Structure

Project is split up into several files depending on what area of the EZOffice API is being dealt with. largely corresponds to how the API v2 documentation is laid out, purely for organizational purposes.

## Notes

When wanting to clear a field out of its current value with an update function, generally the empty string ("") should be used as the new value.
