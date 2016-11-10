# MacPatch 3.0.0 - Install & Setup
-

### Description
This document will walk you through the install and setup of the MacPatch 3.x environment.  

### Table of Contents
* [Required Software](#a1)
* [Prequisits](#a2) 
* [Download, Setup and Install](#a3)
	* [Get Software] (#a3a)
	* [Setup Database] (#a3b)
	* [Install Server Software] (#a3c)
	* [Configure Server Software] (#a3d)
	* [Load and Populate Database] (#a3f)
* [Server Setup & Configuration](#a4)
	* [First Login] (#a4a)
	* [Server Configuration] (#a4b)
	* [Default Patch Group Configuration] (#a4c)
	* [Client Agent Configuration] (#a4d)
* [Download and Add Patch Content](#a5)
	* [Apple Patches](#a5a)
	* [Custom Patches](#a5b)
* [Upload Client Software](#a6)

### Prequisits & Requirements
root or sudo access will be needed to perform these tasks.

#### Requirements <a name='a1'></a>
- Operating System:
	- macOS
		- Mac OS X 10.10 or higher
	- Linux
		- RHEL 7.x or CentOS 7.x
		- Ubuntu Server 16.04
- RAM: 4 Gig min
- MySQL 5.6.x (5.7.x is not supported)
- JAVA JDK 1.8.x

#### Prequisits <a name='a2'></a>
- Install MySQL 5.6.x (must have root password)
- If Installing on Mac OS X, Xcode and command line developer tools need to be installed **AND** the license agreement needs to have been accepted.

### Download, Setup and Install <a name='a3'></a>

##### Get Software <a name='a3a'></a>
		mkdir /opt (If Needed)
		cd /opt
		git clone https://github.com/SMSG-DEV/MacPatch

##### Setup Database <a name='a3b'></a>

The database setup script only creates the MacPatch database and the 2 database accounts needed to use the database. Tuning the MySQL server is out of scope for this document. 

Please remeber the passwords for mpdbadm and mpdbro accounts while running this script. They will be required during the SetupServer.py script database section.

		cd /opt/MacPatch/Server/conf/scripts/setup
		MPDBSetup.sh (must be run on the MySQL server)

**Note:** The MPDBSetup.sh ***can be/should be*** copied to another host if the database exists on a seperate server.
	
##### Install Software <a name='a3c'></a>
	
		cd /opt/MacPatch/scripts
		sudo MPBuildServer.sh	
		
**Note:** If your behind a SSL content inspector add the custom ca using
		
		export PIP_CERT=/path/to/ca/cert.crt

##### Configure Server Software <a name='a3d'></a>
	
		cd /opt/MacPatch/Server/conf/scripts/setup
		sudo ServerSetup.py --setup
	
##### Configure MacPatch schema & populate default data <a name='a3f'></a>
		
		cd /opt/MacPatch/Server/apps
		source env/bin/activate
		mpapi.py db upgrade head
		mpapi.py populateDB
		deactivate

##### Start Services
		
		cd /opt/MacPatch/Server/conf/scripts/setup
		sudo ServerSetup.py --load All

--

### Server Setup & Configuration <a name='a4'></a>

The MacPatch server software has now been installed and should be up and running. The server is almost ready for accepting clients. There are a few more server configuration settings which need to be configured.

##### First Login <a name='a4a'></a>
The default user name is “mpadmin” and the password is “*mpadmin*”, Unless it was changed using the “ServerSetup.py” script. You will need to login for the first time with this account to do all of the setup tasks. Once these tasks are completed it’s recommended that this accounts password be changed. This can be done by editing the siteconfig.json file, which is located in /opt/MacPatch/Server/etc/.

##### Server Configuration <a name='a4b'></a>
Each MacPatch server needs to be added to the environment. The master server is always added automatically.

It is recommended that you login and verify the master server settings. It is common during install that the master server address will be added as localhost or 127.0.0.1. Please make sure that the correct hostname or IP address is set and that **"active"** is enabled.

* Go to “Admin -> Server -> MacPatch Servers”
* Double Click the row with your server or single click the row and click the “Pencil” button.

##### Default Patch Group Configuration <a name='a4c'></a>
A default patch group will be created during install. The name of the default patch group is “Default”. You may use it or create a new one.

To edit the contents for the patch group simply click the “Pencil” icon next to the group name. To add patches click the check boxes to add or subtract patches from the group. When done click the “Save” icon. (Important Step)

* Go to “Patches -> Patch Groups”
* Double Click the row with your server or single click the row and click the “Pencil” button.

##### Client Agent Configuration <a name='a4d'></a>

A default agent configuration is added during the install. Please verify the client agent configuration before the client agent is uploaded.

**Recommended**

* Go to “Admin -> Client Agents -> Configure”
* Set the following 3 properties to be enforced
	* MPServerAddress
	* MPServerPort
	* MPServerSSL
* Verify the “PatchGroup” setting. If you have changed it set it before you upload the client agent.
* Click the save button
* Click the icon in the “Default” column for the default configuration. (Important Step)

Only the default agent configuration will get added to the client agent upon upload.


--

### Download & Add Patch Content <a name='a5'></a>

**Apple Updates** <a name='a5a'></a>

Apple patch content will download eventually on it’s own cycle, but for the first time it’s recommended to download it manually.

The Apple Software Update content settings are stored in a json file (/opt/MacPatch/Server/etc/patchloader.json). By default, Apple patches for 10.9 through 10.12 will be processed and supported.

Run the following command via the Terminal.app on the Master MacPatch server.

`sudo -u www-data /opt/MacPatch/Server/conf/scripts/MPSUSPatchSync.py --config /opt/MacPatch/Server/etc/patchloader.plist`

**Custom Updates** <a name='a5b'></a>

To create your own custom patch content please read the "Custom Patch Content" [docs](https://macpatch.github.io/doc/custom-patch-content.html).

To use "AutoPkg" to add patch content please read the "AutoPkg patch content" [docs](https://macpatch.github.io/doc/autopkg-patch-content.html).	

--

### Upload Client Software <a name='a6'></a>

To upload a client agent you will need to build the client first. Please follow the Building the Client document before continuing.

* Go to “Admin-> Client Agents -> Deploy”
* Download the “MacPatch Agent Uploader”
* Double Click the “Agent Uploader.app”
	* Enter the MacPatch Server
	* Choose the agent package (e.g. MPClientInstall.pkg.zip)
	* Click “Upload” button
