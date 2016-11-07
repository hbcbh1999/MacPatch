from flask import Flask, request
import flask_restful
from flask_restful import Resource, reqparse
from flask_restful_swagger import swagger

from . import *
from .. import db
#from .agentRegistration import *
from .. mputil import *
from .. model import *

# Client Reg Test
class Test(MPResource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(Test, self).__init__()

    @swagger.operation(notes='Get: Test Registration')
    def get(self):
        return {
            'Reg': 'Test',
        }


# Client Reg Process
class Registration(MPResource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        '''
        mpc = MpClientsRegistration()
        for column in mpc.columns:
            self.reqparse.add_argument(column, type = str, required = False, location = 'json')

        # Required but not part of the model
        self.reqparse.add_argument('authHash', type = str, required = True, location = 'json')
        self.reqparse.add_argument('authReq', type = str, required = True, location = 'json')
        self.reqparse.add_argument('client_csr', type = str, required = True, location = 'json')
        '''
        super(Registration, self).__init__()

    @swagger.operation(
        notes='Post Client Reg',
        parameters=[
            {
              "name": "body",
              "description": "",
              "required": False,
              "allowMultiple": False,
              "dataType": "MpClientsRegistration",
              "paramType": "body"
            }
        ])
    def post(self, cuuid, regKey="NA"):
        '''
            Content Dict: cKey, CPubKeyPem, CPubKeyDer, ClientHash
            cKey = Client Auth Key, used for signatures
            CPubKeyPem = Client Pub Key - PEM
            CPubKeyDer = Client Pub Key - DER
            ClientHash = Client Agent Parts Hash (MPAgent, MPAgentExec, MPWorker)
        '''
        content = request.get_json(silent=True)
        if all(key in content for key in ("cKey", "CPubKeyPem", "CPubKeyDer", "ClientHash")):
            print cuuid
            print regKey
        else:
            return {"result": '', "errorno": 300, "errormsg": 'Required Keys are missing.'}, 300


        return {"result": '', "errorno": 0, "errormsg": ''}, 200


# Client Reg Status
class RegistrationStatus(MPResource):

    def __init__(self):
        super(RegistrationStatus, self).__init__()

    @swagger.operation(notes='Get Client registration Status')
    def get(self,cuuid):

        reg_query_object = MPAgentRegistration.query.filter_by(cuuid=cuuid).first()

        if reg_query_object is not None:
            rec = reg_query_object.asDict
            if rec['enabled'] == 1:
                return {"result": True, "errorno": 0, "errormsg": ""}, 200
            else:
                return {"result": False, "errorno": 206, "errormsg": ""}, 206

        return {"result": False, "errorno": 204, "errormsg": ""}, 204


''' Private Methods '''


# Add Routes Resources
register_api.add_resource(Test,                 '/client/RegTest')
register_api.add_resource(Registration,         '/client/register/<string:cuuid>',endpoint='noRegKey')
register_api.add_resource(Registration,         '/client/register/<string:cuuid>/<string:regKey>',endpoint='yaRegKey')
register_api.add_resource(RegistrationStatus,   '/client/register/status/<string:cuuid>')