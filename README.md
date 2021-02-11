# SmartThings Direct-connected Devices for Alarmserver

This repository contains files to implement alarmserver on a Raspberry Pi with device applications using SmartThings direct-connected device API.  A device application will be instantiated for each DSC zone, plus a device application representing the DSC Panel.  Whereas in legacy SmartThings implementations, a separate Stay and Away panel was needed for automation linkage with SmartThings Home Monitor, here only one panel is needed.

Zones device apps can optionally display a GUI window on the Raspbery Pi desktop (one for each zone).  Alternatively they can be run in background with logfiles.
The panel device app, in addition to handling the panel device interface to SmartThings, will also display a full DSC panel GUI window on the Pi desktop for local monitoring and control of the alarm system.  For those not running the Pi desktop, I can provide a non-GUI version upon request.

### Limitations
- Only one DSC partition is currently supported
- Smoke and CO2 zones have not been tested
- In the legacy SmartThings platform, the alarmserver zone devices were automatically generated by a smartapp - a nice feature.  Unfortunately here they will need to be manaually defined in the Developer Workspace, and initially onboarded via the mobile app one at a time.  However this is a one-time-only setup task.

## Pre-requisites
- Installed, configured, and running Direct-connect enablement package for Raspberry Pi (rpi-st-device): https://toddaustin07.github.io/
- Installed, configured, and running alarmserver package: https://github.com/rtorchia/DSC-Envisalink/tree/master/alarmserver
- SmartThings personal token: https://smartthings.developer.samsung.com/docs/auth-and-permissions.html

## Automated Setup Tools

### ASdevsetup
Run this script using one argument that is the full pathname of your alarmserver.cfg file.  The script will read your alarmserver.cfg file to get your defined zones, set up device subdirectories, create device serial numbers, initialize a device loader script (loaddevs), and modify alarmserver.cfg.  Upon successful completion, a file called 'serialnums' will be created that contains a sorted list of the created device serial numbers that you can use to copy and paste into the Developer Workspace device profiles later on. 

Note: this script depends on the core SDK repository tool 'stdk-keygen', so prior installation via my rpi-st-devices package is required.

### STcapabilities.py: auto creation/update/delete of SmartThings custom capabilities 
A python script is provided in the json/capabilities directory that will create all custom capabilities and presentations under your account.  First edit the STcapabilities.py script with your SmartThings personal token and then run it with the argument of 'create' within the json directory.  It will iterate through the capability json files (provided in 'base' subdirectory) to create 10 custom capabilities along with their presentations via the SmartThings API.  Returned json strings are written to file for each capability in the 'created' subdirectory.  Note your assigned capability id prefix.  You can also use this tool to update the capabilities and presentations by modifying the files in the 'created' subdirectory and running STcapabilities.py with the 'update' argument.  Finally, Using a 'delete' argument, this tool will delete all capabilities and presentations as contained in the 'created' directory. (For now, it does not delete the local json files in the 'created' subdirectory - just in case you wanted to archive them!)

### Device Onboarding Helper (wip)
Run this script once everything is configured & installed, i.e. ASdevsetup is complete, device projects are defined in Developer Workspace, and onboarding_config.json files have been downloaded to the device subdirectories.
This script will automate the creation of QR codes for each device (used by mobile app during initial device onboarding) and ensure everything is prepared for initial provisioning of all device apps (zone + panel)

Note: this script depends on the core SDK repository tool 'stdk-qrgen', so prior installation via my rpi-st-devices package is required.

### Additional scripts
- startall - master startup script to load (1) zone device apps & panel (post initial onboarding), (2) DSCmanager, (3) alarmserver; this is optional- you can configure loading anyway you like, e.g. auto-load at boot time through systemd, etc
- buildloader - used by ASdevsetup; creates loaddevs script that is used by DSCmanager to start up each device app (zones + panel)
- loaddevs - used by DSCmanager to load all device apps at startup 
- STdevsn - list serial numbers associated with each device app


## Manual Setup Tasks

### Create SmartThings device profiles
This is done in the Developer Workspace.  One project/device profile must be created for each TYPE of device you are using (e.g. panel, contact, motion, smoke, CO2)
Recommended parameters to use in the Developer Workspace device profile definition screens are as follows:
```
                               DSC Panel              Contact Device          Motion Device        
                               --------------------   --------------------    ---------------------
Device Profile
  Name                         DSC_Panel              DSC_Contact             DSC_Motion     
  Version                      0.1                    0.1                     0.1
  Device Type                  Switch                 ContactSensor           MotionSensor
  Components & Capabilities*   Health Check (opt)     Health Check (opt)      Health Check (opt)
                               partitionStatus        contactStatus           motionStatus
                               partitioncommand       zonebypass              zonebypass
                               dscdashswitch
                               dscstayswitch
                               dscawayswitch
                               dscselectswitch

Onboarding
  Onboarding name                               <<  DSC Zone Device >>
  Authentication type                                << ED25519 >>
  Setup ID                                              << 02 >>
  Instructions                                  << whatever you'd like >>

Product Info
  Category                                           << WiFi/Hub >>
  Availability                                 << United States (or other) >>
  Model Number / SKU           DSC_PANEL001           DSC_CONTACT001           DSC_MOTION001

 
  
  UI Display*                         << 'Customize through device configuration file' >>

```
#### Components & Capabilities
All are defined under 'main' component.  All capabilities besides 'Health Check' are custom that you built in prior step. Filter the capability list for 'My Capabilities', and you should see all the ones you have created.  Select the corresponding capabilities listed in the table above.

#### UI Display
You will choose the option to 'Customize through device configuration file'. First download the file using the link on the page.  You will upload a new file, but you need to get the mnmn and VID values from the downloaded file first.  Edit the applicable device configuration json file provided in the json/deviceconfigs directory of this repository (deviceConfigST_panel.json, deviceConfigST_contact.json, deviceConfigST_motion.json).  Update the file with the mnmn and VID from the file you downloaded.  Then do a global search and replace of the five asterisks with your unique capability id prefix.  Save the file and then upload it.  Complete these steps for each project/device profile (panel, contact, motion, etc).

#### Test Devices (this is a noun, not a verb!)
In this part of the Developer Workspace setup, you identify the serial numbers of the devices you'll be using under each profile.  You can use the STdevsn tool referenced earlier to get a convenient list of these that were created when you ran ASdevsetup.  On the Developer Workspace Test Devices screen, click on the 'REGISTER NEW DEVICE' button for each zone/panel device and copy/paste the serial number.  

### Download onboarding_config.json files
When complete with the above, onboarding_config.json files - generated by the Developer Workspace when you define your device profiles - must be downloaded and placed in each of the appropriate device directories (one json file per device type)


### Initial onboarding/provisioning of each zone device + panel device using mobile app
You will use the onboarding helper script (wip) and SmartThings mobile app to connect with each of the zone & panel device apps on your Raspberry Pi via wireless in order to complete onboarding of each device (one per zone + panel).

### Using the DSC device apps in the SmartThings Mobile App
The first thing you will want to do after your devices are onboarded and happily humming away on your Pi is to go into the mobile app and group the DSC devices into a room, and rename each of them to something useful.  I use of combination of zone number (Z1) and VERY abbreviated zone description - short enough to fit on the dashboard card.  

The zone devices have no action buttons on the dashboard - just the status of the device (open/closed, motion/no motion, etc.).  On the details screen, you'll see a zone status field, which most of the time will show the open/close-type status of the device, but may also show other states such as alarm, trouble, bypassed, etc.  Also on the details screen is a slider switch you can use to turn on and off bypass state for the zone.

The panel device has a bit more function.  On the dashboard, the button is used to arm or disarm the partition.  Whether it performs an arm-away or arm-stay is configured on the details screen (explained below).  The state shown on the dashboard is whatever the DSC is reporting such as ready, not ready, exit delay, armed-away or armed-stay, alarm, etc.  I have eliminated the force-ready status since it's not very useful and in the old alarmserver implementation always caused a crazy amount of constant state changes, filling up the log and messages everytime someone opened a door or walked by a motion sensor.

The dashboard icon on the panel device is supposed to be gray when in Ready state, and color highlighted for anything else.  There is currently a bug where this is not working on IOS mobile devices.

The panel device detail screen has a number of features.  First is the partition status - same as what is shown on the dashboard.  Next are discrete buttons to arm stay or arm away (or disarm afterwards).  Then there is a button to bring up a list of additional partition commands that can be invoked.  Finally there is a toggle button to configure what happens when you tap the button on the dashboard.  It can be set to either type=arm-away or type=arm-stay, whichever you prefer.  Remember you can always go to the details screen to directly arm either way, no matter how the dashboard button is configured.  The detail screen discrete arm buttons will probably be what you want to use for THEN action from automations and Partition Status can be used as the IF condition to trigger automations based on your security system status.

### Operational Specifics:

Alarmserver is re-directed via its config file to send/receive messages to a locally running process on your Pi (DSCmanager), rather than to the former SmartThings graph URL.  DSCmanager then acts as traffic coordinator to forward messages to the appropriate zone/panel device app.  The device apps are connected to SmartThings via the direct-connect API using the ST core SDK (which uses MQTT in the background).  Messages from SmartThings (commands and state changes) are received directly by the respective Pi device app, which in turn routes commands back down to alarmserver via DSCmanager.  UNIX named sockets are used for all IPC between DSCmanager and device apps because it is fast and efficient.  All applications are written and compiled C for optimal speed and compactness.  

GUI displays are implemented with GTK3+.  If there is little interest in the GUI's, I may remove that code for the sake of further efficiency, since it does add quite a bit of required memory.

Loading of device apps is initiated by DSCmanager through a bash script so that users can modify it for preference of running apps in foreground vs. background, piping output to logfiles, GUI option selection, etc.
