# MacPatch 3.x - Install & Setup
-

### Description
This document will walk you through the install and setup of the MacPatch 3.x environment.  

### Prequisits & Requirements
root or sudo access will be needed to perform these tasks.

#### Requirements
- OS: 
	- **macOS**
		- Mac OS X 10.10 or higher		
	- **Linux**
		- RHEL 7.x or CentOS 7.x
- RAM: 4 Gig min
- MySQL 5.6.x (5.7.x is not supported)
- JAVA JDK 1.8.x

#### Prequisits
- Install MySQL 5.6.x (must have root password)
- If Installing on Mac OS X, Xcode and command line developer tools need to be installed and the license agreement needs to have been accepted.

#### Download, Setup and Install
- ##### Get Software
	- mkdir /opt (If Needed)
	- cd /opt
	- git clone https://github.com/SMSG-DEV/MacPatch

- ##### Setup Database
	- cd /opt/MacPatch/Server/conf/scripts/setup
	- MPDBSetup.sh (must be run on the MySQL server)

	**Note:** The MPDBSetup.sh ***can be/should be*** copied to another host if the database exists on a seperate server.
	
- ##### Install Software
	
	**Server Software**
	- cd /opt/MacPatch/scripts
	- sudo MPBuildServer.sh

- ##### Configure Server Software
	- cd /opt/MacPatch/Server/conf/scripts/setup
	- sudo Setup.py --setup

- ##### Setup Python virtual environment
	- cd /opt/MacPatch/Server/apps
	- source env/bin/activate
	- sudo python install.py
		- Note: If your behind a SSL content inspector add the custom ca using
		- export PIP_CERT=/path/to/ca/cert.crt
	- deactivate
	
- ##### Configure MacPatch schema & populate default data
	- cd /opt/MacPatch/Server/apps
	- source env/bin/activate
	- mpapi.py db upgrade head
	- mpapi.py populateDB
	- deactivate

#### Software & Patch Content

- Add Apple Software Update Content
	- scripts dir (/opt/MacPatch/Server/conf/scripts)
	- MPSUSPatchSync.py

- Use autopkg to add custom patch content



### Upload Client Software
-
