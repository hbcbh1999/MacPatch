from mpconsole import db

# Rev 1
#

from datetime import *
from sqlalchemy import BigInteger, Column, DateTime, Integer, LargeBinary, String, Text
from sqlalchemy.dialects.mysql import LONGTEXT, MEDIUMTEXT, INTEGER

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

class CommonBase(db.Model):
    __abstract__ = True

    @property
    def asDict(self):
        """Convert date/datetime to string inorder to jsonify"""
        result = {}
        for column in self.__table__.columns:
            if column.name != "rid":
                try:
                    if column.type.python_type in [type(date(2000, 1, 1)), type(datetime(2000, 1, 1))]:
                        if getattr(self, column.name) is not None:
                            result[column.name] = str(getattr(self, column.name))
                        else:
                            # don't convert None to string
                            result[column.name] = getattr(self, column.name)
                    else:
                        result[column.name] = getattr(self, column.name)
                except Exception, e:
                    result[column.name] = getattr(self, column.name)

        return result

    @property
    def columns(self):
        results = []
        for column in self.__table__.columns:
            if column.name != "rid":
                results.append(column.name)

        return results

    @property
    def columnsAlt(self):
        results = []
        for column in self.__table__.columns:
            if column.name != "rid" or column.name != "date" or column.name != "mdate" or column.name != "rid":
                results.append(column.name)

        return results

    @property
    def hasColumn(self,col):
        result = False
        for column in self.__table__.columns:
            if column.name != col:
                result = True
                break

        return result

''' Database Tables '''

# ------------------------------------------
''' START - Tables for Web Services'''

# ------------------------------------------
## Registration

# mp_agent_registration
class MPAgentRegistration(CommonBase):

    __tablename__ = 'mp_agent_registration'

    rid = Column(BigInteger, primary_key=True)
    cuuid = Column(String(50), nullable=False)
    enabled = Column(Integer, server_default='0')
    clientKey = Column(String(100), server_default='NA')
    pubKeyPem = Column(Text)
    pubKeyPemHash = Column(String(100), server_default='NA')
    reg_date = Column(DateTime, nullable=False, server_default='1970-01-01 00:00:00')

# mp_clients_wait_reg
class MpClientsWantingRegistration(CommonBase):
    __tablename__ = 'mp_clients_wait_reg'

    rid = Column(BigInteger, primary_key=True, nullable=False)
    cuuid = Column(String(50), nullable=False, unique=True)
    hostname = Column(String(255), nullable=False)
    req_date = Column(DateTime, nullable=True)

# mp_clients_reg_conf
class MpClientsRegistrationSettings(CommonBase):
    __tablename__ = 'mp_clients_reg_conf'

    rid = Column(Integer, primary_key=True, nullable=False)
    autoreg = Column(Integer, nullable=True, server_default='0')
    autoreg_key = Column(Integer, nullable=True, server_default='999999')

# mp_client_reg_keys
class MpClientRegKeys(CommonBase):
    __tablename__ = 'mp_client_reg_keys'

    rid = Column(BigInteger, primary_key=True, nullable=False)
    cuuid = Column(String(50), nullable=False, unique=True)
    regKey = Column(String(255), nullable=False)
    active = Column(Integer, nullable=True, server_default='1')

    reg_date = Column(DateTime, nullable=True, server_default='1970-01-01 00:00:00')

# mp_reg_keys
class MpRegKeys(CommonBase):
    __tablename__ = 'mp_reg_keys'

    rid = Column(BigInteger, primary_key=True, nullable=False)
    regKey = Column(String(255), nullable=False)
    keyType = Column(Integer, nullable=True, server_default='0')
    keyQuery = Column(String(255), nullable=False)
    active = Column(Integer, nullable=True, server_default='1')
    validFromDate = Column(DateTime, nullable=True, server_default='1970-01-01 00:00:00')
    validToDate = Column(DateTime, nullable=True, server_default='1970-01-01 00:00:00')

# mp_clients
class MpClient(CommonBase):
    __tablename__ = 'mp_clients'

    rid = Column(BigInteger, primary_key=True)
    cuuid = Column(String(50), nullable=False)
    serialno = Column(String(100), server_default='NA')
    hostname = Column(String(255), server_default='NA')
    computername = Column(String(255), server_default='NA')
    ipaddr = Column(String(64), server_default='NA')
    macaddr = Column(String(64), server_default='NA')
    osver = Column(String(255), server_default='NA')
    ostype = Column(String(255), server_default='NA')
    consoleuser = Column(String(255), server_default='NA')
    needsreboot = Column(String(255), server_default='NA')
    agent_version = Column(String(20), server_default='NA')
    client_version = Column(String(20), server_default='NA')
    mdate = Column(DateTime)

# mp_clients_plist
class MpClientPlist(CommonBase):
    __tablename__ = 'mp_clients_plist'

    rid = Column(BigInteger, primary_key=True)
    cuuid = Column(String(50), nullable=False, server_default='')
    mdate = Column(DateTime, nullable=False, server_default='1970-01-01 00:00:00')
    AllowClient = Column(String(255), server_default='NA')
    AllowServer = Column(String(255), server_default='NA')
    Domain = Column(String(255), server_default='NA')
    Name = Column(String(255), server_default='NA')
    MPInstallTimeout = Column(String(255), server_default='NA')
    PatchGroup = Column(String(255), server_default='NA')
    Description = Column(String(255), server_default='NA')
    MPServerAddress = Column(String(255), server_default='NA')
    MPServerPort = Column(String(255), server_default='NA')
    MPServerSSL = Column(String(255), server_default='NA')
    Reboot = Column(String(255), server_default='NA')
    DialogText = Column(String(255), server_default='NA')
    PatchState = Column(String(255), server_default='NA')
    MPAgentExecDebug = Column(String(255), server_default='NA')
    MPAgentDebug = Column(String(255), server_default='NA')
    SWDistGroup = Column(String(255), server_default='NA')
    SWDistGroupState = Column(String(255), server_default='NA')


# ------------------------------------------
## Patches Needed

# mp_client_patches_apple
class MpClientPatchesApple(CommonBase):
    __tablename__ = 'mp_client_patches_apple'

    rid         = Column(BigInteger, primary_key=True)
    cuuid       = Column(String(50), nullable=False)
    mdate       = Column(DateTime, server_default='1970-01-01 00:00:00')
    patch       = Column(String(255), nullable=False)
    type        = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    size        = Column(String(255), nullable=False)
    recommended = Column(String(255), nullable=False)
    restart     = Column(String(255), nullable=False)
    version     = Column(String(255))

# mp_client_patches_third
class MpClientPatchesThird(CommonBase):
    __tablename__ = 'mp_client_patches_third'

    rid         = Column(BigInteger, primary_key=True)
    cuuid       = Column(String(50), nullable=False)
    mdate       = Column(DateTime, server_default='1970-01-01 00:00:00')
    patch       = Column(String(255), nullable=False)
    type        = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    size        = Column(String(255), nullable=False)
    recommended = Column(String(255), nullable=False)
    restart     = Column(String(255), nullable=False)
    patch_id    = Column(String(255), nullable=False)
    version     = Column(String(255))
    bundleID    = Column(String(255))


# ------------------------------------------
## Patch Content

# apple_patches
class ApplePatch(CommonBase):
    __tablename__ = 'apple_patches'

    rid              = Column(BigInteger, primary_key=True, nullable=False) #
    akey             = Column(String(50), nullable=False, info="AKEY") #
    description      = Column(Text, info="Description")
    description64    = Column(LONGTEXT) #
    osver_support    = Column(String(20), nullable=False, server_default="NA", info="OS Version") #
    patch_state      = Column(String(10), server_default="Create", info="Patch State") #
    patchname        = Column(String(20), nullable=False, server_default="NA", info="Patch Name") #
    postdate         = Column(DateTime, server_default='1970-01-01 00:00:00', info="Post Date") #
    restartaction    = Column(String(20), nullable=False, info="Reboot") #
    severity         = Column(String(10), nullable=False,  server_default='High', info="Severity")
    severity_int     = Column(Integer, server_default="3")
    supatchname      = Column(String(100), nullable=False, info="Patch Name Alt") #
    title            = Column(String(255), nullable=False, info="Title") #
    version          = Column(String(20), nullable=False, info="Version") #


    def columnsMeta(self):
        results = []
        results.append(('rid','rid'))
        results.append(('akey','akey'))
        results.append(('description','Description'))
        results.append(('description64','Description'))
        results.append(('osver_support','OS Version'))
        results.append(('patch_state','Patch State'))
        results.append(('patchname','Patch Name'))
        results.append(('postdate','Post Date'))
        results.append(('restartaction','Reboot'))
        results.append(('severity','Severity'))
        results.append(('severity_int','Severity Int'))
        results.append(('supatchname','SUPatch Name'))
        results.append(('title','Title'))
        results.append(('version','Version'))
        return results

# apple_patches_additions
class ApplePatchAdditions(CommonBase):
    __tablename__ = 'apple_patches_mp_additions'

    rid                     = Column(BigInteger, primary_key=True, nullable=False)
    version                 = Column(String(20), nullable=False)
    supatchname             = Column(String(100))
    severity                = Column(String(10), nullable=False,  server_default='High')
    severity_int            = Column(INTEGER(unsigned=True), server_default="3")
    patch_state             = Column(String(100), nullable=False, server_default="Create")
    patch_install_weight    = Column(INTEGER(unsigned=True), server_default="60")
    patch_reboot            = Column(INTEGER(unsigned=True), server_default="0")
    osver_support           = Column(String(10), nullable=False, server_default="NA")

# mp_patches
class MpPatch(CommonBase):
    __tablename__ = 'mp_patches'

    rid                     = Column(BigInteger, primary_key=True, nullable=False)
    puuid                   = Column(String(50), primary_key=True, nullable=False)
    bundle_id               = Column(String(50), nullable=False, server_default="gov.llnl.Default")
    patch_name              = Column(String(100), nullable=False)
    patch_ver               = Column(String(20), nullable=False)
    patch_vendor            = Column(String(255), server_default="NA")
    patch_install_weight    = Column(Integer, server_default="30")
    description             = Column(String(255))
    description_url         = Column(String(255))
    patch_severity          = Column(String(10), nullable=False)
    patch_state             = Column(String(10), nullable=False)
    patch_reboot            = Column(String(3), nullable=False)
    cve_id                  = Column(String(255))
    active                  =  server_default='1970-01-01 00:00:00'
    pkg_preinstall          = Column(Text)
    pkg_postinstall         = Column(Text)
    pkg_name                = Column(String(100))
    pkg_size                = Column(String(100), server_default="0")
    pkg_hash                = Column(String(100))
    pkg_path                = Column(String(255))
    pkg_url                 = Column(String(255))
    pkg_env_var             = Column(String(255))
    cdate                   = Column(DateTime, server_default='1970-01-01 00:00:00')
    mdate                   = Column(DateTime, server_default='1970-01-01 00:00:00')

# mp_patches_criteria
class MpPatchesCriteria(CommonBase):
    __tablename__ = 'mp_patches_criteria'

    rid                 = Column(BigInteger, primary_key=True, nullable=False)
    puuid               = Column(String(50), primary_key=True, nullable=False)
    type                = Column(String(50), nullable=False)
    type_data           = Column(Text, nullable=False)
    type_order          = Column(Integer, nullable=False)
    type_required_order = Column(Integer, nullable=False, server_default="0")

# mp_patches_requisits
class MpPatchesRequisits(CommonBase):
    __tablename__ = 'mp_patches_requisits'

    rid           = Column(BigInteger, primary_key=True, nullable=False)
    puuid         = Column(String(50))
    type          = Column(Integer, server_default='0')
    type_txt      = Column(String(255))
    type_order    = Column(Integer, server_default='0')
    puuid_ref     = Column(String(50))

# mp_installed_patches
class MpInstalledPatch(CommonBase):
    __tablename__ = 'mp_installed_patches'

    rid         = Column(BigInteger, primary_key=True)
    cuuid       = Column(String(50), nullable=False)
    mdate       = Column(DateTime, nullable=False, server_default='1970-01-01 00:00:00')
    patch       = Column(String(255), nullable=False)
    patch_name  = Column(String(255), server_default="NA")
    type        = Column(String(255), nullable=False)
    type_int    = Column(Integer)
    server_name = Column(String(255), server_default="NA")


# ------------------------------------------
## Patch Groups and Content

# mp_patch_group
class MpPatchGroup(CommonBase):
    __tablename__ = 'mp_patch_group'

    rid     = Column(BigInteger, primary_key=True)
    name    = Column(String(255), nullable=False)
    id      = Column(String(50), nullable=False)
    type    = Column(Integer, nullable=False, server_default="0")
    hash    = Column(String(50), server_default="0")
    mdate   = Column(DateTime, server_default='1970-01-01 00:00:00')

# mp_patch_group_data
class MpPatchGroupData(CommonBase):
    __tablename__ = 'mp_patch_group_data'

    rid         = Column(BigInteger, primary_key=True, nullable=False)
    pid         = Column(String(50), primary_key=True, nullable=False)
    hash        = Column(String(50), nullable=False)
    rev         = Column(BigInteger, server_default="-1")
    data        = Column(LONGTEXT(), nullable=False)
    data_type   = Column(String(4), server_default="")
    mdate       = Column(DateTime, server_default='1970-01-01 00:00:00')


# ------------------------------------------
## Client Agent

# mp_client_agents
class MpClientAgent(CommonBase):
    __tablename__ = 'mp_client_agents'

    rid         = Column(BigInteger, primary_key=True)
    puuid       = Column(String(50), nullable=False)
    type        = Column(String(10), nullable=False)
    osver       = Column(String(255), nullable=False, server_default="*")
    agent_ver   = Column(String(10), nullable=False)
    version     = Column(String(10))
    build       = Column(String(10))
    framework   = Column(String(10))
    pkg_name    = Column(String(100), nullable=False)
    pkg_url     = Column(String(255))
    pkg_hash    = Column(String(50))
    active      = Column(Integer, nullable=False, server_default="0")
    state       = Column(Integer, nullable=False, server_default="0")
    cdate       = Column(DateTime, server_default='1970-01-01 00:00:00')
    mdate       = Column(DateTime, server_default='1970-01-01 00:00:00')

# mp_client_agents_filters
class MpClientAgentsFilter(CommonBase):
    __tablename__ = 'mp_client_agents_filters'

    rid                 = Column(BigInteger, primary_key=True)
    type                = Column(String(255), nullable=False)
    attribute           = Column(String(255), nullable=False)
    attribute_oper      = Column(String(10), nullable=False)
    attribute_filter    = Column(String(255), nullable=False)
    attribute_condition = Column(String(10), nullable=False)


# ------------------------------------------
## AntiVirus

# av_info
class AvInfo(CommonBase):
    __tablename__ = 'av_info'

    rid         = Column(BigInteger, primary_key=True)
    cuuid       = Column(String(50), nullable=False, server_default="")
    mdate       = Column(DateTime, server_default='1970-01-01 00:00:00')
    app_path    = Column(String(255), server_default="NA")
    app_version = Column(String(255), server_default="NA")
    defs_date   = Column(String(50), server_default="NA")
    last_scan   = Column(DateTime, server_default='1970-01-01 00:00:00')

# av_defs
class AvDefs(CommonBase):
    __tablename__ = 'av_defs'

    rid             = Column(BigInteger, primary_key=True)
    mdate           = Column(DateTime, server_default='1970-01-01 00:00:00')
    engine          = Column(String(255), nullable=False)
    current         = Column(String(3), nullable=False)
    defs_date       = Column(DateTime, server_default='1970-01-01 00:00:00')
    defs_date_str   = Column(String(20), nullable=False)
    file            = Column(Text(), nullable=False)


# ------------------------------------------
## Inventory

# mp_inv_state
class MpInvState(CommonBase):
    __tablename__ = 'mp_inv_state'

    cuuid = Column(String(50), primary_key=True)
    mdate = Column(DateTime, server_default='1970-01-01 00:00:00')


# ------------------------------------------
## Servers

# mp_asus_catalogs
class MpAsusCatalog(CommonBase):
    __tablename__ = 'mp_asus_catalogs'

    rid                 = Column(BigInteger, primary_key=True)
    listid              = Column(Integer, nullable=False, server_default="1")
    catalog_url         = Column(String(255), nullable=False)
    os_minor            = Column(Integer, nullable=False)
    os_major            = Column(Integer, nullable=False)
    c_order             = Column(Integer)
    proxy               = Column(Integer, nullable=False, server_default="0")
    active              = Column(Integer, nullable=False, server_default="0")
    catalog_group_name  = Column(String(255), nullable=False)

# mp_asus_catalog_list
class MpAsusCatalogList(CommonBase):
    __tablename__ = 'mp_asus_catalog_list'

    rid     = Column(BigInteger, primary_key=True)
    listid  = Column(Integer, nullable=False)
    name    = Column(String(255), nullable=False)
    version = Column(Integer, nullable=False)

# mp_server_list
class MpServerList(CommonBase):
    __tablename__ = 'mp_server_list'

    rid     = Column(BigInteger, primary_key=True, nullable=False)
    listid  = Column(String(50), primary_key=True, nullable=False)
    name    = Column(String(255), nullable=False)
    version = Column(Integer, nullable=False, server_default="0")

# mp_servers
class MpServer(CommonBase):
    __tablename__ = 'mp_servers'

    rid                 = Column(BigInteger, primary_key=True)
    listid              = Column(String(50), nullable=False)
    server              = Column(String(255), nullable=False)
    port                = Column(Integer, nullable=False, server_default="2600")
    useSSL              = Column(Integer, nullable=False, server_default="1")
    useSSLAuth          = Column(Integer, nullable=False, server_default="0")
    allowSelfSignedCert = Column(Integer, nullable=False, server_default="1")
    isMaster            = Column(Integer, nullable=False, server_default="0")
    isProxy             = Column(Integer, nullable=False, server_default="0")
    active              = Column(Integer, nullable=False, server_default="1")


# ------------------------------------------
## Profiles

# mp_os_config_profiles
class MpOsConfigProfiles(CommonBase):
    __tablename__ = 'mp_os_config_profiles'

    rid                 = Column(BigInteger, primary_key=True, nullable=False)
    profileID           = Column(String(50), primary_key=True, nullable=False)
    profileIdentifier   = Column(String(255))
    profileData         = Column(LargeBinary)
    profileName         = Column(String(255))
    profileDescription  = Column(Text)
    profileHash         = Column(String(50))
    profileRev          = Column(Integer)
    enabled             = Column(Integer, server_default='0')
    uninstallOnRemove   = Column(Integer, server_default='1')
    cdate               = Column(DateTime, server_default='1970-01-01 00:00:00')
    mdate               = Column(DateTime, server_default='1970-01-01 00:00:00')

# mp_os_config_profiles_assigned
class MpOsConfigProfilesAssigned(CommonBase):
    __tablename__ = 'mp_os_config_profiles_assigned'

    rid         = Column(BigInteger, primary_key=True, nullable=False)
    profileID   = Column(String(50), primary_key=True, nullable=False)
    groupID     = Column(String(50), primary_key=True, nullable=False)


# ------------------------------------------
## Software

# mp_software
class MpSoftware(CommonBase):
    __tablename__ = 'mp_software'

    rid                 = Column(BigInteger, primary_key=True, nullable=False)
    suuid               = Column(String(50), primary_key=True, nullable=False)
    patch_bundle_id     = Column(String(100))
    auto_patch          = Column(Integer, nullable=False, server_default='0')
    sState              = Column(Integer, server_default='0')
    sName               = Column(String(255), nullable=False)
    sVendor             = Column(String(255))
    sVersion            = Column(String(40), nullable=False)
    sDescription        = Column(String(255))
    sVendorURL          = Column(String(255))
    sReboot             = Column(Integer, server_default='1')
    sw_type             = Column(String(10))
    sw_path             = Column(String(255))
    sw_url              = Column(String(255))
    sw_size             = Column(BigInteger, server_default='0')
    sw_hash             = Column(String(50))
    sw_pre_install_script   = Column(LONGTEXT())
    sw_post_install_script  = Column(LONGTEXT())
    sw_uninstall_script     = Column(LONGTEXT())
    sw_env_var              = Column(String(255))
    cdate                   = Column(DateTime, server_default='1970-01-01 00:00:00')
    mdate                   = Column(DateTime, server_default='1970-01-01 00:00:00')

# mp_software_criteria
class MpSoftwareCriteria(CommonBase):
    __tablename__ = 'mp_software_criteria'

    rid                 = Column(BigInteger, primary_key=True, nullable=False)
    suuid               = Column(String(50), primary_key=True, nullable=False)
    type                = Column(String(50), nullable=False)
    type_data           = Column(Text, nullable=False)
    type_order          = Column(Integer, nullable=False)
    type_required_order = Column(Integer, nullable=False, server_default='0')

# mp_software_group_tasks
class MpSoftwareGroupTasks(CommonBase):
    __tablename__ = 'mp_software_group_tasks'

    rid                 = Column(BigInteger, primary_key=True)
    sw_group_id         = Column(String(50), nullable=False)
    sw_task_id          = Column(String(50), nullable=False)
    selected            = Column(Integer, server_default='0')

# mp_software_groups
class MpSoftwareGroup(CommonBase):
    __tablename__ = 'mp_software_groups'

    rid             = Column(BigInteger, primary_key=True, nullable=False)
    gid             = Column(String(50), primary_key=True, nullable=False)
    gName           = Column(String(255), nullable=False)
    gDescription    = Column(String(255))
    gType           = Column(Integer, nullable=False, server_default='0')
    gHash           = Column(String(50), server_default='0')
    state           = Column(Integer, server_default='1')
    cdate           = Column(DateTime, server_default='1970-01-01 00:00:00')
    mdate           = Column(DateTime, server_default='1970-01-01 00:00:00')

# mp_software_groups_filters
class MpSoftwareGroupFilters(CommonBase):
    __tablename__ = 'mp_software_groups_filters'

    rid                 = Column(BigInteger, primary_key=True, nullable=False)
    gid                 = Column(String(50), nullable=False)
    attribute           = Column(String(255))
    attribute_oper      = Column(String(255))
    attribute_filter    = Column(String(255))
    attribute_condition = Column(String(255))
    datasource          = Column(String(255))

# mp_software_groups_privs
class MpSoftwareGroupPrivs(CommonBase):
    __tablename__ = 'mp_software_groups_privs'

    rid     = Column(BigInteger, primary_key=True, nullable=False)
    gid     = Column(String(50), nullable=False)
    uid     = Column(String(255), nullable=False)
    isowner = Column(Integer, nullable=False, server_default='0')

# mp_software_installs
class MpSoftwareInstall(CommonBase):
    __tablename__ = 'mp_software_installs'

    rid             = Column(BigInteger, primary_key=True, nullable=False)
    cuuid           = Column(String(50), primary_key=True, nullable=False, server_default='')
    tuuid           = Column(String(50))
    suuid           = Column(String(50))
    action          = Column(String(1), server_default='i')
    result          = Column(Integer)
    resultString    = Column(Text)
    cdate           = Column(DateTime, server_default='1970-01-01 00:00:00')

# mp_software_requisits
class MpSoftwareRequisits(CommonBase):
    __tablename__ = 'mp_software_requisits'

    rid           = Column(BigInteger, primary_key=True, nullable=False)
    suuid         = Column(String(50))
    type          = Column(Integer, server_default='0')
    type_txt      = Column(String(255))
    type_order    = Column(Integer, server_default='0')
    suuid_ref     = Column(String(50))

# mp_software_task
class MpSoftwareTask(CommonBase):
    __tablename__ = 'mp_software_task'

    rid                 = Column(BigInteger, primary_key=True)
    tuuid               = Column(String(50), nullable=False)
    name                = Column(String(255), nullable=False)
    primary_suuid       = Column(String(50))
    active              = Column(Integer, server_default='0')
    sw_task_type        = Column(String(2), server_default='o')
    sw_task_privs       = Column(String(255), server_default='Global')
    sw_start_datetime   = Column(DateTime, server_default='1970-01-01 00:00:00')
    sw_end_datetime     = Column(DateTime, server_default='1970-01-01 00:00:00')
    mdate               = Column(DateTime, server_default='1970-01-01 00:00:00')
    cdate               = Column(DateTime, server_default='1970-01-01 00:00:00')

# mp_software_tasks_data
class MpSoftwareTasksData(CommonBase):
    __tablename__ = 'mp_software_tasks_data'

    rid         = Column(BigInteger, primary_key=True)
    gid         = Column(String(50), nullable=False)
    gDataHash   = Column(String(50), nullable=False)
    gData       = Column(LONGTEXT(), nullable=False)
    mdate       = Column(DateTime, server_default='1970-01-01 00:00:00')


# ------------------------------------------
## Plugins

# mp_agent_plugins
class MPPluginHash(CommonBase):
    __tablename__ = 'mp_agent_plugins'

    rid             = Column(BigInteger, primary_key=True)
    pluginName      = Column(String(255), nullable=False)
    pluginBundleID  = Column(String(100), nullable=False)
    pluginVersion   = Column(String(20), nullable=False)
    hash            = Column(String(100), nullable=False)
    active          = Column(Integer, server_default='0')


''' STOP - Tables for Web Services'''
# ------------------------------------------

# ------------------------------------------
## Console

class MPUser(CommonBase, UserMixin):
    rid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(255))

    def get_id(self):
        return unicode(self.rid)

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_username(username):
        return MPUser.query.filter_by(username=username).first()

    def __repr__(self):
        return "<User '{}'>".format(self.username)

# ------------------------------------------