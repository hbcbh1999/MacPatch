from flask import render_template, jsonify, request
from datetime import *
import json
import base64
import re
import collections
from datetime import datetime
import uuid

from . import reports
from .. import login_manager
from ..models import ApplePatch
from .. import db

@reports.route('/new')
def new():

    return render_template('patch_groups.html', data={}, columns={})
