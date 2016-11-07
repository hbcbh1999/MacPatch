from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user

from ldap3 import Server, Connection, ALL, AUTO_BIND_NO_TLS, SUBTREE, ALL_ATTRIBUTES
import ldap3

from . import auth
from .. import db
from ..models import MPUser, User, AdmUsers
from .forms import LoginForm

from flask_ldap3_login.forms import LDAPLoginForm


@auth.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        user = AdmUsers.query.filter(AdmUsers.user_id == form.username.data ).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash("Logged in successfully as {}.".format(user.username))
            return redirect(request.args.get('next') or url_for('bookmarks.user', username=user.username))
        else:
            userID = form.username.data + "@llnl.gov"
            server = Server(host='adroot-1.empty-root.llnl.gov', port=3269, use_ssl=True)
            conn = Connection(server, user=userID, password=form.password.data, authentication=ldap3.AUTH_SIMPLE)

            if conn.bind():
                conn.search(search_base='DC=llnl,DC=gov',
                            search_filter='(&(objectClass=*)(userPrincipalName=userID))',
                            search_scope=SUBTREE, attributes=ALL_ATTRIBUTES, get_operational_attributes=True)
                print conn.response_to_json()
                if user is None:
                    user = AdmUsers()
                    user.user_id = form.username.data
                    user.user_pass = "NA"
                    db.session.add(user)
                    db.session.commit()

                login_user(user, form.remember_me.data)
                return redirect(url_for('dashboard.index', username=user.user_id))

        #flash('Incorrect username or password.')
    return render_template("login.html", form=form)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))

'''
@auth.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password = form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Welcome, {}! Please login.'.format(user.username))
        return redirect(url_for('.login'))
    return render_template("signup.html", form=form)
'''