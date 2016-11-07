from flask import Flask
from flask_ldapconn import LDAPConn

app = Flask(__name__)
ldap = LDAPConn(app)

username = 'heizer1@llnl.gov'
password = ''
attribute = 'userPrincipalName'
search_filter = ('(active=1)')
basedn = "dc=llnl,dc-gov"

with app.app_context():
    retval = ldap.authenticate(username, password, attribute,
                               basedn, search_filter')
    if not retval:
        return 'Invalid credentials.'
    return 'Welcome %s.' % username