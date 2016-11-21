from flask import render_template, jsonify, request
from datetime import *
import json
import base64
import re
import collections
from datetime import datetime
import uuid

from . import osmanage
from .. import login_manager
from .. model import *
from .. import db

@osmanage.route('/profiles')
def profiles():

    return render_template('patch_groups.html', data={}, columns={})