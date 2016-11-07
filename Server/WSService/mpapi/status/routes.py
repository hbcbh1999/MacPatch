from flask import Flask, request, abort
import flask_restful
from flask_restful import reqparse
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from distutils.version import LooseVersion
import base64

from . import *
from .. import db
from .. mputil import *
from .. model import *
from .. mplogger import *

parser = reqparse.RequestParser()

class ServerStatus(MPResource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(ServerStatus, self).__init__()

    def get(self):
        try:
            log_Info("Running Server Status With DB Check")
            args = self.reqparse.parse_args()
            _body = request.get_json(silent=True)

            res = MpServer.query.filter(MpServer.isMaster==1).first()

            admUsrLst = []
            admUsr = AdmGroupUsers.query.filter(AdmGroupUsers.email_notification == 1,AdmGroupUsers.user_email != None).all()
            for i in admUsr:
                admUsrLst.append(i.user_email)

            if res:
                res_data = {'status': "Server is up and db connection is good."}
                return {"result": res_data, "errorno": 0, "errormsg": 'none'}, 200
            else:
                res_data = {'status': "Server is up and db connection is no good."}
                return {"result": res_data, "errorno": 404, "errormsg": ''}, 404

        except IntegrityError, exc:
            log_Error('[ServerStatus][Get][IntegrityError] Message: %s' % (exc.message))
            return {'errorno': 500, 'errormsg': exc.message, 'result': ''}, 500
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_Error('[ServerStatus][Get][Exception][Line: %d] Message: %s' % (
                exc_tb.tb_lineno, e.message))
            return {'errorno': 500, 'errormsg': e.message, 'result': ''}, 500

class ServerStatusNoDB(MPResource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(ServerStatusNoDB, self).__init__()

    def get(self):
        try:
            log_Info("Running Server Status With DB NO Check")
            args = self.reqparse.parse_args()
            _body = request.get_json(silent=True)

            res_data = {'status': "Server is up flask is working."}
            return {"result": res_data, "errorno": 0, "errormsg": 'none'}, 200


        except IntegrityError, exc:
            log_Error('[ServerStatusNoDB][Get][IntegrityError] Message: %s' % (exc.message))
            return {'errorno': 500, 'errormsg': exc.message, 'result': ''}, 500
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_Error('[ServerStatusNoDB][Get][Exception][Line: %d] Message: %s' % (
                exc_tb.tb_lineno, e.message))
            return {'errorno': 500, 'errormsg': e.message, 'result': ''}, 500


# Routes
status_api.add_resource(ServerStatus,      '/server/status')
status_api.add_resource(ServerStatusNoDB,  '/server/status/nodb')
