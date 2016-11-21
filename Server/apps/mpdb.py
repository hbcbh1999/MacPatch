import uuid
import md5
from datetime import datetime
from mpapi import db
from mpapi.mputil import return_data_for_root_key
from mpapi.model import MpClientsRegistrationSettings
from mpapi.model import AgentConfig, AgentConfigData
from mpapi.model import MpPatchGroup, PatchGroupMembers
from mpapi.model import MpAsusCatalogList
from mpapi.model import MpServer, MpServerList
from mpapi.model import MpSoftwareGroup, MpSoftwareGroupPrivs

def addDefaultData():
	addRegConfig()
	addClientConfig()
	addDefaultPatchGroup()
	addDefaultSWGroup()
	addDefaultSUSGroup()
	addDefaultServerConfig()
	addDefaultServerList()

# Agent Registration Settings ------------------------------------------------
def hasRegConfig():
	res = MpClientsRegistrationSettings.query.all()
	if res is not None:
		return True
	else:
		return False

def addRegConfig():
	# Check for config
	if hasRegConfig():
		return False

	# Add Agent Config
	db.session.add(MpClientsRegistrationSettings(autoreg="0", autoreg_key="999999999", client_parking="0"))
	db.session.commit()

# Agent Config ---------------------------------------------------------------
def hasClientConfig():
	res = AgentConfig.query.filter(AgentConfig.isDefault==1).first()
	if res is not None:
		return True
	else:
		return False

def addClientConfig():
	# Check for config
	if hasClientConfig():
		return False

	agentConf = { "AllowClient": "1", "AllowServer": "0", "Description": "Defautl Agent Config",
					"Domain": "Default", "PatchGroup": "Default", "Reboot": "1", "SWDistGroup": "Default",
					"MPProxyServerAddress": "AUTOFILL", "MPProxyServerPort": "2600", "MPProxyEnabled": "0",
					"MPServerAddress": "AUTOFILL", "MPServerPort": "2600", "MPServerSSL": "1",
					"CheckSignatures": "0", "MPServerAllowSelfSigned": "0"
				}

	# Create UUID
	_uuid = str(uuid.uuid4())
	# Add Agent Config
	db.session.add(AgentConfig(aid=_uuid, name="Default", isDefault="1", revision="0"))
	db.session.commit()

	# Add Agent Config Data
	for key in agentConf.keys():
		db.session.add(AgentConfigData(aid=_uuid, akey=key, akeyValue=agentConf[key], enforced="0"))
		db.session.commit()

	# Get & Set Revision Hash
	revHash = getRevisonForConfig(_uuid)
	if revHash != "NA":
		_hash = AgentConfig.query.filter(AgentConfig.aid == _uuid).first()
		_hash.revision = revHash
		db.session.commit()

def getRevisonForConfig(configID):

	res = AgentConfigData.query.filter(AgentConfigData.aid == configID).all()
	if res is not None:
		reslst = []
		for i in res:
			reslst.append(i.akeyValue.lower())

		reslststr = "".join(reslst)
		configHash = md5.md5(reslststr).hexdigest()

		return configHash
	else:
		return "NA"

# Patch Group ----------------------------------------------------------------
def hasDefaultPatchGroup():
	res = MpPatchGroup.query.filter(MpPatchGroup.name=='Default').first()
	if res is not None:
		return True
	else:
		return False

def addDefaultPatchGroup():
	# Check for config
	if hasDefaultPatchGroup():
		return False

	adm_dict = return_data_for_root_key('users')
	adm_user = adm_dict['admin']['name']

	# Create UUID
	_uuid = str(uuid.uuid4())

	# Add Agent Config
	db.session.add(MpPatchGroup(name="Default", id=_uuid, type="0"))
	db.session.commit()

	# Add Agent Config
	db.session.add(PatchGroupMembers(user_id=adm_user, patch_group_id=_uuid, is_owner="1"))
	db.session.commit()

# SW Dist Group --------------------------------------------------------------
def hasDefaultSWGroup():
	res = MpSoftwareGroup.query.filter(MpSoftwareGroup.gName=='Default').first()
	if res is not None:
		return True
	else:
		return False

def addDefaultSWGroup():
	# Check for config
	if hasDefaultSWGroup():
		return False

	adm_dict = return_data_for_root_key('users')
	adm_user = adm_dict['admin']['name']

	# Create UUID
	_uuid = str(uuid.uuid4())

	# Add Agent Config
	dts = datetime.now()
	db.session.add(MpSoftwareGroupPrivs(gid=_uuid, uid=adm_user, isowner='1'))
	db.session.commit()
	db.session.add(MpSoftwareGroup(gid=_uuid, gName="Default", gDescription="Default", gType="0", gHash='0', state='1', cdate=dts, mdate=dts ))
	db.session.commit()

# SUS Server Group -----------------------------------------------------------
def hasDefaultSUSGroup():
	res = MpAsusCatalogList.query.filter(MpAsusCatalogList.listid=='1').first()
	if res is not None:
		return True
	else:
		return False

def addDefaultSUSGroup():
	# Check for config
	if hasDefaultSUSGroup():
		return False

	# Add Default SUS Server Group
	db.session.add(MpAsusCatalogList(name="Default", listid='1', version="0"))
	db.session.commit()

# Server Config --------------------------------------------------------------
def hasDefaultServerConfig():
	res = MpServer.query.filter(MpServer.isMaster==1).first()
	if res is not None:
		return True
	else:
		return False

def addDefaultServerConfig():
	# Check for config
	if hasDefaultServerConfig():
		return False

	# Add Agent Config
	db.session.add(MpServer(listid='1', server="localhost", port="2600", useSSL='1', useSSLAuth='0', allowSelfSignedCert='1', isMaster='1', isProxy='0', active='0'))
	db.session.commit()

def hasDefaultServerList():
	res = MpServerList.query.filter(MpServerList.listid==1).first()
	if res is not None:
		return True
	else:
		return False

def addDefaultServerList():
	# Check for config
	if not hasDefaultServerList():
		return False

	# Add Agent Config
	db.session.add(MpServerList(listid='1', name="Default", version="0"))
	db.session.commit()