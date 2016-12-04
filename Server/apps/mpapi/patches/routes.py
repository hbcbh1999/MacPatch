from flask import Flask, request, abort
import flask_restful
from flask_restful import reqparse
from sqlalchemy.exc import IntegrityError
from datetime import datetime


from . import *
from .. import db
from .. mputil import *
from .. model import *
from .. mplogger import *

parser = reqparse.RequestParser()

# Clientin Info/Status
class ClientPatchStatus(MPResource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(ClientPatchStatus, self).__init__()

    def get(self,cuuid):
        try:
            args = self.reqparse.parse_args()
            _body = request.get_json(silent=True)

            if not isValidClientID(cuuid):
                log_Error('[ClientPatchStatus][Get]: Failed to verify ClientID (%s)' % (cuuid))
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify ClientID'}, 424

            if not isValidSignature(self.req_signature, cuuid, self.req_uri, self.req_ts):
                log_Error('[ClientPatchStatus][Get]: Failed to verify Signature for client (%s)' % (cuuid))
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify Signature'}, 424

            apple_obj = MpClientPatchesApple.query.filter_by(cuuid=cuuid).all()
            custom_obj = MpClientPatchesThird.query.filter_by(cuuid=cuuid).all()

            apple = []
            third = []
            for row in apple_obj:
                apple.append(row.as_dict())

            for row in custom_obj:
                third.append(row.as_dict())

            # Return Results
            res = {'apple':apple, 'third': third, 'total': (len(apple) + len(third))}
            log_Debug('[ClientPatchStatus][Get]: Result: %s' % (res))
            return {"result": res, "errorno": 0, "errormsg": 'none'}, 200

        except IntegrityError, exc:
            log_Error('[ClientPatchStatus][Get][IntegrityError] CUUID: %s Message: %s' % (cuuid, exc.message))
            return {"result": '', "errorno": 500, "errormsg": exc.message}, 500
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_Error('[ClientPatchStatus][Get][Exception][Line: %d] CUUID: %s Message: %s' % (exc_tb.tb_lineno, cuuid, e.message))
            return {'errorno': 500, 'errormsg': e.message, 'result': ''}, 500

# Get Patch Scan List (Third Only)
class PatchScanList(MPResource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(PatchScanList, self).__init__()

    def get(self, cuuid):
        try:
            args = self.reqparse.parse_args()
            _body = request.get_json(silent=True)

            if not isValidClientID(cuuid):
                log_Error('[PatchScanList][Get]: Failed to verify ClientID (%s)' % (cuuid))
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify ClientID'}, 424

            if not isValidSignature(self.req_signature, cuuid, self.req_uri, self.req_ts):
                log_Error('[PatchScanList][Get]: Failed to verify Signature for client (%s)' % (cuuid))
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify Signature'}, 424

            _scanList = PatchScan()
            _list = _scanList.getScanList()

            if _list is not None:
                result = {'patches': _list}
                return {"result": result, "errorno": 0, "errormsg": 'none'}, 200
            else:
                log_Error('[PatchScanList][Get]: Failed to get a scan list for client %s' % (cuuid))
                return {"result": {}, "errorno": 0, "errormsg": 'none'}, 404

        except IntegrityError, exc:
            log_Error('[PatchScanList][Get][IntegrityError] CUUID: %s Message: %s' % (cuuid, exc.message))
            return {"result": '', "errorno": 500, "errormsg": exc.message}, 500
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_Error('[PatchScanList][Get][Exception][Line: %d] CUUID: %s Message: %s' % (exc_tb.tb_lineno, cuuid, e.message))
            return {'errorno': 500, 'errormsg': e.message, 'result': ''}, 500

# Get Patch Scan List filter on OS Ver e.g. 10.9, 10.10 ... (Third Only)
class PatchScanListFilterOS(MPResource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(PatchScanListFilterOS, self).__init__()

    def get(self, cuuid, osver='*', state='Production'):
        try:
            args = self.reqparse.parse_args()
            _body = request.get_json(silent=True)

            if not isValidClientID(cuuid):
                log_Error('[PatchScanListFilterOS][Get]: Failed to verify ClientID (%s)' % (cuuid))
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify ClientID'}, 424

            if not isValidSignature(self.req_signature, cuuid, self.req_uri, self.req_ts):
                log_Error('[PatchScanListFilterOS][Get]: Failed to verify Signature for client (%s)' % (cuuid))
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify Signature'}, 424

            log_Debug('[PatchScanListFilterOS][Get]: Args: cuuid=(%s) osver=(%s) state=(%s)' % (cuuid, osver, state))

            _scanList = PatchScan()
            _list = _scanList.getScanList(osver)

            if _list is not None:
                result = {'patches': _list}
                return {"result": result, "errorno": 0, "errormsg": 'none'}, 200
            else:
                log_Error('[PatchScanListFilterOS][Get]: Failed to get a scan list for client %s' % (cuuid))
                return {"result": {}, "errorno": 0, "errormsg": 'none'}, 404

        except IntegrityError, exc:
            log_Error('[PatchScanListFilterOS][Get][IntegrityError] CUUID: %s Message: %s' % (cuuid, exc.message))
            return {"result": '', "errorno": 500, "errormsg": exc.message}, 500
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_Error('[PatchScanListFilterOS][Get][Exception][Line: %d] CUUID: %s Message: %s' % (
                exc_tb.tb_lineno, cuuid, e.message))
            return {'errorno': 500, 'errormsg': e.message, 'result': ''}, 500

# Get Patch Group Patches
class PatchGroupPatches(MPResource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(PatchGroupPatches, self).__init__()

    def get(self, cuuid, patchGroup ):

        try:
            args = self.reqparse.parse_args()
            _body = request.get_json(silent=True)

            if not isValidClientID(cuuid):
                log_Error('[PatchGroupPatches][Get]: Failed to verify ClientID (%s)' % (cuuid))
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify ClientID'}, 424

            if not isValidSignature(self.req_signature, cuuid, self.req_uri, self.req_ts):
                log_Error('[PatchGroupPatches][Get]: Failed to verify Signature for client (%s)' % (cuuid))
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify Signature'}, 424


            # Get Patch Group ID from Name
            group_id = 'NA'
            q_group = MpPatchGroup.query.filter(MpPatchGroup.name == patchGroup).first()
            if q_group is not None:
                if q_group.id:
                    group_id = q_group.id

                    # Get Patch Group Patches
                    q_data = MpPatchGroupData.query.filter(MpPatchGroupData.pid == group_id, MpPatchGroupData.data_type == 'JSON').first()
                    if q_data is not None:
                        if q_data.data:
                            return {"result": q_data.data, "errorno": 0, "errormsg": ''}, 200
            else:
                log_Error('[PatchGroupPatches][Get][%s]: No patch group (%s) found.' % (cuuid, patchGroup))
                return {"result": '', "errorno": 404, "errormsg": 'Not Found'}, 404


        except IntegrityError, exc:
            log_Error('[PatchGroupPatches][Get][IntegrityError] CUUID: %s Message: %s' % (cuuid, exc.message))
            return {"result": '', "errorno": 500, "errormsg": exc.message}, 500
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_Error('[PatchGroupPatches][Get][Exception][Line: %d] CUUID: %s Message: %s' % (
                exc_tb.tb_lineno, cuuid, e.message))
            return {'errorno': 500, 'errormsg': e.message, 'result': ''}, 500

# Post Client Patch Scan Data
class PatchScanData(MPResource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(PatchScanData, self).__init__()

    def post(self, cuuid, patch_type):
        # Type: 0 = error, 1 = Apple, 2 = Third

        try:
            args = self.reqparse.parse_args()
            _body = request.get_json(silent=True)

            if not isValidClientID(cuuid):
                log_Error('[PatchScanData][Post]: Failed to verify ClientID (%s)' % (cuuid))
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify ClientID'}, 424

            if not isValidSignature(self.req_signature, cuuid, request.data, self.req_ts):
                log_Error('[PatchScanData][Post]: Failed to verify Signature for client (%s)' % (cuuid))
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify Signature'}, 424

            if patch_type == "0":
                log_Error('[PatchScanData][Post][%s]: Type (%s) not accepted ' % (cuuid, patch_type))
                return {"result": '', "errorno": 404, "errormsg": "Type not accepted"}, 404

            elif patch_type == "1":
                # Apple Patches
                log_Debug('[PatchScanData][Post][%s]: Type (%s) selected' % (cuuid, patch_type))
                MpClientPatchesApple.query.filter(MpClientPatchesApple.cuuid == cuuid).delete()
                db.session.commit()

                if _body != None and 'rows' in _body:
                    for row in _body['rows']:
                        apple_object = MpClientPatchesApple()
                        # Set All of the column values
                        for col in apple_object.columns:
                            if col in row:
                                setattr(apple_object, col, row[col])

                        # Set the Mod DateTime
                        setattr(apple_object, 'mdate', datetime.now())
                        setattr(apple_object, 'cuuid', cuuid)

                        try:
                            log_Debug('[PatchScanData][Post][%s]: Adding Apple: %s' % (cuuid, apple_object.asDict))
                            db.session.add(apple_object)
                            db.session.commit()
                        except IntegrityError, exc:
                            db.session.rollback()
                            log_Error('[PatchScanData][Post][%s]: Error adding apple record. %s' % (cuuid, exc.message))
                            return {"result": '', "errorno": 0, "errormsg": exc.message}, 406

                    # Rows have been added
                    return {"result": '', "errorno": 0, "errormsg": 'none'}, 201
            elif patch_type == "2":
                # Custom Patches
                log_Debug('[PatchScanData][Post][%s]: Type (%s) selected' % (cuuid, patch_type))
                MpClientPatchesThird.query.filter(MpClientPatchesThird.cuuid == cuuid).delete()
                db.session.commit()

                if _body != None and 'rows' in _body:
                    for row in _body['rows']:
                        third_object = MpClientPatchesThird()
                        # Set All of the column values
                        for col in third_object.columns:
                            if col in row:
                                setattr(third_object, col, row[col])

                        # Set the Mod DateTime
                        setattr(third_object, 'mdate', datetime.now())
                        setattr(third_object, 'cuuid', cuuid)

                        try:
                            log_Debug('[PatchScanData][Post][%s]: Adding Custom: %s' % (cuuid, third_object.asDict))
                            db.session.add(third_object)
                            db.session.commit()
                        except IntegrityError, exc:
                            db.session.rollback()
                            log_Error('[PatchScanData][Post][%s]: Error adding custom record. %s' % (cuuid, exc.message))
                            return {"result": '', "errorno": 0, "errormsg": exc.message}, 406

                    # Rows have been added
                    return {"result": '', "errorno": 0, "errormsg": 'none'}, 201
            else:
                log_Error('[PatchScanData][Post][%s]: Type (%s) not found' % (cuuid, patch_type))
                return {"result": '', "errorno": 404, "errormsg": "Type not found"}, 404


        except IntegrityError, exc:
            log_Error('[PatchScanData][Post][IntegrityError] CUUID: %s Message: %s' % (cuuid, exc.message))
            return {"result": '', "errorno": 500, "errormsg": exc.message}, 500
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_Error('[PatchScanData][Post][Exception][Line: %d] CUUID: %s Message: %s' % (
                exc_tb.tb_lineno, cuuid, e.message))
            return {'errorno': 500, 'errormsg': e.message, 'result': []}, 500

# Post Client Patch Install Data
class PatchInstallData(MPResource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(PatchInstallData, self).__init__()

    def post(self, cuuid, patch_type, patch):

        try:
            args = self.reqparse.parse_args()

            if not isValidClientID(cuuid):
                log_Error('[PatchInstallData][Post]: Failed to verify ClientID (%s)' % (cuuid))
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify ClientID'}, 424

            if not isValidSignature(self.req_signature, cuuid, self.req_uri, self.req_ts):
                log_Error('[PatchInstallData][Post]: Failed to verify Signature for client (%s)' % (cuuid))
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify Signature'}, 424

            # Type: 0 = error, 1 = Apple, 2 = Third
            _patchType = 3
            _patchName = patch
            if patch_type.lower() == "apple" or patch_type == '1':
                _patchType = 0
                _patchTypeName = "apple"
                log_Debug('[PatchInstallData][Post][%s]: Adding Apple Patch: %s' % (cuuid, patch))

            if patch_type.lower() == "third" or patch_type == '2':
                _patchType = 1
                _patchTypeName = "third"
                _patchData = MpPatch.query.filter(MpPatch.puuid == patch).first()
                if not _patchData:
                    log_Error("[PatchInstallData][Post]: Unable to get patch info for %s" % (patch))
                _patchName = "%s-%s" % (_patchData.patch_name, _patchData.patch_ver)
                log_Debug('[PatchInstallData][Post][%s]: Adding Custom Patch: %s' % (cuuid, _patchName))

            # Create Patch Obj to add to DB
            installed_patch = MpInstalledPatch()
            setattr(installed_patch, 'cuuid', cuuid)
            setattr(installed_patch, 'mdate', datetime.now())
            setattr(installed_patch, 'patch', patch)
            setattr(installed_patch, 'patch_name', _patchName)
            setattr(installed_patch, 'type', _patchTypeName)
            setattr(installed_patch, 'type_int', _patchType)

            db.session.add(installed_patch)
            db.session.commit()

            # Update Status Table
            if _patchType == 0:
                # Apple Patch
                log_Debug('[PatchInstallData][Post][%s]: Removing Apple Patch (%s) from needed table' % (cuuid, patch))
                MpClientPatchesApple.query.filter(MpClientPatchesApple.patch == patch, MpClientPatchesApple.cuuid == cuuid).delete()
                db.session.commit()

            if _patchType == 1:
                # Custom Patch
                log_Debug('[PatchInstallData][Post][%s]: Removing Custom Patch (%s) from needed table' % (cuuid, _patchName))
                _patch_data = MpClientPatchesThird.query.filter(MpClientPatchesThird.patch_id == patch, MpClientPatchesThird.cuuid == cuuid).first()
                if _patch_data is not None:
                    if _patch_data.rid:
                        MpClientPatchesThird.query.filter(MpClientPatchesThird.rid == _patch_data.rid).delete()
                        db.session.commit()

            return {"result": '', "errorno": 0, "errormsg": ''}, 202

        except IntegrityError, exc:
            db.session.rollback()
            log_Error('[PatchInstallData][Post][IntegrityError] CUUID: %s Message: %s' % (cuuid, exc.message))
            return {"result": '', "errorno": 500, "errormsg": exc.message}, 500
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_Error('[PatchInstallData][Post][Exception][Line: %d] CUUID: %s Message: %s' % (
                exc_tb.tb_lineno, cuuid, e.message))
            return {'errorno': 500, 'errormsg': e.message, 'result': ''}, 500


''' ------------------------------- '''
''' NOT A WEB SERVICE CLASS         '''
''' Class for Getting the Scan List '''
class PatchScan():

    def __init__(self):
        pass

    def bundleIDList(self):
        '''
            Return a tuple of bundle_id set and ordered list based on version number
            descending.
        '''

        #Query DataBase get all Custom Patches based on bundle and version
        q = MpPatch.query.with_entities(MpPatch.puuid, MpPatch.patch_name, MpPatch.patch_ver, MpPatch.bundle_id,
                                        MpPatch.patch_reboot, MpPatch.patch_state, MpPatch.active, MpPatch.rid
        ).filter(MpPatch.active == 1, MpPatch.patch_state == "Production").order_by(MpPatch.bundle_id.desc()).all()

        bundleList = []
        results = []
        if q is not None:
            for row in q:
                bundleList.append(row[3])
                results.append({"puuid":row[0],"patch_name":row[1],"patch_ver":row[2],"bundle_id":row[3],
                                "patch_reboot":row[4],"patch_state":row[5],"active":row[6],"rid":row[7]})

            # Create Unique List of Bundle ID's
            bundleList = set(bundleList)
            # Sort the list of patches by bundle_id and then by version number
            sortedlist = sorted(results, key=lambda elem: "%s %s" % ( elem['bundle_id'], (".".join([i.zfill(5) for i in elem['patch_ver'].split(".")])) ), reverse=True)
            # Return the result as a tuple
            return bundleList, sortedlist
        else:
            return None, None

    def scanCriteriaForPatch(self, puuid):
        '''
            Get Patch Scab Query Data for patch id (puuid)
            returns a list of dictionaries
        '''

        results = []
        q = MpPatchesCriteria.query.with_entities(MpPatchesCriteria.type,MpPatchesCriteria.type_order,MpPatchesCriteria.type_data).filter(MpPatchesCriteria.puuid == puuid).order_by(MpPatchesCriteria.type_order).all()
        if q is not None:
            for row in q:
                query_ =  row.type.strip() + "@" + row.type_data.strip()
                results.append({'id':str(row.type_order),'qStr':query_})

        return results

    def osCheckForPatch(self, puuid, os='*'):
        '''
            Get Patch Scab Query Data for patch id (puuid)
            returns a list of dictionaries
        '''

        result = False
        q = MpPatchesCriteria.query.with_entities(MpPatchesCriteria.type_data).filter(MpPatchesCriteria.puuid == puuid, MpPatchesCriteria.type == "OSVersion").first()
        if q is not None:
            if q[0] == "*":
                return True
            if os in q[0]:
                return True
            if "*" in q[0]:
                for i in q[0].split(','):
                    _i = i.split('.')
                    qOS = _i[0]+"."+_i[1]

                    cOS = '0.0'
                    _o = os.split('.')
                    if len(_o) >= 2:
                        cOS = _o[0]+"."+_o[1]

                    if qOS.strip() == cOS.strip():
                        return True

        return result

    # Really the only public method to be used
    def getScanList(self, os=None):
        results = []
        b = self.bundleIDList()
        for name in b[0]:
            for x in b[1]:
                if name == x["bundle_id"]:
                    if os:
                        if self.osCheckForPatch(x["puuid"],os):
                            x['query'] = self.scanCriteriaForPatch(x["puuid"])
                            x.pop("rid",None)
                            results.append(x)
                            break
                    else:
                        x['query'] = self.scanCriteriaForPatch(x["puuid"])
                        x.pop("rid",None)
                        results.append(x)
                        break

        return results

# Add Routes Resources
patches_api.add_resource(ClientPatchStatus,     '/client/patch/status/<string:cuuid>')
patches_api.add_resource(PatchScanListFilterOS, '/client/patch/scanlist/<string:cuuid>',endpoint='noOS')
patches_api.add_resource(PatchScanListFilterOS, '/client/patch/scanlist/<string:cuuid>/<string:osver>',endpoint='withOS')

patches_api.add_resource(PatchGroupPatches,     '/client/patch/group/<string:patchGroup>/<string:cuuid>')
# Post Client Patch Scan Data
patches_api.add_resource(PatchScanData,         '/client/patch/scan/<string:patch_type>/<string:cuuid>')
# Post Client Patch Install Data
patches_api.add_resource(PatchInstallData,      '/client/patch/install/<string:patch>/<string:patch_type>/<string:cuuid>')
