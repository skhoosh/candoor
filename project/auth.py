from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db

# import TigerGraph
import pyTigerGraph as tg

# create data for input into tg
import uuid
from datetime import date

auth = Blueprint('auth', __name__)

# Connect to TigerGraph DB
hostName = "https://candoor01.i.tgcloud.io/"
userName = "tigergraph"
password = "password"
conn = tg.TigerGraphConnection(host=hostName, username=userName, password=password)

# Connect to TigerGraph Graph
conn.graphname="test_login"
secret = conn.createSecret()
authToken = conn.getToken(secret)
authToken = authToken[0]
conn = tg.TigerGraphConnection(host=hostName, graphname="test_login", username=userName, password=password, apiToken=authToken)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    # login code 
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    # check if user exists
    user = User.query.filter_by(email=email).first()
    # take user-supplied password and hash it 
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():

    user_id = f"{uuid.uuid4()}"
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    created_date = date.today().strftime("%Y-%m-%d")

    user_attributes = {
        "username": name,
        "email": email,
        "date_created": created_date
    }

    # check if user exists
    user = User.query.filter_by(email=email).first()

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return(redirect(url_for('auth.signup')))

    # create a new user with form data. Hash password. 
    new_user = User(tg_id=user_id, email=email, name=name, password=generate_password_hash(password, method='sha256'))
    # add user to the sqlite database 
    db.session.add(new_user)
    db.session.commit()

    # add user to tg database
    conn.upsertVertex('person', user_id, user_attributes)

    # print(req)
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))