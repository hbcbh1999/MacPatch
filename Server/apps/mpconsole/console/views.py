from flask import render_template, jsonify, request
import json

from . import console
from ..models import *
from .. import db

@console.route('/admin')
def admin():
    return render_template('blank.html', data={}, columns={})

@console.route('/tasks')
def tasks():
    return render_template('console_tasks.html')

@console.route('/tasks/assignClientsToGroups',methods=['POST'])
def assignClientsToGroup():

    q_defaultGroup = MpClientGroups.query.filter(MpClientGroups.group_name == "default").first()
    if q_defaultGroup:
        defaultGroupID = q_defaultGroup.group_id
    else:
        return json.dumps({'error': 404, 'errormsg': 'Default group not found.'}), 404

    clients = MpClient.query.all()
    clientsInGroups = MpClientGroupMembers.query.all()

    for client in clients:
        if not client.cuuid in clientsInGroups:
            addToGroup = MpClientGroupMembers()
            setattr(addToGroup, 'group_id', defaultGroupID)
            setattr(addToGroup, 'cuuid', client.cuuid)
            db.session.add(addToGroup)
            db.session.commit()

    return json.dumps({'error': 0}), 200

'''
    Client Agents
'''
@console.route('/agent/deploy')
def agentDeploy(tab=1):

    groupResult = {}

    qGet1 = MpClientAgent.query.all()
    cListCols = MpClientAgent.__table__.columns
    cListHiddenCols = ['state']
    cListEditCols = ['state']
    # Sort the Columns based on "doc" attribute
    sortedCols = sorted(cListCols, key=getDoc)

    qGet2 = MpClientAgentsFilter.query.all()
    cListFiltersCols = MpClientAgentsFilter.__table__.columns
    # Sort the Columns based on "doc" attribute
    sortedFilterCols = sorted(cListFiltersCols, key=getDoc)

    _agents = []
    for v in qGet1:
        _row = {}
        for column, value in v.asDict.items():
            if column != "cdate":
                if column == "mdate":
                    #_row[column] = value.strftime("%Y-%m-%d %H:%M:%S")
                    _row[column] = value
                elif column == "active":
                    _row[column] = "Yes" if value == 1 else "No"
                else:
                    _row[column] = value

        _agents.append(_row)

    _filters = []
    for v in qGet2:
        _row = {}
        for column, value in v.asDict.items():
            if column != "cdate":
                if column == "mdate":
                    # _row[column] = value.strftime("%Y-%m-%d %H:%M:%S")
                    _row[column] = value
                else:
                    _row[column] = value

        _filters.append(_row)

    # Get All Client Group Admins
    '''
    _admins = []
    _qadm = MpClientGroupAdmins.query.filter(MpClientGroupAdmins.group_id == name).all()
    if _qadm:
        for u in _qadm:
            _row = {'user_id':u.group_admin,'owner': 'False'}
            _admins.append(_row)

    _owner = MpClientGroups.query.filter(MpClientGroups.group_id == name).first()
    _admins.append({'user_id':_owner.group_owner,'owner': 'True'})
    '''
    groupResult['Agents'] = {'data': _agents, 'columns': sortedCols}
    groupResult['Filters'] = {'data': _filters, 'columns': sortedFilterCols}
    groupResult['Admin'] = True

    return render_template('adm_agent_deploy.html', gResults=groupResult, selectedTab=tab)

@console.route('/agent/configure')
def agentConfig():
    return render_template('console_tasks.html')

@console.route('/agent/plugins')
def agentPlugins():
    return render_template('console_tasks.html')

'''
    MacPatch Servers
'''
@console.route('/servers/mp')
def mpServers():
    return render_template('console_tasks.html')

'''
    ASUS Servers
'''
@console.route('/servers/asus')
def asusServers():
    return render_template('console_tasks.html')

'''
    DataSources
'''
@console.route('/server/datasources')
def mpDataSources():
    return render_template('console_tasks.html')

''' Global '''
def getDoc(col_obj):
    return col_obj.doc