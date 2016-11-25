#![MPLogo](Docs/Images/MPLogo_64x64.png "MPLogo") MacPatch 3

## Status

**WARNING MacPatch 3.x is currently in development. Script and code may not fuction properly.**



## Overview
MacPatch simplifies the act of patching and installing software on Mac OS X based systems. The client relies on using the built-in software update application for patching the Mac OS X system updates and it's own scan and patch engine for custom patches. 

MacPatch offers features and functionality that provide Mac OS X administrators with best possible patching solution to meet the challenges of supporting Mac OS X in a Workgroup or Enterprise.

## Features

* Custom patch creation
* Custom patch groups
* End-User Self Patch
* Software Distribution
* Inventory Collection
* Basic Reporting
* Mac OS X Profiles support
* AutoPKG support

## System Requirements

###Client
* Mac OS X Intel 32 & 64bit.  
* Mac OS X 10.8.0 and higher.

#####Server Requirements:
* Mac OS X or Mac OS X Server 10.10 or higher 
* Linux Fedora (19 and higher), RHEL 7, Ubuntu 12.x
* Using Intel Hardware, PPC is not supported
* 4 GB of RAM, 8 GB is recommended
* Python 2.7
* Java v1.8 or higher (Java 8 may not available in older distributions of Linux)
* MySQL version 5.1 or higher, MySQL 5.6.x is recommended.

####MySQL

While MySQL 5.6 is still the recommended database version. MySQL 5.7 has been out for some time now. MySQL changed the sql_mode settings in 5.7 which broke some queries in MacPatch. In order to use MacPatch with MySQL 5.7 the **sql_mode** setting will have to be changed.

To view and set the config use 
	
	SELECT @@GLOBAL.sql_mode;
	SET GLOBAL sql_mode = 'modes';

The default SQL mode in MySQL 5.7 includes these modes: 
	
	ONLY_FULL_GROUP_BY, STRICT_TRANS_TABLES, NO_ZERO_IN_DATE, NO_ZERO_DATE, ERROR_FOR_DIVISION_BY_ZERO, NO_AUTO_CREATE_USER, and NO_ENGINE_SUBSTITUTION.
	
The default SQL mode in MySQL 5.6 includes this mode: 

	NO_ENGINE_SUBSTITUTION

Preliminary testing has been successful when removing the **ONLY\_FULL\_GROUP\_BY** mode.


## Install and Setup
To get MacPatch up and running use the QuickStart docs from the macpatch.github.io website.

#### From Source
* Mac QuickStart: https://macpatch.llnl.gov/documentation/quickstart-osx.html
* Linux QuickStart: https://macpatch.llnl.gov/documentation/quickstart-linux.html

#### Binary
* Download the [MacPatch DMG](https://github.com/SMSG-MAC-DEV/MacPatch/releases/latest). Install PDF and client are located in the DMG.

## Help
For questions or help visit the [MacPatch](https://groups.google.com/d/forum/macpatch) group.

## License

MacPatch is available under the GNU GPLv2 license. See the [LICENSE](LICENSE "License") file for more info.
