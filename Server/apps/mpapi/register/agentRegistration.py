from .. model import *
from .. import db

def isClientRegistered(ClientID):
    reg_query_object = MPAgentRegistration.query.filter_by(cuuid=ClientID).first()

    if reg_query_object is not None:
        rec = reg_query_object.asDict
        if rec['enabled'] == 1:
            return True
        else:
            return False

    return False

def isKeyRequired(ClientID):
    pass

def isKeyValid(aKey):
    pass

def setKeyUsed(ClientID, aKey):
    pass
