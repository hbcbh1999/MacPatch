#!/usr/bin/env python

'''
 Copyright (c) 2013, Lawrence Livermore National Security, LLC.
 Produced at the Lawrence Livermore National Laboratory (cf, DISCLAIMER).
 Written by Charles Heizer <heizer1 at llnl.gov>.
 LLNL-CODE-636469 All rights reserved.
 
 This file is part of MacPatch, a program for installing and patching
 software.
 
 MacPatch is free software; you can redistribute it and/or modify it under
 the terms of the GNU General Public License (as published by the Free
 Software Foundation) version 2, dated June 1991.
 
 MacPatch is distributed in the hope that it will be useful, but WITHOUT ANY
 WARRANTY; without even the IMPLIED WARRANTY OF MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE. See the terms and conditions of the GNU General Public
 License for more details.
 
 You should have received a copy of the GNU General Public License along
 with MacPatch; if not, write to the Free Software Foundation, Inc.,
 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
'''

'''
  MacPatch Patch Loader Setup Script
  MacPatch Version 3.0.x
  
  Script Version 2.0.3
'''

import os
import plistlib
import platform
import argparse
import pwd
import grp
import shutil
import json
import getpass
from distutils.version import LooseVersion
import ConfigParser
import sys
from sys import exit
from Crypto.PublicKey import RSA 

# ----------------------------------------------------------------------------
# Script Requires ROOT
# ----------------------------------------------------------------------------
if os.geteuid() != 0:
    exit("\nYou must be an admin user to run this script.\nPlease re-run the script using sudo.\n")

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------
MP_SRV_BASE	 = "/opt/MacPatch/Server"
MP_CONTENT	 = "/opt/MacPatch/Content"
MP_SRV_ETC	 = MP_SRV_BASE+"/etc"
MP_CONF_FILE = MP_SRV_BASE+"/etc/siteconfig.json"

if sys.platform.startswith('linux'):	
	dist_type 	 = platform.dist()[0]
else:
	dist_type 	 = "Mac"


MP_SRV_CONF 	= MP_SRV_BASE+"/conf"
MP_SRV_CONT 	= MP_SRV_BASE+"/Content/Web"
MP_INV_DIR		= MP_SRV_BASE+"/InvData"
MP_SRV_KEYS		= MP_SRV_ETC +"/keys"

os_type 		= platform.system()
system_name 	= platform.uname()[1]
gUID 			= 79
gGID 			= 70


if sys.platform.startswith('linux'):
	# OS is Linux, I need the dist type...
	try:
		pw = pwd.getpwnam('www-data')
		if pw:
			gUID = pw.pw_uid
			
		gw = grp.getgrnam('www-data')
		if gw:
			gGID = gw.gr_gid
			
	except KeyError:
		print('User www-data does not exist.')
		exit(1)

macServices=["gov.llnl.mp.tomcat.plist","gov.llnl.mp.invd.plist","gov.llnl.mp.py.api.plist",
"gov.llnl.mploader.plist","gov.llnl.mpavdl.plist","gov.llnl.mp.rsync.plist",
"gov.llnl.mp.sync.plist","gov.llnl.mp.pfctl.plist","gov.llnl.mp.fw.plist","gov.llnl.mp.nginx.plist"]

lnxServices=["MPTomcat","MPInventoryD","MPAPI","MPNginx"]
lnxCronSrvs=["MPPatchLoader","MPAVLoader"]

# ----------------------------------------------------------------------------
# Script Methods
# ----------------------------------------------------------------------------

def existsOrExit(filePath):
	if os.path.exists(filePath):
		return filePath
	else:
		print(filePath + ' does not exist. Now exiting.')
		exit(1)

def readJSON(filename):
	returndata = {}
	try:
		fd = open(filename, 'r+')
		returndata = json.load(fd)
		fd.close()
	except: 
		print 'COULD NOT LOAD:', filename

	return returndata

def writeJSON(data, filename):
	try:
		fd = open(filename, 'w')
		json.dump(data,fd, indent=4)
		fd.close()
	except:
		print 'ERROR writing', filename
		pass

def repairPermissions():
	try:
		if os_type == "Darwin":
			os.system("/usr/sbin/dseditgroup -o edit -a _appserver -t user _www")
			os.system("/usr/sbin/dseditgroup -o edit -a _www -t user _appserverusr")

		# Change Permissions for Linux & Mac		  
		for root, dirs, files in os.walk(MP_SRV_BASE):  
			for momo in dirs:  
				os.chown(os.path.join(root, momo), gUID, gGID)
			for momo in files:
				os.chown(os.path.join(root, momo), gUID, gGID)
	
		os.chmod("/opt/MacPatch", 0775)
		os.chmod(MP_SRV_BASE+"/logs", 0775)
		os.system("chmod -R 0775 "+ MP_CONTENT +"/Web")
		
		if os_type == "Darwin":
			os.system("chown root:wheel "+MP_SRV_BASE+"/conf/launchd/*")
			os.system("chmod 644 "+MP_SRV_BASE+"/conf/launchd/*")
	except Exception, e:
		print("Error: %s" % e)
				
def linuxLoadServices(service):

	_services = list()
	_servicesC = list()
	
	if service.lower() == "all":
		_services = lnxServices
		_servicesC = lnxCronSrvs
	else:
		if service in lnxServices:
			_services.append(service)
		elif service in lnxCronSrvs:
			_servicesC.append(service)

	# Load Init.d Services
	if _services != None:
		for srvs in _services:
			linuxLoadInitServices(srvs)
	
	# Load Cron Services
	if _servicesC != None:
		for srvs in _servicesC:
			linuxLoadCronServices(srvs)

def linuxUnLoadServices(service):

	_services = list()
	_servicesC = list()
	
	if service.lower() == "all":
		_services = lnxServices
		_servicesC = lnxCronSrvs
	else:
		if service in lnxServices:
			_services.append(service)
		elif service in lnxCronSrvs:
			_servicesC.append(service)

	# Load Init.d Services
	if _services != None:
		for srvs in _services:
			linuxUnLoadInitServices(srvs)
	
	# Load Cron Services
	if _servicesC != None:
		for srvs in _servicesC:
			removeCronJob(srvs)

def linuxLoadInitServices(service):
	
	print "Loading service "+service

	useSYSTEMD=False
	if platform.dist()[0] == "Ubuntu" and LooseVersion(platform.dist()[1]) >= LooseVersion("15.0"):
		useSYSTEMD=True
	elif (platform.dist()[0] == "redhat" or platform.dist()[0] == "centos") and LooseVersion(platform.dist()[1]) >= LooseVersion("7.0"):
		useSYSTEMD=True
	else:
		print "Unable to start service ("+service+") at start up. OS("+platform.dist()[0]+") is unsupported."	
		return

	if useSYSTEMD == True:
		serviceName=service+".service"
		etcServiceConf="/etc/systemd/system/"+serviceName

		if os.path.exists(etcServiceConf):
			os.system("/bin/systemctl start "+serviceName)
		else:
			print "Unable to find " + etcServiceConf
	else:
		_initFile = "/etc/init.d/"+service
		if os.path.exists(_initFile):
			os.system("/etc/init.d/"+service+" start")
		else:
			print "Unable to find " + _initFile

def linuxUnLoadInitServices(service):
	# UnLoad Init Services
	print "UnLoading service "+service
	useSYSTEMD=False
	if platform.dist()[0] == "Ubuntu" and LooseVersion(platform.dist()[1]) >= LooseVersion("15.0"):
		useSYSTEMD=True
	elif (platform.dist()[0] == "redhat" or platform.dist()[0] == "centos") and LooseVersion(platform.dist()[1]) >= LooseVersion("7.0"):
		useSYSTEMD=True
	else:
		print "Unable to start service ("+service+") at start up. OS("+platform.dist()[0]+") is unsupported."	
		return

	if useSYSTEMD == True:
		serviceName=service+".service"
		etcServiceConf="/etc/systemd/system/"+serviceName

		if os.path.exists(etcServiceConf):
			os.system("/bin/systemctl stop "+serviceName)
		else:
			print "Unable to find " + etcServiceConf
	else:
		_initFile = "/etc/init.d/"+service
		if os.path.exists(_initFile):
			os.system("/etc/init.d/"+service+" stop")
		else:
			print "Unable to find " + _initFile

def linuxLoadCronServices(service):
	from crontab import CronTab
	cron = CronTab()
	
	if service == "MPPatchLoader":
		print("Loading MPPatchLoader")

		cmd = MP_SRV_CONF + '/scripts/MPSUSPatchSync.py --config ' + MP_SRV_BASE + '/etc/patchloader.json'
		job  = cron.new(command=cmd)
		job.set_comment("MPPatchLoader")
		job.hour.every(8)
		job.enable()
		cron.write_to_user(user='root')
	
	if service == "MPAVLoader":
		print("Loading MPAVLoader")

		cmd = MP_SRV_CONF + '/scripts/MPAVDefsSync.py --config ' + MP_SRV_BASE + '/etc/avconf.json'
		job  = cron.new(command=cmd)
		job.set_comment("MPAVLoader")
		job.hour.every(11)
		job.enable()
		cron.write_to_user(user='root')

def removeCronJob(comment):
	from crontab import CronTab
	cron = CronTab()

	for job in cron:
		if job.comment == comment:
			print "Removing Cron Job" + comment
			cJobRm = raw_input('Are you sure you want to remove this cron job (Y/N)?')
			if cJobRm.lower() == "y" or cJobRm.lower() == "yes":
				cron.remove (job)

def osxLoadServices(service):
	_services = list()
	
	if service.lower() == "all":
		_services = macServices
	else:
		if service in macServices:
			_services.append(service)
		else:
			print service + " was not found. Service will not load."
			return
			
	for srvc in _services:
		# Set Permissions
		os.chown(MP_SRV_BASE+"/conf/launchd/"+srvc, 0, 0)
		os.chmod(MP_SRV_BASE+"/conf/launchd/"+srvc, 0644)
		
		_launchdFile = "/Library/LaunchDaemons/"+srvc
		if os.path.exists(_launchdFile):
			print "Loading service "+srvc
			os.system("/bin/launchctl load -w /Library/LaunchDaemons/"+srvc)
		else:
			if os.path.exists(MP_SRV_BASE+"/conf/launchd/"+srvc):
				if os.path.exists("/Library/LaunchDaemons/"+srvc):
					os.remove("/Library/LaunchDaemons/"+srvc)
			
				os.symlink(MP_SRV_BASE+"/conf/launchd/"+srvc,"/Library/LaunchDaemons/"+srvc)
				
				print "Loading service "+srvc
				os.system("/bin/launchctl load -w /Library/LaunchDaemons/"+srvc)
				
			else:
				print srvc + " was not found in MacPatch Server directory. Service will not load."
						
def osxUnLoadServices(service):

	_services = []
	if service.lower() == "all":
		_services = macServices
	else:
		if service in macServices:
			_services = service
			
	for srvc in _services:
		_launchdFile = "/Library/LaunchDaemons/"+srvc
		if os.path.exists(_launchdFile):
			print "UnLoading service "+srvc
			os.system("/bin/launchctl unload -wF /Library/LaunchDaemons/"+srvc)

def setupRsyncFromMaster():
	os.system('clear')
	print("\nConfigure this server to syncronize data from the \"Master\" MacPatch server.\n")
	server_name = raw_input("MacPatch Server \"hostname\" or \"IP Address\" TO sync data from: ")

	'''	Write the Plist With Changes '''
	theFile = MP_SRV_BASE + "/etc/gov.llnl.mp.sync.plist"
	if os.path.exists(theFile):
		prefs = plistlib.readPlist(theFile)
	else:
		prefs = {}

	prefs['MPServerAddress'] = server_name

	try:
		plistlib.writePlist(prefs,theFile)	
	except Exception, e:
		print("Error: %s" % e)	

	''' Enable Startup Scripts '''
	if os_type == "Darwin":
		if os.path.exists(MP_SRV_BASE+"/conf/launchd/gov.llnl.mp.sync.plist"):
			if os.path.exists("/Library/LaunchDaemons/gov.llnl.mp.sync.plist"):
				os.remove("/Library/LaunchDaemons/gov.llnl.mp.sync.plist")
			
			os.symlink(MP_SRV_BASE+"/conf/launchd/gov.llnl.mp.sync.plist","/Library/LaunchDaemons/gov.llnl.mp.sync.plist")
			os.chown(MP_SRV_BASE+"/conf/launchd/gov.llnl.mp.sync.plist", 0, 0)
			os.chmod(MP_SRV_BASE+"/conf/launchd/gov.llnl.mp.sync.plist", 0644)

	if os_type == "Linux":
		from crontab import CronTab
		cron = CronTab()
		cron_cmd = MP_SRV_BASE+"/conf/scripts/MPSyncContent.py --plist "+MP_SRV_BASE+"/etc/gov.llnl.mp.sync.plist"
		job  = cron.new(command=cron_cmd)
		job.set_comment("MPSyncContent")
		job.every(15).minute()	
		cron.write()

def setupPatchLoader():

	'''	Write the Plist With Changes '''
	prefs = dict()
	theFile = MP_SRV_BASE + "/etc/patchloader.json"
	if os.path.exists(theFile):
		prefs=readJSON(theFile)

	_srvHost = "127.0.0.1"
	_srvPort = "3600"
	_srvUSSL = "Y"
	
	srvHost = raw_input('Master server address [127.0.0.1]: ')
	srvHost = srvHost or _srvHost

	srvPort = raw_input('Master server port [3600]: ')
	srvPort = srvPort or _srvPort
	srvUSSL = raw_input('Master server, use SSL [Y]: ')
	if srvUSSL.lower() == "y" or srvUSSL.lower() == "":
		srvUSSLBOOL = True
	elif srvUSSL.lower() == "n":
		srvUSSLBOOL = False	

	prefs['settings']['MPServerAddress'] = srvHost
	prefs['settings']['MPServerUseSSL'] = srvUSSLBOOL
	prefs['settings']['MPServerPort'] = str(srvPort)

	try:
		writeJSON(prefs, theFile)
	except Exception, e:
		print("Error: %s" % e)

	''' Enable Startup Scripts '''
	if os_type == "Darwin":
		if os.path.exists(MP_SRV_BASE+"/conf/launchd/gov.llnl.mploader.plist"):
			if os.path.exists("/Library/LaunchDaemons/gov.llnl.mploader.plist"):
				os.remove("/Library/LaunchDaemons/gov.llnl.mploader.plist")
			
			os.symlink(MP_SRV_BASE+"/conf/launchd/gov.llnl.mploader.plist","/Library/LaunchDaemons/gov.llnl.mploader.plist")
			os.chown(MP_SRV_BASE+"/conf/launchd/gov.llnl.mploader.plist", 0, 0)
			os.chmod(MP_SRV_BASE+"/conf/launchd/gov.llnl.mploader.plist", 0644)
	else:
		linuxLoadCronServices('MPPatchLoader')

def setupServices():

	srvsList = []
	print "You will be asked which services you would like to load"
	print "on system startup."
	print ""

	# Master or Distribution
	masterType = True
	srvType = raw_input('Is this a Master or Distribution server [M/D]?')
	if srvType.lower() == "m" or srvType.lower() == "master":
		masterType = True
	elif srvType.lower() == "d" or srvType.lower() == "distribution":
		masterType = False

	# Web Services
	_WEBSERVICES = 'Y' 
	webService = raw_input('Enable Web Services [%s]' % _WEBSERVICES)
	webService = webService or _WEBSERVICES
	jData = readJSON(MP_CONF_FILE)
	if webService.lower() == 'y':

		jData['settings']['services']['mpwsl'] = True
		jData['settings']['services']['mpapi'] = True

		if os_type == 'Darwin':
			if 'gov.llnl.mp.py.api.plist' not in srvsList:
				srvsList.append('gov.llnl.mp.py.api.plist')
			if 'gov.llnl.mp.invd.plist' not in srvsList:
				srvsList.append('gov.llnl.mp.invd.plist')
			if 'gov.llnl.mp.nginx.plist' not in srvsList:
				srvsList.append('gov.llnl.mp.nginx.plist')
		else:
			linkStartupScripts('MPInventoryD')
			srvsList.append('MPInventoryD')
			linkStartupScripts('MPNginx')
			srvsList.append('MPNginx')
			linkStartupScripts('MPAPI')
			srvsList.append('MPAPI')
	else:
		jData['settings']['services']['mpwsl'] = False
		jData['settings']['services']['mpapi'] = False

	writeJSON(jData,MP_CONF_FILE)
	
	# Web Admin Console
	
	_ADMINCONSOLE = 'Y' if masterType else 'N'  
	adminConsole = raw_input('Enable Admin Console Application [%s]' % _ADMINCONSOLE)
	adminConsole = adminConsole or _ADMINCONSOLE
	jData = readJSON(MP_CONF_FILE)
	if adminConsole.lower() == 'y':

		jData['settings']['services']['console'] = True

		if os_type == 'Darwin':
			if 'gov.llnl.mp.tomcat.plist' not in srvsList:
				srvsList.append('gov.llnl.mp.tomcat.plist')
			if 'gov.llnl.mp.nginx.plist' not in srvsList:
				srvsList.append('gov.llnl.mp.nginx.plist')
		else:
			linkStartupScripts('MPNginx')
			srvsList.append('MPNginx')
			linkStartupScripts('MPTomcat')
			srvsList.append('MPTomcat')

	else:
		
		jData['settings']['services']['console'] = False

	writeJSON(jData,MP_CONF_FILE)

	# Content Sync
	_CONTENT = 'Y' if masterType else 'N'  
	print "Content sync allows distribution servers to sync from the master server."
	cRsync = raw_input('Start Content Sync Service (Master Only) [%s]' % _CONTENT)
	cRsync = cRsync or _CONTENT
	if cRsync.lower() == 'y':
		srvsList.append('gov.llnl.mp.rsync.plist')

	# Patch Loader
	_PATCHLOAD = 'Y' if masterType else 'N'
	patchLoader = raw_input('ASUS Patch Content Loader [%s]' % _PATCHLOAD)
	patchLoader = patchLoader or _PATCHLOAD
	if patchLoader.lower() == 'y':
		setupPatchLoader()
		if os_type == 'Darwin':
			srvsList.append('gov.llnl.mploader.plist')
	
	# Sync From Master
	if masterType == False:
		_RSYNC = 'Y'
		mpRsync = raw_input('Sync Content from Master server (Recommended) [%s]' % _RSYNC)
		mpRsync = mpRsync or _RSYNC
		if mpRsync.lower() == 'y':
			setupRsyncFromMaster()
			if os_type == 'Darwin':
				srvsList.append('gov.llnl.mp.sync.plist')

	# Firewall Config / Port Forwarding
	if os_type == 'Darwin':
		_PFLOAD = 'Y'
		print "MacPatch Tomcat Runs on several tcp ports (8080,8443,2600)"
		print "Port forwading forwards the following ports"
		print "80 -> 8080"
		print "443 -> 8443"
		pfConf = raw_input('Enable port forwading (Recommended) [%s]' % _PFLOAD)
		pfConf = pfConf or _PFLOAD
		if pfConf.lower() == 'y':
			if platform.mac_ver()[0] >= "10.10.0":
				srvsList.append('gov.llnl.mp.pfctl.plist')
			else:
				srvsList.append('gov.llnl.mp.fw.plist')


	return set(srvsList)

def linkStartupScripts(service):
	
	print "Copy Startup Script for "+service
	useSYSTEMD=False

	if platform.dist()[0] == "Ubuntu" and LooseVersion(platform.dist()[1]) >= LooseVersion("15.0"):
		useSYSTEMD=True
	elif (platform.dist()[0] == "redhat" or platform.dist()[0] == "centos") and LooseVersion(platform.dist()[1]) >= LooseVersion("7.0"):
		useSYSTEMD=True
	else:
		print "Unable to start service ("+service+") at start up. OS("+platform.dist()[0]+") is unsupported."	
		return

	if useSYSTEMD == True:
		serviceName=service+".service"
		serviceConf=MP_SRV_BASE+"/conf/systemd/"+serviceName
		etcServiceConf="/etc/systemd/system/"+serviceName
		shutil.copy2(serviceConf, etcServiceConf)

		os.system("/bin/systemctl enable "+serviceName)

	else:
		_initFile = "/etc/init.d/"+service
		if os.path.exists(_initFile):
			return
		else:
			script = MP_SRV_BASE+"/conf/init.d/Ubuntu/"+service
			link = "/etc/init.d/"+service 

			os.chown(script, 0, 0)
			os.chmod(script, 0755)
			os.symlink(script,link)

		os.system("update-rc.d "+service+" defaults")

# ----------------------------------------------------------------------------
# DB Config Class
# ----------------------------------------------------------------------------

class MPDatabase:

	config_file = MP_SRV_BASE+"/etc/siteconfig.json" 
	ws_alt_conf = MP_SRV_BASE+"/apps/config.cfg"

	def __init__(self):
		
		if sys.platform.startswith('linux'):
			MPDatabase.config_file = MP_SRV_BASE+"/etc/siteconfig.json" 
			MPDatabase.ws_alt_conf = MP_SRV_BASE+"/apps/config.cfg"

	def loadConfig(self):
		config = {}
		try:
			fd = open(MPDatabase.config_file, 'r+')
			config = json.load(fd)
			fd.close()
		except: 
			print 'COULD NOT LOAD:', filename
			exit(1)

		return config

	def writeConfig(self, config):
		print "Writing configuration data to file ..."
		with open(MPDatabase.config_file, "w") as outfile:
			json.dump(config, outfile, indent=4)

	def writeFlaskConfig(self, key, value):
		keyVal = "%s=\"%s\"\n" % (key,value)
		f = open(MPDatabase.ws_alt_conf,'a')
		f.write(keyVal)
		f.close()


	def configDatabase(self):
		conf = self.loadConfig()
		system_name = platform.uname()[1]

		os.system('clear')
		print "Configure MacPatch Database Info..."
		mp_db_hostname = raw_input("MacPatch Database Server Hostname:  [" + str(system_name) + "]: ") or str(system_name)

		conf["settings"]["database"]["prod"]["dbHost"] = mp_db_hostname
		conf["settings"]["database"]["ro"]["dbHost"] = mp_db_hostname

		mp_db_port = raw_input("MacPatch Database Server Port Number [3306]: ") or "3306"
		conf["settings"]["database"]["prod"]["dbPort"] = mp_db_port
		conf["settings"]["database"]["ro"]["dbPort"] = mp_db_port
		
		mp_db_name = raw_input("MacPatch Database Name [MacPatchDB]: ") or "MacPatchDB"
		conf["settings"]["database"]["prod"]["dbName"] = mp_db_name
		conf["settings"]["database"]["ro"]["dbName"] = mp_db_name
		
		mp_db_usr = raw_input("MacPatch Database User Name [mpdbadm]: ") or "mpdbadm"
		conf["settings"]["database"]["prod"]["username"] = mp_db_usr
		
		mp_db_pas = getpass.getpass('MacPatch Database User Password:')
		conf["settings"]["database"]["prod"]["password"] = mp_db_pas
		
		mp_db_pas_ro = getpass.getpass('MacPatch Database Read Only User Password:')
		conf["settings"]["database"]["ro"]["password"] = mp_db_pas_ro

		save_answer = raw_input("Would you like the save these settings [Y]?:").upper() or "Y"
		if save_answer == "Y":
			self.writeConfig(conf)
			self.writeFlaskConfig('DB_HOST',mp_db_hostname)
			self.writeFlaskConfig('DB_PORT',mp_db_port)
			self.writeFlaskConfig('DB_NAME',mp_db_name)
			self.writeFlaskConfig('DB_USER',mp_db_usr)
			self.writeFlaskConfig('DB_PASS',mp_db_pas)
		else:
			return configDatabase()

# ----------------------------------------------------------------------------
# LDAP Config Class
# ----------------------------------------------------------------------------

class MPLdap:

	config_file = MP_SRV_BASE+"/etc/siteconfig.json" 

	def __init__(self):
		
		if sys.platform.startswith('linux'):
			MPLdap.config_file = MP_SRV_BASE+"/etc/siteconfig.json" 

	def loadConfig(self):
		config = {}
		try:
			fd = open(MPLdap.config_file, 'r+')
			config = json.load(fd)
			fd.close()
		except: 
			print 'COULD NOT LOAD:', filename
			exit(1)

		return config

	def writeConfig(self, config):
		print "Writing configuration data to file ..."
		with open(MPLdap.config_file, "w") as outfile:
			json.dump(config, outfile, indent=4)

	def configLdap(self):
		conf = self.loadConfig()

		os.system('clear')
		print "Configure MacPatch Login Source..."
		use_ldap = raw_input("Would you like to use Active Directory/LDAP for login? [Y]:").upper() or "Y"

		if use_ldap == "Y":
			ldap_hostname = raw_input("Active Directory/LDAP server hostname: ")
			conf["settings"]["ldap"]["server"] = ldap_hostname

			print "Common ports for LDAP non secure is 389, secure is 636."
			print "Common ports for Active Directory non secure is 3268, secure is 3269"
			ldap_port = raw_input("Active Directory/LDAP server port number: ")
			conf["settings"]["ldap"]["port"] = ldap_port
			
			use_ldap_ssl = raw_input("Active Directory/LDAP use ssl? [Y]: ").upper() or "Y"
			if use_ldap_ssl == "Y":
				print "Please note, you will need to run the addRemoteCert.py script prior to starting the MacPatch Web Admin Console."
				ldap_ssl = "CFSSL_BASIC"
				conf["settings"]["ldap"]["secure"] = ldap_ssl
			else:
				ldap_ssl = "NONE"
				conf["settings"]["ldap"]["secure"] = ldap_ssl

			ldap_searchbase = raw_input("Active Directory/LDAP Search Base: ")
			conf["settings"]["ldap"]["searchbase"] = ldap_searchbase
			
			ldap_lgnattr = raw_input("Active Directory/LDAP Login Attribute [userPrincipalName]: ") or "userPrincipalName"
			conf["settings"]["ldap"]["loginAttr"] = ldap_lgnattr

			ldap_lgnpre = raw_input("Active Directory/LDAP Login User Name Prefix [None]: ") or ""
			conf["settings"]["ldap"]["loginUsrPrefix"] = ldap_lgnpre

			ldap_lgnsuf = raw_input("Active Directory/LDAP Login User Name Suffix [None]: ") or ""
			conf["settings"]["ldap"]["loginUsrSufix"] = ldap_lgnsuf

			save_answer = raw_input("Would you like the save these settings [Y]?:").upper() or "Y"
			if save_answer == "Y":
				self.writeConfig(conf)
			else:
				return configLdap()

		else:
			conf["settings"]["ldap"]["enabled"] = "NO"
			self.writeConfig(conf)

# ----------------------------------------------------------------------------
# MPAdmin Config Class
# ----------------------------------------------------------------------------

class MPAdmin:

	def __init__(self):
		self.mp_adm_name = "mpadmin"
		self.mp_adm_pass = "*mpadmin*"
		MPAdmin.config_file = MP_CONF_FILE
			

	def loadConfig(self):
		config = {}
		try:
			fd = open(MPAdmin.config_file, 'r+')
			config = json.load(fd)
			fd.close()
		except: 
			print 'COULD NOT LOAD:', filename
			exit(1)

		return config

	def writeConfig(self, config):
		print "Writing configuration data to file ..."
		with open(MPAdmin.config_file, "w") as outfile:
			json.dump(config, outfile, indent=4)

	def configAdminUser(self):
		conf = self.loadConfig()

		os.system('clear')
		print "Set Default Admin name and password..."    

		set_admin_info = raw_input("Would you like to set the admin name and password [Y]:").upper() or "Y"
		if set_admin_info == "Y":
			mp_adm_name = raw_input("MacPatch Default Admin Account Name [mpadmin]: ") or "mpadmin"
			conf["settings"]["users"]["admin"]["name"] = mp_adm_name
			mp_adm_pass = getpass.getpass("MacPatch MacPatch Default Admin Account Password:")
			conf["settings"]["users"]["admin"]["pass"] = mp_adm_pass

		save_answer = raw_input("Would you like the save these settings [Y]?:").upper() or "Y"
		if save_answer == "Y":
			self.writeConfig(conf)
		else:
<<<<<<< HEAD
			return self.configAdminUser()
=======
			return configAdminUser(self)
>>>>>>> 724d0ad14de4920afa8ef656ca22edc32d1bd7a4

# ----------------------------------------------------------------------------
# MP Set Default Config Data
# ----------------------------------------------------------------------------

class MPConfigDefaults:

	def __init__(self):
		MPConfigDefaults.config_file = MP_CONF_FILE

	def loadConfig(self):
		config = {}
		try:
			fd = open(MPConfigDefaults.config_file, 'r+')
			config = json.load(fd)
			fd.close()
		except: 
			print 'COULD NOT LOAD:', MPConfigDefaults.config_file
			exit(1)

		return config

	def genServerKeys(self):
		new_key = RSA.generate(4096, e=65537) 
		public_key = new_key.publickey().exportKey("PEM") 
		private_key = new_key.exportKey("PEM") 
		return private_key, public_key

	def writeConfig(self, config):
		print "Writing configuration data to file ..."
		with open(MPConfigDefaults.config_file, "w") as outfile:
			json.dump(config, outfile, indent=4)

	def genConfigDefaults(self):
		conf = self.loadConfig()

		# Paths
		conf["settings"]["paths"]["base"] = MP_SRV_BASE
		conf["settings"]["paths"]["content"] = MP_SRV_CONT

		# Inventory
		conf["settings"]["server"]["inventory_dir"] = MP_INV_DIR

		# Server Keys
		if not os.path.exists(MP_SRV_KEYS):
			os.makedirs(MP_SRV_KEYS)
		
		pub_key = MP_SRV_KEYS + "/server_pub.pem"
		pri_key = MP_SRV_KEYS + "/server_pri.pem"
		if not os.path.exists(pub_key) and not os.path.exists(pri_key):
			if conf["settings"]["server"]["autoGenServerKeys"]:
				rsaKeys = self.genServerKeys()
				with open(pri_key, 'w') as the_pri_file:
					the_pri_file.write(rsaKeys[0])
				with open(pub_key, 'w') as the_pub_file:
					the_pub_file.write(rsaKeys[1])
				conf["settings"]["server"]["priKey"] = pri_key
				conf["settings"]["server"]["pubKey"] = pub_key
		else:
			print "Server RSA Keys already exist."
		
		print "Write MPConfigDefaults"
		print conf["settings"]["server"]
 		self.writeConfig(conf)			

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
	'''Main command processing'''

	parser = argparse.ArgumentParser(description='Process some args.')
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--setup', help="Setup Services", required=False, action='store_true')
	group.add_argument('--load', help="Load/Start Services", required=False)
	group.add_argument('--cron', help="Load/Start Cron Services", required=False)
	group.add_argument('--unload', help='Unload/Stop Services', required=False)
	args = parser.parse_args()

	# First Repair permissions
	# repairPermissions()

	if args.setup != False:
		srvconf = MPConfigDefaults()
		srvconf.genConfigDefaults()

		adm = MPAdmin()
		adm.configAdminUser()

		db = MPDatabase()
		db.configDatabase()

		ldap = MPLdap()
		ldap.configLdap()

		os.system('clear')
		srvList = setupServices()

	if os_type == 'Darwin':
		if args.setup != False:
			for srvc in srvList:
				osxLoadServices(srvc)
		elif args.load != None:
			osxLoadServices(args.load)
		elif args.unload != None:
			osxUnLoadServices(args.unload)

	elif os_type == 'Linux':
		if args.setup != False:
			for srvc in srvList:
				linuxLoadServices(srvc)

		if args.cron != None:
			linuxLoadCronServices(args.cron)

		if args.load != None:
			linuxLoadServices(args.load)
		elif args.unload != None:
			linuxUnLoadServices(args.unload)

def usage():
	print "Setup.py --setup or --load/--unload [All - Service]\n"
	print "\t--setup\t\tSetup all services to start on boot and any configuration needed. Will load selected services."
	print "\t--load\t\tLoads a Service or All services with the key word 'All'"
	print "\t--unload\tUn-Loads a Service or All services with the key word 'All'\n"


if __name__ == '__main__':
	main()
	