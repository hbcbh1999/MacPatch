import pip
import zipfile
import os

_pre_ = [
    "pip",
    "setuptools"
]

_all_ = [
    "alembic==0.8.7",
    "aniso8601==1.1.0",
    "blinker==1.4",
    "click==6.6",
    "enum34==1.1.6",
    "Flask==0.11.1",
    "Flask-DebugToolbar==0.10.0",
    "Flask-Cache==0.13.1",
    "flask-ldap3-login==0.9.12",
    "Flask-Login==0.3.2",
    "Flask-Migrate==1.8.1",
    "Flask-RESTful==0.3.5",
    "flask-restful-swagger==0.19",
    "Flask-Script==2.0.5",
    "Flask-SQLAlchemy==2.1",
    "Flask-WTF==0.13.1",
    "gevent==1.1.2",
    "greenlet==0.4.10",
    "gunicorn==19.6.0",
    "healthcheck==1.3.1",
    "itsdangerous==0.24",
    "Jinja2==2.8",
    "ldap3==2.1.0",
    "Mako==1.0.4",
    "MarkupSafe==0.23",
    "pyasn1==0.1.9",
    "python-dateutil==2.5.3",
    "python-editor==1.0.1",
    "pytz==2016.6.1",
    "six==1.10.0",
    "uWSGI==2.0.14",
    "Werkzeug==0.11.11",
    "WTForms==2.1",
]

MP_HOME     = "/opt/MacPatch"
MP_SRV_BASE = MP_HOME+"/Server"

srcDir      = MP_SRV_BASE+"/apps/_src_"
cryptoPKG   = srcDir+"/M2Crypto-0.21.1-py2.7-macosx-10.8-intel.egg"

linux = ["M2Crypto>=0.24.0","mysql-connector-python-rf>=2.1.3"]
darwin = ["mysql-connector-python-rf>=2.1.3",]

def easyInstall(package):
    if os.path.exists(package):
        os.system("easy_install " + package)

def installAlt(package):
    # Debugging
    # pip.main(["install", "--pre", "--upgrade", "--no-index",
    #         "--find-links=.", package, "--log-file", "log.txt", "-vv"])
    pip.main(["install", "--quiet", "--no-cache-dir", "--no-index", "--find-links=.", package])

def upgrade(packages):
    for package in packages:
        pip.main(['install', "--quiet", "--egg", "--no-cache-dir", "--upgrade", "--trusted-host", "pypi.python.org", package])

def install(packages):
    for package in packages:
        print("Installing Python Module: " + package)
        res = pip.main(['install', "--quiet", "--egg", "--no-cache-dir", "--trusted-host", "pypi.python.org", package])
        if res != 0:
            print("Error installing " + package + ". Please verify env.")

if __name__ == '__main__':

    from sys import platform

    upgrade(_pre_) 
    install(_all_) 
    
    if platform.startswith('linux'):
        install(linux)

    if platform.startswith('darwin'): # MacOS
        install(darwin)
        easyInstall(cryptoPKG)


