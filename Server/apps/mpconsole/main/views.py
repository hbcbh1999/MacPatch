from flask import render_template
from flask_login import login_required, current_user

from . import main
from .. import login_manager
#from ..models import User, Bookmark, Tag
from ..models import MPUser, MpClient, User, AdmUsers


@login_manager.user_loader
def load_user(userid):
    return AdmUsers.query.get(int(userid))


@main.route('/')
@login_required
def index():
    print "Base"
    return render_template('index.html')

@main.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

'''
@main.app_context_processor
def inject_tags():
    return dict(all_tags=Tag.all)
'''