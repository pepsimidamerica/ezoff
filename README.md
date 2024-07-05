# ezo

Python package for interacting with the EZOffice API

## Installation

Add as a git submodule for now. Intend on at some point making available as a proper package.

## Usage

Several environment variables are required for ezo to function.

| Required? | Env Variable | Description |
| --------- | ------------ | ----------- |
| EZO_BASE_URL | Yes | Should be https://{companyname}.ezofficeinventory.com/ |
| EZO_TOKEN | Yes | The access token used to authenticate requests |

## Project Structure

Project is split up into several files depending on what area of the EZOffice API is being dealt with. Purely for organizational purposes.

### Assets

### Groups

### Locations

### Members

### Work Orders

## Notes

The documentation is mistaken on custom fields (insofar as filling them out when creating an object or updating the custom field on an already existing object). It says to put underscores in place of spaces in the field name, but this is incorrect. After testing the API, it appears it wants the actual name of the field with the spaces, not underscores. At least on members.

Similarly, the documentation isn't exhaustive when it comes to listing the valid fields when creating or updating something. Frequently there are fields on the actual page that aren't mentioned in the EZOffice documentation. Throughout program I check for that keys provided are valid to prevent the API call from erroring out. Just have to add to list of valid key whenever we run into one.

When wanting to clear a field out of its current value with an update function, generally the empty string ("") should be used.
