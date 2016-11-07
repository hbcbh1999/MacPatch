from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import text
from datetime import datetime

from .  import dashboard
from .. import login_manager
from .. models import MPUser, MpClient
from .. import db

@dashboard.route('/dashboard')
@login_required
def index():

    clients = MpClient.query.all()
    _client_count = len(clients)

    # Get OS Ver Data
    osVerData = []
    sql1 = text('SELECT osver, Count(osver) As Count From mp_clients Group By osver')
    result = db.engine.execute(sql1)
    for row in result:
        osVerData.append((str(row[0]), str(row[1])))

    # Get Reboot Count
    rbData = []
    sql2 = text("""SELECT CASE needsReboot
                WHEN '0' THEN 'False'
                WHEN '1' THEN 'True'
                ELSE needsReboot END AS needsReboot,
                Count(needsReboot) As Count
                FROM mp_clients
                Group By needsReboot""")

    rb_result = db.engine.execute(sql2)
    for row in rb_result:
        rbData.append((str(row[0]).title(), str(row[1])))

    # Get Model Info
    sql3 = text("""
        SELECT hw.mpa_Model_Identifier AS ModelType, Count(hw.mpa_Model_Identifier) As Count
        FROM mp_clients mpc
        LEFT JOIN mpi_SPHardwareOverview hw ON hw.cuuid = mpc.cuuid
        Group By hw.mpa_Model_Identifier
        Order By Count Desc
        Limit 0,10
    """)
    mdl_data = []
    mdl_result = db.engine.execute(sql3)
    for row in mdl_result:
        mdl_data.append((str(row[0]).title(), str(row[1])))

    # Client Patch Status

    sql4 = text("""
        Select 	patch, Count(*) As Clients
        From 	client_patch_status_view
        LEFT 	JOIN mp_clients_view ci
        ON 		client_patch_status_view.cuuid=ci.cuuid
        Group By patch
        Order By Clients DESC
        LIMIT 0, 10 """)
    pch_data = []
    pch_result = db.engine.execute(sql4)
    for row in pch_result:
        pch_data.append((str(row[0]).title(), str(row[1])))


    # Client Checkin Status
    status_data = []
    today = datetime.now()
    normal = 0
    warn = 0
    alert = 0
    sql5 = text(""" SELECT mdate From mp_clients""")
    status_result = db.engine.execute(sql5)
    for row in status_result:
        diff = today - row[0]
        if diff.days <= 7:
            normal = normal + 1
        if diff.days > 7 and diff.days < 15:
            warn = warn + 1
        if diff.days >= 15:
            alert = alert + 1

    status_data = [normal, warn, alert]

    agents_data = []
    sql6 = text(""" select client_version, Count(*) as Total from mp_clients
    GROUP BY client_version
    Order By total Desc
    """)
    agentver_result = db.engine.execute(sql6)
    for row in agentver_result:
        agents_data.append((str(row[0]).title(), str(row[1])))



    return render_template('dashboard.html', clientCount=_client_count, osData=osVerData,
                           rebootData=rbData, modelData=mdl_data, patchData=pch_data, clientStatus=status_data,
                           agentVers=agents_data)