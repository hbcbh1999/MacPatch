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

# Client AV Data Collection
class AVData(MPResource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        avi = AvInfo()
        for column in avi.columns:
            self.reqparse.add_argument(column, type=str, required=False, location='json')

        super(AVData, self).__init__()

    def post(self, cuuid):

        try:
            args = self.reqparse.parse_args()
            _body = request.get_json(silent=True)

            if not isValidClientID(cuuid):
                log_Error('Failed to verify ClientID (' + cuuid + ')')
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify ClientID'}, 424

            if not isValidSignature(self.req_signature, cuuid, _body, self.req_ts):
                log_Error('Failed to verify Signature for client (' + cuuid + ')')
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify Signature'}, 424

            av_obj = AvInfo.query.filter_by(cuuid=cuuid).first()

            if av_obj:
                # Update
                log_Info('Updating AV data for client (' + cuuid + ')')
                for col in av_obj.columns:
                    if col == 'mdate':
                        setattr(av_obj, col, datetime.now())
                    else:
                        setattr(av_obj, col, args[col])

                db.session.commit()
                return {"result": '', "errorno": 0, "errormsg": 'none'}, 201
            else:
                # Add
                log_Info('Adding AV data for client (' + cuuid + ')')
                av_new_obj = AvInfo()

                av_new_obj.cuuid = cuuid
                for col in av_new_obj.columns:
                    if col == 'mdate':
                        setattr(av_new_obj, col, datetime.now())
                    else:
                        setattr(av_new_obj, col, args[col])

                db.session.add(av_new_obj)
                db.session.commit()
                return {"result": '', "errorno": 0, "errormsg": 'none'}, 201

        except IntegrityError, exc:
            log_Error('[AVData][Post][IntegrityError] CUUID: %s Message: %s' % (cuuid, exc.message))
            return {"result": '', "errorno": 500, "errormsg": exc.message}, 500
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_Error('[AVData][Post][Exception][Line: %d] CUUID: %s Message: %s' % (
                exc_tb.tb_lineno, cuuid, e.message))
            return {'errorno': 500, 'errormsg': e.message, 'result': {}}, 500

# Antivirus Latest Defs Info
class AVDefs(MPResource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(AVDefs, self).__init__()

    def get(self, cuuid, av_engine):
        try:
            args = self.reqparse.parse_args()
            _body = request.get_json(silent=True)

            if not isValidClientID(cuuid):
                log_Error('Failed to verify ClientID (' + cuuid + ')')
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify ClientID'}, 424

            if not isValidSignature(self.req_signature, cuuid, _body, self.req_ts):
                log_Error('Failed to verify Signature for client (' + cuuid + ')')
                return {"result": '', "errorno": 424, "errormsg": 'Failed to verify Signature'}, 424

            avdefs = AvDefs.filter(AvDefs.engine == av_engine, AvDefs.current == 'YES').first()

            if avdefs:
                av_data = {'defsUpdate': avdefs.file}
                log_Debug('[AVDefs]: Defs Data: %s Client: %s' % (av_data, cuuid))
                return {"result": av_data, "errorno": 0, "errormsg": 'none'}, 200
            else:
                log_Error('AV Engine Not found. for client (' + cuuid + ')')
                return {"result": '', "errorno": 404, "errormsg": 'AV Engine Not found.'}, 404

        except IntegrityError, exc:
            log_Error('[AVDefs][Get][IntegrityError] CUUID: %s Message: %s' % (cuuid, exc.message))
            return {"result": '', "errorno": 500, "errormsg": exc.message}, 500
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_Error('[AVDefs][Get][Exception][Line: %d] CUUID: %s Message: %s' % (
                exc_tb.tb_lineno, cuuid, e.message))
            return {'errorno': 500, 'errormsg': e.message, 'result': {}}, 500

# Add Routes Resources
antivirus_api.add_resource(AVData, '/client/av/<string:cuuid>')
antivirus_api.add_resource(AVDefs, '/client/av/defs/<string:av_engine>/<string:cuuid>')