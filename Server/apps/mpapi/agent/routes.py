from werkzeug import secure_filename
from flask import Flask, request, abort, current_app
import flask_restful
from flask_restful import reqparse
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from distutils.version import StrictVersion, LooseVersion
import sys
import uuid
import plistlib
import hashlib
from ast import literal_eval

from . import *
from .. import db
from .. mputil import *
from .. model import *
from .. mplogger import *

parser = reqparse.RequestParser()

# Agent Updates
class MP_AgentUpdate(MPResource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(MP_AgentUpdate, self).__init__()

    def get(self, cuuid, agentver='0', agentbuild='0'):
        try:
            args = self.reqparse.parse_args()

            if not isValidClientID(cuuid):
                log_Error('[AgentUpdate][GET]: Failed to verify ClientID (' + cuuid + ')')
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify ClientID'}, 424

            if not isValidSignature(self.req_signature, cuuid, self.req_uri, self.req_ts):
                if current_app.config['ALLOW_MIXED_SIGNATURES'] == True:
                    log_Info('[AgentUpdate][GET]: ALLOW_MIXED_SIGNATURES is enabled.')
                else:
                    log_Error('[AgentUpdate][GET]: Failed to verify Signature for client (' + cuuid + ')')
                    return {"result": '', "errorno": 424, "errormsg": 'Failed to verify Signature'}, 424

            _at = AgentUpdates()
            log_Info('[AgentUpdate][GET]: Checking if update to Agent is needed for CUUID: %s AGENTVER: %s' % (cuuid, agentver))
            _update = _at.agentUpdates(cuuid, agentver, agentbuild)

            if _update is not None:
                log_Info('[AgentUpdate][GET]: Update is needed for CUUID: %s' % (cuuid))
                log_Debug('[AgentUpdate][GET]: Update CUUID: %s DICT: %s' % (cuuid, _update))

                return {"result": _update, "errorno": 0, "errormsg": 'none'}, 200
            else:
                log_Info('[AgentUpdate][GET]: No update is needed for CUUID: %s' %(cuuid))

                return {"result": {}, "errorno": 0, "errormsg": 'none'}, 202

        except IntegrityError, exc:
            log_Error('[MP_AgentUpdate][Get][IntegrityError] CUUID: %s Message: %s' % (cuuid, exc.message))
            return {"result": '', "errorno": 500, "errormsg": exc.message}, 500
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_Error('[MP_AgentUpdate][Get][Exception][Line: %d] CUUID: %s Message: %s' % (
                exc_tb.tb_lineno, cuuid, e.message))
            return {'errorno': 500, 'errormsg': e.message, 'result': {}}, 500

# Agent Updater Updates
class MP_AgentUpdaterUpdate(MPResource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(MP_AgentUpdaterUpdate, self).__init__()

    def get(self, cuuid, agentver):
        try:
            args = self.reqparse.parse_args()

            if not isValidClientID(cuuid):
                log_Error('[AgentUpdaterUpdate][GET]: Failed to verify ClientID (' + cuuid + ')')
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify ClientID'}, 424

            if not isValidSignature(self.req_signature, cuuid, self.req_uri, self.req_ts):
                if current_app.config['ALLOW_MIXED_SIGNATURES'] == True:
                    log_Info('[MP_AgentUpdaterUpdate][GET]: ALLOW_MIXED_SIGNATURES is enabled.')
                else:
                    log_Error('[AgentUpdaterUpdate][GET]: Failed to verify Signature for client (' + cuuid + ')')
                    return {"result": '', "errorno": 424, "errormsg": 'Failed to verify Signature'}, 424

            _at = AgentUpdates()
            log_Info('[AgentUpdaterUpdate][GET]: Checking if update to Updater is needed for CUUID: %s AGENTVER: %s' % (cuuid, agentver))
            _update = _at.agentUpdates(cuuid, agentver)

            if _update is not None:
                log_Info('[AgentUpdaterUpdate][GET]: Update is needed for CUUID: %s' % (cuuid))
                log_Debug('[AgentUpdaterUpdate][GET]: Update CUUID: %s DICT: %s' % (cuuid, _update))

                return {"result": _update, "errorno": 0, "errormsg": 'none'}, 200
            else:
                log_Info('[AgentUpdaterUpdate][GET]: No update is needed for CUUID: %s' % (cuuid))

                return {"result": {}, "errorno": 0, "errormsg": 'none'}, 202

        except IntegrityError, exc:
            log_Error('[MP_AgentUpdaterUpdate][Get][IntegrityError] CUUID: %s Message: %s' % (cuuid, exc.message))
            return {"result": '', "errorno": 500, "errormsg": exc.message}, 500
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_Error('[MP_AgentUpdaterUpdate][Get][Exception][Line: %d] CUUID: %s Message: %s' % (
                exc_tb.tb_lineno, cuuid, e.message))
            return {'errorno': 500, 'errormsg': e.message, 'result': {}}, 500

# Agent Plugins
class MP_PluginHash(MPResource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(MP_PluginHash, self).__init__()

    def get(self, cuuid, plugin_name, plugin_bundle, plugin_version):
        try:
            args = self.reqparse.parse_args()

            if not isValidClientID(cuuid):
                log_Error('[PluginHash][GET]: Failed to verify ClientID (' + cuuid + ')')
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify ClientID'}, 424

            if not isValidSignature(self.req_signature, cuuid, self.req_uri, self.req_ts):
                log_Error('[PluginHash][GET]: Failed to verify Signature for client (' + cuuid + ')')
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify Signature'}, 424

            log_Info('[PluginHash][GET]: Verifying Plugin (%s) for CUUID: %s' % (plugin_name, cuuid))
            q_result = MPPluginHash.query.filter(MPPluginHash.pluginName == plugin_name, MPPluginHash.pluginBundleID == plugin_bundle, MPPluginHash.pluginVersion == plugin_version).first()
            #bresult = MPPluginHash.query.filter(MPPluginHash.pluginName == plugin_name).all()

            if q_result is not None:
                log_Info('[PluginHash][GET]: Plugin (%s) is verified for CUUID: %s' % (plugin_name, cuuid))
                log_Debug('[PluginHash][GET]: Plugin HASH Result %s for CUUID: %s' % (q_result.asDict, cuuid))
                return {"result": q_result.hash, "errorno": 0, "errormsg": 'none'}, 200
            else:
                log_Error('[PluginHash][GET]: Plugin (%s) hash could not be found.' % (plugin_name))
                return {"result": {}, "errorno": 404, "errormsg": 'Plugin hash could not be found.'}, 404

        except IntegrityError, exc:
            log_Error('[MP_PluginHash][Get][IntegrityError] CUUID: %s Message: %s' % (cuuid, exc.message))
            return {"result": '', "errorno": 500, "errormsg": exc.message}, 500
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_Error('[MP_PluginHash][Get][Exception][Line: %d] CUUID: %s Message: %s' % (
                exc_tb.tb_lineno, cuuid, e.message))
            return {'errorno': 500, 'errormsg': e.message, 'result': {}}, 500

# Agent Configuration
class MP_ConfigData(MPResource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(MP_ConfigData, self).__init__()

    def get(self, token):
        try:
            args = self.reqparse.parse_args()

            if token != '0': # DEBUG, remove in prod
                _user = verify_auth_token(token)
                if not _user or (_user == "BadSignature" or _user == "SignatureExpired"):
                    log_Error('[MP_ConfigData][GET]: Failed to verify token')
                    return {"result": '', "errorno": 424, "errormsg": 'Failed to verify token'}, 424

                if not isValidAdminUser(_user):
                    log_Error('[MP_ConfigData][GET]: Failed to verify user (%s) rights' % (_user))
                    return {"result": '', "errorno": 424, "errormsg": 'Failed to verify user rights'}, 424

            config = GenAgentConfig().config()
            if config == None:
                log_Error("[MP_ConfigData][GET]: Error getting agent config.")
                return {"result": {}, "errorno": 425, "errormsg": "Error getting agent config."}, 425

            _srv_pub_key = "NA"
            _srv_pub_key_hash = "NA"
            res = MpSiteKeys.query.filter(MpSiteKeys.active==1).first()
            if res is not None:
                _srv_pub_key = res.pubKey
                _srv_pub_key_hash = res.pubKeyHash

            configPlist = plistlib.writePlistToString(config)
            log_Debug("[MP_ConfigData][GET]: Agent Config Result: %s" % (configPlist))
            resData = {'plist': configPlist, 'pubKey':_srv_pub_key, 'pubKeyHash':_srv_pub_key_hash}
            return {"result": resData, "errorno": 0, "errormsg": ""}, 200

        except IntegrityError, exc:
            log_Error('[MP_ConfigData][Get][IntegrityError] Message: %s' % (exc.message))
            return {"result": '', "errorno": 500, "errormsg": ""}, 500
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_Error('[MP_ConfigData][Get][Exception][Line: %d] Message: %s' % (
                exc_tb.tb_lineno, e.message))
            return {'errorno': 500, 'errormsg': e.message, 'result': {}}, 500

# Upload Agent Packages
class MP_UploadAgentPackage(MPResource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(MP_UploadAgentPackage, self).__init__()

    def post(self, agent_id, token):

        try:
            args = self.reqparse.parse_args()

            if token != '0': # DEBUG, remove in prod
                _user = verify_auth_token(token)
                if not _user or (_user == "BadSignature" or _user == "SignatureExpired"):
                    log_Error('[MP_UploadAgentPackage][GET]: Failed to verify token')
                    return {"result": '', "errorno": 424, "errormsg": 'Failed to verify token'}, 424

                if not isValidAdminUser(_user):
                    log_Error('[MP_UploadAgentPackage][GET]: Failed to verify user (%s) rights' % (_user))
                    return {"result": '', "errorno": 424, "errormsg": 'Failed to verify user rights'}, 424

            r = request
            _files = r.files
            _filesName = ['fBase', 'fUpdate', 'fComplete']

            fData = literal_eval(r.form['data'])
            fBase = r.files['fBase']
            fBaseHash = ""
            fUpdate = r.files['fUpdate']
            fUpdateHash = ""
            fAgent = r.files['fComplete']
            if not fBase or not fUpdate or not fAgent:
                log_Error('[MP_UploadAgentPackage][GET]: Failed to verify uploaded files. User: %s' % (_user))
                return {"result": '', "errorno": 425, "errormsg": 'Failed to verify uploaded files.'}, 425

            # Verify if Agent already exists
            agent_ver = fData['app']['agent_ver']
            app_ver = fData['app']['version']
            app_build = fData['app']['build']
            haveAgent = MpClientAgent.query.filter(MpClientAgent.agent_ver == agent_ver,
                                                   MpClientAgent.version == app_ver,
                                                   MpClientAgent.build == app_build,
                                                   MpClientAgent.type == "app").first()
            if haveAgent:
                log_Error('[MP_UploadAgentPackage][GET]: Agent(AGENT VER: %s, APP VER: %s) Already Exists User: %s' % (agent_ver, app_ver, _user))
                return {"result": '', "errorno": 426, "errormsg": 'Agent Already Exists'}, 426

            # Save uploaded files
            upload_dir = os.path.join(current_app.config['AGENT_CONTENT_DIR'], agent_id)
            _files = [ fBase, fUpdate, fAgent ]
            if not os.path.isdir(upload_dir):
                os.makedirs(upload_dir)

            for f in _files:
                log_Debug('Saving: %s' % (f.filename))
                filename = secure_filename(f.filename)
                _pkg_file_path = os.path.join(upload_dir, filename)

                if os.path.exists(_pkg_file_path):
                    log_Debug('Removing existing agent file (%s)' % (_pkg_file_path))
                    os.remove(_pkg_file_path)

                f.save(_pkg_file_path)
                if "Base.pkg" in f.filename:
                    fBaseHash = fileHashSHA1(_pkg_file_path)
                elif "Updater.pkg" in f.filename:
                    fUpdateHash = fileHashSHA1(_pkg_file_path)


            #log_Debug('fBaseHash: %s' % (fBaseHash))
            #log_Debug('fUpdateHash: %s' % (fUpdateHash))

            # Save Agent Data to database
            log_Debug('[MP_UploadAgentPackage][GET]: Create Base Agent Data Record')
            agentObjApp = MpClientAgent()
            setattr(agentObjApp, 'puuid', agent_id)
            setattr(agentObjApp, 'type', 'app')
            setattr(agentObjApp, 'osver', fData['app']['osver'])
            setattr(agentObjApp, 'agent_ver', fData['app']['agent_ver'])
            setattr(agentObjApp, 'version', fData['app']['version'])
            setattr(agentObjApp, 'build', fData['app']['build'])
            setattr(agentObjApp, 'pkg_name', fData['app']['pkg_name'])
            setattr(agentObjApp, 'pkg_url', os.path.join('/mp-content/clients/updates', agent_id,fBase.filename))
            setattr(agentObjApp, 'pkg_hash', fBaseHash)
            setattr(agentObjApp, 'cdate', datetime.now())
            setattr(agentObjApp, 'mdate', datetime.now())
            log_Debug('[MP_UploadAgentPackage][GET]: Add Base Agent Data Record')
            db.session.add(agentObjApp)

            log_Debug('[MP_UploadAgentPackage][GET]: Create Updater Agent Data Record')
            agentObjUpdt = MpClientAgent()
            setattr(agentObjUpdt, 'puuid', agent_id)
            setattr(agentObjUpdt, 'type', 'update')
            setattr(agentObjUpdt, 'osver', fData['update']['osver'])
            setattr(agentObjUpdt, 'agent_ver', fData['update']['agent_ver'])
            setattr(agentObjUpdt, 'version', fData['update']['version'])
            setattr(agentObjUpdt, 'build', fData['update']['build'])
            setattr(agentObjUpdt, 'pkg_name', fData['update']['pkg_name'])
            setattr(agentObjUpdt, 'pkg_url', os.path.join('/mp-content/clients/updates', agent_id,fUpdate.filename))
            setattr(agentObjUpdt, 'pkg_hash', fUpdateHash)
            setattr(agentObjUpdt, 'cdate', datetime.now())
            setattr(agentObjUpdt, 'mdate', datetime.now())
            log_Debug('[MP_UploadAgentPackage][GET]: Add Updater Agent Data Record')
            db.session.add(agentObjUpdt)
            db.session.commit()

            return {"result": '', "errorno": 0, "errormsg": ""}, 200
        except OSError as err:
            log_Error('[MP_UploadAgentPackage][Post][OSError] MP_UploadAgentPackage: %s' % (format(err)))
            return {"result": '', "errorno": err.errno, "errormsg": format(err)}, 500
        except IntegrityError, exc:
            log_Error('[MP_UploadAgentPackage][Post][IntegrityError] MP_UploadAgentPackage: %s' % (exc.message))
            return {"result": '', "errorno": 500, "errormsg": ""}, 500
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_Error('[MP_UploadAgentPackage][Post][Exception][Line: %d] Message: %s' % (
                exc_tb.tb_lineno, e.message))
            return {'errorno': 500, 'errormsg': e.message, 'result': {}}, 500
''' ------------------------------- '''
''' NOT A WEB SERVICE CLASS         '''
''' Class for Getting the Scan List '''

class AgentUpdates():

    def __init__(self):
        pass

    def agentUpdaterUpdates(self, cuuid, updaterVersion, agentBuild=0):

        updateID = self.agentUpdateID()
        if updateID is None:
            return None

        updateDict = self.agentUpdateForID(updateID)
        if updateDict is None:
            log_Error('[AgentUpdates][agentUpdaterUpdates]: Error, we have a RID but no data.')
            return None

        clientData = self.clientOSInfo(cuuid)
        if clientData is None:
            log_Error('[AgentUpdates][agentUpdaterUpdates]: Error, we were handed a client ID which does not exist')
            return None

        # Check OS is supported
        if updateDict['osver'] != '*':
            updateOSVer = updateDict['osver'].replace('+', '')
            if not (LooseVersion(updateOSVer) <= StrictVersion(clientData['osver'])):
                log_Error("[AgentUpdates][agentUpdates]: Client OS Ver is not greater or equal to the min os supported.")
                return None

        # Check Agent Updater version
        if updateDict['agent_ver'] == updaterVersion:
            # Version is the same check build Rev
            if agentBuild != 0:
                if int(updateDict['build']) <= int(agentBuild):
                    log_Info("[AgentUpdates][agentUpdates]: Client is running the latest version and no newer build rev.")
                    return None

        elif not (LooseVersion(updateDict['agent_ver']) < LooseVersion(updateVersion)):
            log_Info("[AgentUpdates][agentUpdates]: Client is running the latest version.")
            return None

        # Apply filters to see if agent is allowed to update
        updateFilters = self.agentUpdaterClientFilters()
        agent_needs_update = False
        if updateFilters is not None:
            log_Info("[AgentUpdates][agentUpdaterUpdates]: Client (%s) needs agent update." % (cuuid))
            agent_needs_update = self.evaluateFilters(clientData, updateFilters)

        if agent_needs_update == True:

            update = {'puuid': updateDict['puuid'], 'type': updateDict['type'],
                    'pkg_hash': updateDict['pkg_hash'], 'pkg_name': updateDict['pkg_name'],
                    'pkg_url': updateDict['pkg_url'], 'updateAvailable': True}
            log_Debug("[AgentUpdates][agentUpdaterUpdates]: Client (%s) Update Data: %s" % (cuuid,update))
            return update
        else:
            return {}

    def agentUpdates(self, cuuid, updateVersion, agentBuild=0):

        updateID = self.agentUpdateID()
        if updateID is None:
            return None

        updateDict = self.agentUpdateForID(updateID)
        log_Info('updateDict: %s' % (updateDict))
        if updateDict is None:
            log_Error("[AgentUpdates][agentUpdates]: Error, we have a RID but no data")
            return None

        clientData = self.clientOSInfo(cuuid)
        if clientData is None:
            log_Error("[AgentUpdates][agentUpdates]: Error, we were handed a client ID (%s) which does not exist" % (cuuid))
            return None

        # Check OS is supported
        if updateDict['osver'] != '*':
            updateOSVer = updateDict['osver'].replace('+', '')
            if not (LooseVersion(updateOSVer) <= StrictVersion(clientData['osver'])):
                log_Error("[AgentUpdates][agentUpdates]: Client OS Ver is not greater or equal to the min os supported.")
                return None

        # Check Agent Updater version
        if updateDict['agent_ver'] == updateVersion:
            # Version is the same check build Rev
            if agentBuild != 0:
                if int(updateDict['build']) <= int(agentBuild):
                    log_Info("[AgentUpdates][agentUpdates]: Client is running the latest version and no newer build rev.")
                    return None

        elif not (LooseVersion(updateDict['agent_ver']) < LooseVersion(updateVersion)):
            log_Info("[AgentUpdates][agentUpdates]: Client is running the latest version.")
            return None

        # Apply filters to see if agent is allowed to update
        updateFilters = self.agentUpdaterClientFilters()
        agent_needs_update = False
        if updateFilters is not None:
            agent_needs_update = self.evaluateFilters(clientData, updateFilters)

        if agent_needs_update == True:
            update = {'puuid': updateDict['puuid'], 'type': updateDict['type'],
                    'pkg_hash': updateDict['pkg_hash'], 'pkg_name': updateDict['pkg_name'],
                    'pkg_url': updateDict['pkg_url'], 'updateAvailable': True}
            log_Debug("[AgentUpdates][agentUpdates]: Client (%s) Update Data: %s" % (cuuid, update))
            return update
        else:
            return {}

    ''' Get the RID of the latest updater agent update '''

    def agentUpdaterUpdateID(self):
        _sql = """Select rid From mp_client_agents
                Where type = 'update'
                AND active = '1'
                ORDER BY
                INET_ATON(SUBSTRING_INDEX(CONCAT(agent_ver,'.0.0.0.0.0'),'.',6)) DESC,
                INET_ATON(SUBSTRING_INDEX(CONCAT(build,'.0.0.0.0.0'),'.',6)) DESC
                """
        res = db.engine.execute(_sql).first()
        if res is not None:
            return res[0]

        return None

    ''' Get the RID of the latest agent update '''

    def agentUpdateID(self):
        _sql = """Select rid From mp_client_agents
                Where type = 'app'
                AND active = '1'
                ORDER BY
                INET_ATON(SUBSTRING_INDEX(CONCAT(agent_ver,'.0.0.0.0.0'),'.',6)) DESC,
                INET_ATON(SUBSTRING_INDEX(CONCAT(build,'.0.0.0.0.0'),'.',6)) DESC
                """
        res = db.engine.execute(_sql).first()
        if res is not None:
            return res[0]

        return None

    ''' Get a dictionary of the agent update data from the RID '''

    def agentUpdateForID(self, rid):
        _data = MpClientAgent.query.filter(MpClientAgent.rid == rid).first()
        if _data is not None:
            return _data.asDict
        else:
            return None

    ''' Get Client Info Needed for filtering data '''

    def clientOSInfo(self, cuuid):

        #Base.query = self.db.query_property()
        result = {}
        result['cuuid'] = cuuid
        result['osver'] = "10.0.0"
        result['ipaddr'] = "127.0.0.1"
        result['hostname'] = "localhost"
        result['domain'] = "Default"
        result['patchgroup'] = "Default"

        _client = MpClient.query.with_entities(MpClient.osver, MpClient.ipaddr, MpClient.hostname).filter(MpClient.cuuid == cuuid).first()
        _plist = MpClientPlist.query.with_entities(MpClientPlist.Domain,MpClientPlist.PatchGroup).filter(MpClientPlist.cuuid == cuuid).first()

        if _client is not None:
            result['osver'] = _client[0]
            result['ipaddr'] = _client[1]
            result['hostname'] = _client[2]
        else:
            return None

        if _plist is not None:
            result['domain'] = _plist[0]
            result['patchgroup'] = _plist[1]
        else:
            print "BAD"

        return result

    ''' Query DB for agent filters '''

    def agentUpdaterClientFilters(self):
        _data = MpClientAgentsFilter.query.all()
        results = []
        if _data is not None:
            for row in _data:
                results.append(row.asDict)

            return results
        else:
            return None

    def runFilterUsingAttributes(self, clientInfo, attr, attrOpr, attrFltr):

        if attr.lower() == "all" and attrOpr.lower() == "eq" and attrFltr.lower() == "all":
            return True

        if attr in clientInfo:
            if attrOpr.lower() == "eq":
                if clientInfo[attr].lower() == attrFltr.lower():
                    return True
                else:
                    return False
            else:
                if clientInfo[attr].lower() != attrFltr.lower():
                    return True
                else:
                    return False
        else:
            return False

    def evaluateFilters(self, clientInfo, filters):

        myRes = {}
        section = 0
        filter_count = 0
        result_passed = 0

        for i in filters:
            # If attribute_condition is "or" then start a new section
            if i['attribute_condition'].lower() == "or":
                filter_count = 0
                result_passed = 0
                section += 1

            # filter count & Test if filter applies
            filter_count += 1
            filter_result = self.runFilterUsingAttributes(clientInfo, i['attribute'], i['attribute_oper'],
                                                          i['attribute_filter'])
            if filter_result == True:
                # If filter is true add 1 to result
                result_passed += 1

            # Build section result dict, always adding the count and result to it
            section_dict = {'count': filter_count, 'result': result_passed}
            myRes[section] = section_dict

            # If the attribute_condition is None, then do not process any other filters
            if i['attribute_condition'].lower() == "none":
                break

        xres = 0
        for x in myRes:
            sect = myRes[x]
            if sect['count'] == sect['result']:
                xres += 1

        # If one section evaluates as true then the client needs an update
        if xres >= 1:
            return True
        else:
            return False


class GenAgentConfig():
    def __init__(self):
        pass

    def config(self):

        # Get Default Config Info, need default agent config ID
        _defaultConfigID = AgentConfig.query.filter_by(isDefault = 1).first()
        if not _defaultConfigID:
            log_Error("[GenAgentConfig][config]: No Default Agent Config Was Found.")
            return None

        # Get all agent data from aid
        _agentConfig = AgentConfigData.query.filter(AgentConfigData.aid == _defaultConfigID.aid).all()
        if not _agentConfig:
            log_Error("[GenAgentConfig][config]: No Agent Config Data Found")
            return None

        _autoReg = "0"
        _parking = "0"
        _regQuery = MpClientsRegistrationSettings.query.first()
        if _regQuery is not None:
            rec = _regQuery.asDict
            if rec['autoreg'] == 1:
                _autoReg = "1"
            if rec['client_parking'] == 1:
                _parking = "1"

        masterConf = self.serverDataOfType("Master")
        proxyConf = self.serverDataOfType("Proxy")
        if masterConf == None and proxyConf == None:
            log_Error("[GenAgentConfig][config]: No serverDataOfType for Master or Proxy found.")
            return None

        defaultProxy = False
        defaultMaster = False

        _aConfig = {}
        _default = {}
        _enforced = {}

        for row in _agentConfig:
            print row.asDict

            if row.enforced == 0:
                if 'Proxy' in row.akey:
                    defaultProxy = True
                elif 'MPServer' in row.akey:
                    defaultMaster = True
                else:
                    _default[row.akey] = row.akeyValue

            elif row.enforced == 1:
                if 'Proxy' in row.akey:
                    defaultProxy = False
                elif 'MPServer' in row.akey:
                    defaultMaster = False
                else:
                    _enforced[row.akey] = row.akeyValue

        if defaultMaster:
            _default['MPServerAddress'] = masterConf['MPServerAddress']
            _default['MPServerPort']    = masterConf['MPServerPort']
            _default['MPServerSSL']     = masterConf['MPServerSSL']
            _default['MPServerAllowSelfSigned'] = masterConf['MPServerAllowSelfSigned']
            if current_app.config['REQUIRE_SIGNATURES'] == True:
                _default['registrationEnabled'] = '1'
            else:
                _default['registrationEnabled'] = '0'

            _default['autoregEnabled'] = _autoReg
            _default['clientParkingEnabled'] = _parking

        else:
            _enforced['MPServerAddress'] = masterConf['MPServerAddress']
            _enforced['MPServerPort'] = masterConf['MPServerPort']
            _enforced['MPServerSSL'] = masterConf['MPServerSSL']
            _enforced['MPServerAllowSelfSigned'] = masterConf['MPServerAllowSelfSigned']

        if defaultProxy:
            _default['MPProxyServerAddress'] = proxyConf['MPProxyServerAddress']
            _default['MPProxyServerPort'] = proxyConf['MPProxyServerPort']
            _default['MPProxyEnabled'] = proxyConf['MPProxyEnabled']
        else:
            _enforced['MPProxyServerAddress'] = proxyConf['MPProxyServerAddress']
            _enforced['MPProxyServerPort'] = proxyConf['MPProxyServerPort']
            _enforced['MPProxyEnabled'] = proxyConf['MPProxyEnabled']

        _aConfig["default"] = _default
        _aConfig["enforced"] = _enforced

        print _aConfig

        return _aConfig

    def serverDataOfType(self,type):

        _res = {}

        if type == "Proxy":
            _server = MpServer.query.filter(MpServer.isProxy == 1, MpServer.active == 1).first()
            if _server:
                _res['MPProxyServerAddress'] = _server.server
                _res['MPProxyServerPort'] = _server.port
                _res['MPProxyEnabled'] = _server.useSSL
            else:
                _res['MPProxyServerAddress'] = "localhost"
                _res['MPProxyServerPort'] = 2600
                _res['MPProxyEnabled'] = 0

            return _res
        elif type == "Master":
            _server = MpServer.query.filter(MpServer.isMaster == 1, MpServer.active == 1).first()
            if _server:
                _res['MPServerAddress'] = _server.server
                _res['MPServerPort'] = _server.port
                _res['MPServerSSL'] = _server.useSSL
                _res['MPServerAllowSelfSigned'] = _server.allowSelfSignedCert
                return _res
            else:
                log_Error("[serverDataOfType]: No Data for Master Server found.")
                return None
        else:
            log_Error("[serverDataOfType]: Type not accepted.")
            return None


def fileHashSHA1(file):
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    sha1 = hashlib.sha1()

    with open(file, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()

# Add Routes Resources
agent_api.add_resource(MP_AgentUpdate,         '/agent/update/<string:cuuid>/<string:agentver>/<string:agentbuild>')
agent_api.add_resource(MP_AgentUpdaterUpdate,  '/agent/updater/<string:cuuid>/<string:agentver>')

agent_api.add_resource(MP_PluginHash,          '/agent/plugin/hash/<string:cuuid>/<string:plugin_name>/<string:plugin_bundle>/<string:plugin_version>')

agent_api.add_resource(MP_ConfigData,           '/agent/config/<string:token>')
agent_api.add_resource(MP_UploadAgentPackage,   '/agent/upload/<string:agent_id>/<string:token>')
