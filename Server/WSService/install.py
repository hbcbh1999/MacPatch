import pip
import zipfile
import os

_pre_ = [
    "pip",
    "setuptools"
]

_all_ = [
    "alembic>=0.7.7",
    "aniso8601>=1.1.0",
    "Flask>=0.10.1",
    "Flask-Cache>=0.13.1",
    "Flask-Login>=0.3.2",
    "Flask-Migrate>=1.8.0",
    "Flask-RESTful>=0.3.5",
    "flask-restful-swagger>=0.19",
    "Flask-Script>=2.0.5",
    "Flask-SQLAlchemy>=2.1",
    "gunicorn>=19.4.5",
    "itsdangerous>=0.24",
    "Jinja2>=2.8",
    "Mako>=1.0.4",
    "MarkupSafe>=0.23",
    "python-dateutil>=2.5.3",
    "pytz>=2016.4",
    "six>=1.10.0",
    "SQLAlchemy>=1.0.12",
    "Werkzeug>=0.11.9",
    "ldap3>=1.4.0",
    "gevent>=1.1.2",
]

MP_HOME     = "/opt/MacPatch"
MP_SRV_BASE = MP_HOME+"/Server"

srcDir      = MP_SRV_BASE+"/WSService/_src_"
mysqlZIP    = "_src_/mysql-connector-python-2.1.3.zip"
mysqlPKG    = "_src_/mysql-connector-python-2.1.3"
cryptoPKG   = MP_SRV_BASE+"/WSService/_src_/M2Crypto-0.21.1-py2.7-macosx-10.8-intel.egg"

linux = ["M2Crypto>=0.24.0","mysql-connector-python-rf>=2.1.3"]
darwin = ["mysql-connector-python-rf>=2.1.3",]

def easyInstall(package):
    if os.path.exists(package):
        os.system("easy_install " + package)

def installAlt(package):
    # Debugging
    # pip.main(["install", "--pre", "--upgrade", "--no-index",
    #         "--find-links=.", package, "--log-file", "log.txt", "-vv"])
    pip.main(["install", "--no-cache-dir", "--no-index", "--find-links=.", package])

def upgrade(packages):
    for package in packages:
        pip.main(['install', "--egg", "--no-cache-dir", "--upgrade", "--trusted-host", "pypi.python.org", package])

def install(packages):
    for package in packages:
        pip.main(['install', "--egg", "--no-cache-dir", "--trusted-host", "pypi.python.org", package])

if __name__ == '__main__':

    from sys import platform

    upgrade(_pre_) 
    install(_all_) 
    
    if platform.startswith('linux'):
        install(linux)

    if platform.startswith('darwin'): # MacOS
        install(darwin)
        easyInstall(cryptoPKG)


