#!/usr/bin/env python

import os
import md5
from flask_script import Manager, Command, Option, Server
from flask_migrate import Migrate, MigrateCommand
from mpdb import addDefaultData
from mpapi.extensions import db
import hashlib
import multiprocessing

import warnings
from flask.exthook import ExtDeprecationWarning
warnings.simplefilter('ignore', ExtDeprecationWarning)

from mpapi import create_app
from mpapi.model import MPUser, AgentConfig, AgentConfigData, AdmUsers

# Create app -----------------------------------------------------------------
app = create_app()
manager = Manager(app)


# Gunicorn -------------------------------------------------------------------
class GunicornServer(Command):

	description = 'Run the app within Gunicorn'

	def __init__(self, host='127.0.0.1', port=int(os.environ.get("PORT", 3601)), workers=4, daemon=False):
		self.port = port
		self.host = host
		self.workers = workers
		self.daemon = daemon

	def get_options(self):
		return [
			Option('-h', '--host', dest='host', default=self.host),
			Option('-p', '--port', dest='port', type=int, default=self.port),
			Option('--workers', dest='workers', type=int, default=self.workers),
			Option('--daemon', dest='daemon', action='store_true'),
		]

	def run(self, *args, **kwargs):
		from gunicorn.app.base import Application
		host = kwargs['host']
		port = kwargs['port']
		#workers = kwargs['workers']
		workers = multiprocessing.cpu_count() + 1
		daemon = kwargs['daemon']

	    # Register blueprints
		# register_blueprints(app)

		print("Starting gunicorn server on %s:%d ...\n " % (host, port))
		class FlaskApplication(Application):
			def init(self, parser, opts, args):
				return {
					'bind': '{0}:{1}'.format(host, port),
					'workers': workers,
					'daemon': daemon,
					'worker_class': 'gevent',
					'worker_connections': 2000,
					'preload_app': True,
					'accesslog': '/opt/MacPatch/Server/logs/api_access.log',
					'errorlog': '/opt/MacPatch/Server/logs/api_error.log',
					'loglevel': 'info',
				}

			def load(self):
				return app

		FlaskApplication().run()

class Populate(Command):
    def run(self):
        print 'Add Default Data To Database'
		addDefaultData()
		print 'Default Data Added Database'

# DB Migrate -----------------------------------------------------------------
manager.add_command('db', MigrateCommand)
manager.add_command('db', Populate())

@manager.command
def init_db():
    db.create_all()
    db.session.commit()
    print 'Initialized the database'

@manager.command
def insert_data():
	_pass = hashlib.md5("*mpadmin*").hexdigest()
	db.session.add(AdmUsers(user_id="mpadmin", user_RealName="MPAdmin", user_pass=_pass, enabled='1'))
	db.session.commit()


@manager.command
def dropdb():
    if prompt_bool(
        "Are you sure you want to lose all your data"):
        db.drop_all()
        print 'Dropped the database'

@manager.command
def populateDB():
	print 'Add Default Data To Database'
	addDefaultData()
	print 'Default Data Added Database'



# Override default runserver with options from config.py
manager.add_command('runserver', Server(host=app.config['SRV_HOST'], port=app.config['SRV_PORT']) )

# Add gunicorn command to the manager
manager.add_command("gunicorn", GunicornServer())

if __name__ == '__main__':
	manager.run()
