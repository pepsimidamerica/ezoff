# ezoff

Python package for interacting with the EZOffice API.

Note: a [v2 of the API](https://www.ezofficeinventory.com/api-docs/index.html) exists. Working on moving existing functions over from the v1 I was aware of to the v2. Intent is to first replace existing functions with the V2 endpoints. Then at some point move on adding endpoints that haven't yet been used.

## Installation

Package is published to [PyPI](https://pypi.org/project/ezoff/) so installation should be as simple as below:

`pip install ezoff`

## Usage

Two environment variables are required for ezoff to function.

| Env Variable | Description |
| ------------ | ----------- |
| EZO_BASE_URL | Should be https://{companyname}.ezofficeinventory.com/ |
| EZO_TOKEN | The access token used to authenticate requests |

An API access token can be created in the EZOffice tenant settings under the "Integrations" heading.

## Package Structure

The ezoff package is split up into several files depending on what area of the EZOffice API is being dealt with. Purely for organizational purposes.

Below is a listing of functions in ezoff. It is not yet exhaustive in terms of what the underlying API can do. But it covers some of the functionality that I expect is most commonly used.

### Assets

Contains functions for the following:

- get all asssets
- get filtered assets
- search for an asset
- create an asset
- update an asset
- delete an asset
- check asset in
- check asset out
- get an asset's history

### Inventories

- get inventories
- get inventory details
- create inventory order
- get inventory history

### Groups

Contains functions for the following:

- get groups
- get a specific group
- get subgroups

### Locations

Contains functions for the following:

- get locations
- get location details
- get item quantities in location
- create a location
- activate a location
- deactivate a location
- update a location

### Members

Contains functions for the following:

- get members
- get a member's details
- create a member
- update a member
- deactivate a member
- activate a member
- get custom roles
- get teams

### Work Orders

Contains functions for the following:

- get work orders
- get work order details
- get work order types
- create a work order
- start a work order
- end a work order
- add work log to a work order
- add linked inventory to a work order
- get checklists

## Notes

When wanting to clear a field out of its current value with an update function, generally the empty string ("") should be used.

### API V2 Migration

Making note of any peculiarities I find while moving each function to the API V2 endpoint. WIP, things may change here as I do further testing.

- get_group - Returns asset info. Seems to give a listing of assets that are in that group, rather than info about the group.

- get_subgroups - Doesn't appear to be valid endpoint, was getting a 404
