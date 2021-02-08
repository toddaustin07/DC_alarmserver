# SmartThings Direct-connected Devices for Alarmserver

This repository contains files to implement alarmserver on a Raspberry Pi with device applications using SmartThings direct-connected device API.  A device application will be instantiated for each DSC zone, plus a device application representing the DSC Panel.  Whereas in legacy SmartThings implementations, a separate Stay and Away panel was needed for automation linkage with SmartThings Home Monitor, here only one panel is needed.

Zones device apps can optionally display a GUI window on the Raspbery Pi desktop (one for each zone).  Alternatively they can be run in background with logfiles.
The panel application, in addition to handling the device interface to SmartThings, will also display a full DSC panel GUI window on the Pi desktop for local monitoring and control of the alarm system.

## Pre-requisites
-Direct-connect enablement github package for Raspberry Pi (rpi-st-device): https://toddaustin07.github.io/
-Installed and configured alarmserver package: https://github.com/rtorchia/DSC-Envisalink/tree/master/alarmserver

## Manual Setup Tasks
1) Creation of SmartThings custom capabilities: this can be done through the CLI tool or through the API with tools like Postman; all json is provided in this package
note: This task will hopefully be greatly simplified if/when custom capabilities can be shared; or when further automation tools for these steps are added to this package
2) Creation of SmartThings device profiles in the Developer Workspace: ONE for each device TYPE needed (types=panel, contact, motion, smoke, co2)

## Automated Setup Tools
Some scripts are provided to automate installation and setup:

### ASdevsetup
Run this script in your alarmserver directory.  It will read your alarmserver.cfg file to get the defined zones and will then automate creation of device serial numbers and set up each zone device subdirectory with required files.  Note: this depends on prior install of rpi-st-device package.


