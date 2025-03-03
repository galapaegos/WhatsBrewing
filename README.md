# WhatsBrewing
This is a simple application for reading and displaying information from Brewfather. The main purpose is to provide a quick overview of the available beers, and uses a touch screen to assign the beers to a specific tap. The software is meant to run on a pi zero 2 w with a waveshare display. Updates are triggered manually since the data changes very infrequently for my usage.

At most my brewery can support 3 kegs at a time. This software is designed to let me assign a keg to a tap number and provide high-level information for any garage gatherings. Information is queried from Brewfather manually, and only applied to brews that are not 'Archived'. The types of information can be expanded as you see fit.

# Software:
The following python libraries are used:
- PySide6
- requests

# Hardware:
Currently using a Raspberry Pi zero 2 w with a Waveshare 7" touch screen display.

# Usage:
You will need to create an API key within brewfather. The auth.json file that needs to be created will have two keys to fill in, 'username' and 'passkey'. 


