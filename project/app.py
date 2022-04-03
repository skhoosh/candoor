from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, join_room
from models import User, db
# import db

# import TigerGraph
import pyTigerGraph as tg

# create data for input into tg
import uuid
from datetime import date

# init SQLAlchemy so we can use it later in our models
# db = SQLAlchemy()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

db.init_app(app)

# Connect to TigerGraph DB
hostName = "https://candoor01.i.tgcloud.io/"
userName = "tigergraph"
password = "password"
conn = tg.TigerGraphConnection(
    host=hostName, username=userName, password=password)

# Connect to TigerGraph Graph
conn.graphname = "test_login"
secret = conn.createSecret()
authToken = conn.getToken(secret)
authToken = authToken[0]
conn = tg.TigerGraphConnection(host=hostName, graphname="test_login",
                               username=userName, password=password, apiToken=authToken)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------- AUTHENTICATION ---------


@app.route('/login')
def login():
    nav_items = [
        {"nav_label": "About",
         "nav_link": "#"},
        {"nav_label": "Sign Up",
         "nav_link": "/signup"}
    ]
    return render_template('login.html', nav_items=nav_items)


@app.route('/login', methods=['POST'])
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
        return redirect(url_for('login'))

    login_user(user, remember=remember)
    return redirect(url_for('my_profile'))


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
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

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return(redirect(url_for('signup')))

    # create a new user with form data. Hash password.
    new_user = User(tg_id=user_id, email=email, name=name,
                    password=generate_password_hash(password, method='sha256'))
    # add user to the sqlite database
    db.session.add(new_user)
    db.session.commit()

    # add user to tg database
    conn.upsertVertex('person', user_id, user_attributes)

    # print(req)
    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# -------- MAIN APP ---------
@app.route('/')
def index():
    nav_items = [
        {"nav_label": "About",
         "nav_link": "#"},
        {"nav_label": "Messages",
         "nav_link": "/chat_home"},
        {"nav_label": "My Profile",
         "nav_link": "/my-profile"},
        {"nav_label": "Logout",
         "nav_link": "/logout"}
    ]
    return render_template('index.html', nav_items=nav_items)


# -------- My PROFILE ---------
@app.route('/my-profile')
@login_required
def my_profile():
    # Replace with code to call from TG
    about_me_dict = {
        "name": "abc",
        "headline": "Artist | Scientist | Musician",
        "about_me": "Some description about myself goes here. I like to paint, draw and illustrate with Python. My favourte YouTube videos are about fish. It's a special interest of mine."
    }

    ask_me_dict = [
        # {
        #     "skill": "Watercolour",
        #     "note": "I do watercolouring for my job. I like to paint landscape and fish",
        #     "level": "Ask me anything! I'm an expert"
        # },
        #     {
        #     "skill": "Python",
        #     "note": "I have been coding for 1 year. I like python because it's cool. ",
        #     "level": "Ask me about my learning journey"
        # },
        #     {
        #     "skill": "Fish",
        #     "note": "Fish keeping has been a passion and hobby of mine since I was a child. We used to go to Qian Hu fish farm a lot to look at the fish.",
        #     "level": "Ask me about my hobby"
        # }
    ]

    tell_me_dict = [{
        "skill": "Chickens",
        "note": "I would love to rear chickens one day. If you have an advice, let's chat",
        "level": "I'm curious about the hobby"
    },
        {
        "skill": "Skydiving",
        "note": "I'm a thrill seeker! Would love to skydive. Anyone care to share about their experiences?  ",
        "level": "I'm looking for an experience"
    },
        {
        "skill": "Yoga",
        "note": "I've been doing yoga for close to 8 years now. I practice around 3 times per week. I'm curious about taking this further and potentially becoming a teacher.",
        "level": "Looking for a potential career switch"
    }]

    nav_items = [
        {"nav_label": "About",
         "nav_link": "#"},
        {"nav_label": "Messages",
         "nav_link": "/chat_home"},
        {"nav_label": "Logout",
         "nav_link": "/logout"}
    ]

    # , tg_id=current_user.tg_id
    return render_template('my_profile.html', nav_items=nav_items, name=current_user.name, about_me_dict=about_me_dict, ask_me_dict=ask_me_dict, tell_me_dict=tell_me_dict)

# -------- EDIT MY PROFILE --------
@app.route('/edit_about_me', methods=['POST'])
@login_required
def edit_about_me():
    displayName = request.form.get("displayName")
    headline = request.form.get("headline")
    aboutme = request.form.get("aboutme")

    about_me = {
        "displayName": displayName,
        "headline": headline,
        "aboutme": aboutme
    }

    # Replace with code to write to TG
    with open("edit_about_me.txt", "a") as f:
        f.write(str(about_me)+"\n")
    
    return redirect(url_for("my_profile"))

@app.route('/edit_ask_me_about', methods=['POST'])
@login_required
def edit_ask_me():
    expertise = request.form.get("expertise")
    describeExpertise = request.form.get("describeExpertise")
    expertiseLevel = request.form.get("expertiseLevel")

    ask_me = {
        "expertise": expertise,
        "describeExpertise": describeExpertise,
        "expertiseLevel": expertiseLevel
    }

    # Replace with code to write to TG
    with open("edit_ask_me.txt", "a") as f:
        f.write(str(ask_me)+"\n")
    
    return redirect(url_for("my_profile"))

@app.route('/edit_tell_me_about', methods=['POST'])
@login_required
def edit_tell_me():
    aspiration = request.form.get("aspiration")
    describeAspiration = request.form.get("describeAspiration")
    aspirationLevel = request.form.get("aspirationLevel")

    tell_me = {
        "aspiration": aspiration,
        "describeAspiration": describeAspiration,
        "aspirationLevel": aspirationLevel
    }

    # Replace with code to write to TG
    with open("edit_tell_me.txt", "a") as f:
        f.write(str(tell_me)+"\n")
    
    return redirect(url_for("my_profile"))


# -------- CHAT ---------
@app.route('/chat_home')
@login_required
def chat_home():
    friends_list = [
        {"name": "Mary Jane Tan"},
        {"name": "John Teo"},
        {"name": "Jane Brown"}
    ]

    nav_items = [
        {"nav_label": "About",
         "nav_link": "#"},
        {"nav_label": "Messages",
         "nav_link": "/chat_home"},
        {"nav_label": "Logout",
         "nav_link": "/logout"}
    ]

    return render_template('chat_home_test.html', nav_items=nav_items, friends_list=friends_list, username=current_user.name)


@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')

    if username and room:
        return render_template('chat.html', username=username, room=room)
    else:
        return redirect(url_for('chat_home'))


@socketio.on('send_message')
def handle_send_message_event(data):
    socketio.emit('receive_message', data, room=data['room'])


@socketio.on('join_room')
def handle_join_room_event(data):
    join_room(data["room"])
    socketio.emit('join_room_announcement', data)


# -------- FIND PEOPLE RESULTS ---------
@app.route('/find_people')
@login_required
def find_people():
    people_list = [
        {
            "name": "Eva Bot",
            "headline": "I'm a cute doggo",
            "about_me": "I'm a cute and clever doggo. I like to play soccer and balls make me go crazyyyy."
        },
        {
            "name": "Clover Bot",
            "headline": "13/10 good doge",
            "about_me": "I'm cute and fluffy. But I can be quite fierce sometimes. Don't cross me. "
        },
    ]

    return render_template('find_people.html', people_list=people_list)


# -------- VIEW OTHERS PROFILE ---------
@app.route('/others')
@login_required
def others():
    about_me_dict = {
        "name": "Cat Bot",
        "headline": "Am CAT",
        "about_me": "Specialising in knocking things over. You may pet me. But not like that."
    }

    ask_me_dict = [
        # {
        #     "skill": "Watercolour",
        #     "note": "I do watercolouring for my job. I like to paint landscape and fish",
        #     "level": "Ask me anything! I'm an expert"
        # },
        #     {
        #     "skill": "Python",
        #     "note": "I have been coding for 1 year. I like python because it's cool. ",
        #     "level": "Ask me about my learning journey"
        # },
        #     {
        #     "skill": "Fish",
        #     "note": "Fish keeping has been a passion and hobby of mine since I was a child. We used to go to Qian Hu fish farm a lot to look at the fish.",
        #     "level": "Ask me about my hobby"
        # }
    ]

    tell_me_dict = [{
        "skill": "Chickens",
        "note": "I would love to rear chickens one day. If you have an advice, let's chat",
        "level": "I'm curious about the hobby"
    },
        {
        "skill": "Skydiving",
        "note": "I'm a thrill seeker! Would love to skydive. Anyone care to share about their experiences?  ",
        "level": "I'm looking for an experience"
    },
        {
        "skill": "Yoga",
        "note": "I've been doing yoga for close to 8 years now. I practice around 3 times per week. I'm curious about taking this further and potentially becoming a teacher.",
        "level": "Looking for a potential career switch"
    }]

    nav_items = [
        {"nav_label": "About",
         "nav_link": "#"},
        {"nav_label": "Messages",
         "nav_link": "/chat_home"},
        {"nav_label": "My Profile",
         "nav_link": "/my-profile"},
        {"nav_label": "Logout",
         "nav_link": "/logout"}
    ]

    # , tg_id=current_user.tg_id
    return render_template('others_profile.html', nav_items=nav_items,  about_me_dict=about_me_dict, ask_me_dict=ask_me_dict, tell_me_dict=tell_me_dict)


if __name__ == '__main__':
    socketio.run(app, debug=True)
