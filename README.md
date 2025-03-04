# What's Brewing?
This is a simple application for reading and displaying information from Brewfather. The main purpose is to provide a quick overview of available beers, progress of any beers getting ready, and use a touch screen to assign the beers to a specific tap. The software is meant to run on a pi zero 2 w with a waveshare touchscreen display. Updates are triggered manually since the data changes very infrequently for my usage.

At most my brewery can support 3 kegs at a time. Information is queried from Brewfather and only brews that are not 'Archived' will have additional detailed information. The types of information can be expanded as you see fit, just clone and have fun.

# Software:
The following python libraries are used:
- PySide6
- requests

# Hardware:
Currently using a Raspberry Pi zero 2 w with a Waveshare 7" touch screen display.

# Usage:
Clone the repository on your platform, and install the python libraries above. Add execute privelages with 'chmod +x whatsbrewing.py'.

You will need to create an API key within brewfather. The auth.json file that needs to be created will have two keys to fill in, 'username' and 'passkey'. These keys are used to query the brewfather API.

Run the softwar with 'python3 ./whatsbrewing.py'. Will be adding to system as well, details later.
