import os
import logging
basedir = os.path.abspath(os.path.dirname(__file__))

MP_ROOT_DIR = '/opt/MacPatch'
MP_SRV_DIR = MP_ROOT_DIR+'/Server'

class BaseConfig:
    
    DEBUG   = False
    TESTING = False
    BASEDIR = basedir

    # Web Server Options
    # Use 127.0.0.1 and port 3601, NGINX will be the outward facing
    # avenue for clients to communicate.
    SRV_HOST                        = '127.0.0.1'
    SRV_PORT                        = 5000

    # Database Options
    DB_USER                         = 'mpdbadm'
    DB_PASS                         = 'password'
    DB_HOST                         = 'localhost'
    DB_PORT                         = '3306'
    DB_NAME                         = 'MacPatchDB'
    SQLALCHEMY_DATABASE_URI         = 'mysql+mysqlconnector://'
    SQLALCHEMY_TRACK_MODIFICATIONS  = False
    SQLALCHEMY_POOL_SIZE            = 50
    SQLALCHEMY_POOL_TIMEOUT         = 20
    SQLALCHEMY_POOL_RECYCLE         = 170

    # App Options
    SECRET_KEY          = '~t\x86\xc9\x1ew\x8bOcX\x85O\xb6\xa2\x11kL\xd1\xce\x7f\x14<y\x9e'
    LOGGING_FORMAT      = '%(asctime)s [%(name)s][%(levelname).3s] --- %(message)s'
    LOGGING_LEVEL       = logging.INFO
    LOGGING_LOCATION    = '/opt/MacPatch/logs/mpconsole.log'

    # MacPatch App Options
    SITECONFIG_FILE     = MP_ROOT_DIR+'/etc/siteconfig.json'
    CONTENT_DIR         = MP_ROOT_DIR+'/Content'
    AGENT_CONTENT_DIR   = MP_ROOT_DIR+'/Content/Web/clients'
    PATCH_CONTENT_DIR   = MP_ROOT_DIR+'/Content/Web/patches'
    

"""
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://mpdbadm:Apple2e123@localhost:3306/MacPatchDB'
    #SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://mpdbadm:Apple2e123@dbmy2.llnl.gov:3306/MacPatchDB'
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 50
    SQLALCHEMY_POOL_TIMEOUT = 20
    SQLALCHEMY_POOL_RECYCLE = 170

    LDAP_HOST = 'adroot-1.empty-root.llnl.gov'  # Hostname of your LDAP Server
    LDAP_PORT = 3269
    LDAP_USE_SSL = True
    LDAP_BIND_DIRECT_CREDENTIALS = True
    LDAP_BASE_DN = 'dc=llnl,dc=gov'  # Base DN of your directory


class ProductionConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://mpdbadm:Apple2e123@localhost:3306/MacPatchDB'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 50
    SQLALCHEMY_POOL_TIMEOUT = 20
    SQLALCHEMY_POOL_RECYCLE = 170

"""

class DevelopmentConfig(BaseConfig):
    
    DEBUG                           = True
    LOGGING_LEVEL                   = logging.DEBUG
    DEBUG_TB_INTERCEPT_REDIRECTS    = False
    SQLALCHEMY_TRACK_MODIFICATIONS  = False


class ProductionConfig(BaseConfig):
    
    DEBUG                           = False
    LOGGING_LEVEL                   = logging.INFO

config = {
    "development": "mpapi.config.DevelopmentConfig",
    "prduction": "mpapi.config.ProductionConfig"
}