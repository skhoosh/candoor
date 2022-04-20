import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))
from flask import Flask, render_template, request, redirect, url_for, flash
# from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, join_room
from markupsafe import escape
from models import User, db
from datetime import datetime
# import db

# import TigerGraph
import pyTigerGraph as tg
from tigergraph_settings import *
# import TG functions
from queries import *
# from tg_functions import createNewUser

# create data for input into tg
from datetime import date

# init SQLAlchemy so we can use it later in our models
# db = SQLAlchemy()
# Create two constant. They direct to the app root folder and logo upload folder
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'styles', 'img')

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

db.init_app(app)

# Connect to TigerGraph DB
conn = tg.TigerGraphConnection(
    host=hostName, username=userName, password=password)

# Connect to TigerGraph Graph
conn.graphname = "candoor"
secret = conn.createSecret()
authToken = conn.getToken(secret)
authToken = authToken[0]
conn = tg.TigerGraphConnection(host=hostName, graphname="candoor",
                               username=userName, password=password, apiToken=authToken)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


nav_items_authenticated = [
    {"nav_label": "Me",
     "nav_link": "/my-profile"},
    {"nav_label": "Messages",
     "nav_link": "/chat_home"},
    {"nav_label": "Friends",
     "nav_link": "/friends"},
    {"nav_label": "Blocked",
     "nav_link": "/blocked"},
    {"nav_label": "Logout",
     "nav_link": "/logout"}
]

expertise_mapping = {
    0: "Hobbyist - I do this for a hobby",
    1: "Novice - I'm a student or in an entry-level role",
    2: "Intermediate - I have some experience applying theory to practice",
    3: "Advanced - I'm a professional with practical experience",
    4: "Expert - I'm an expert, ask me anything"
}

aspiration_mapping = {
    0: "Hobbyist - I'm looking for a new hobby",
    1: "Novice - I interested in studying this or learn more about it",
    2: "Intermediate - Looking to see if I can begin a career or side-hustle in this",
    3: "Advanced - I want to advance professionally in this",
    4: "Expert - I want to be an expert at this"
}


def toOrdinalNum(n):
    return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(4 if 10 <= n % 100 < 20 else n % 10, "th")


# -------- MAIN APP ---------
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('my_profile'))
    else:
        return redirect(url_for("login"))


# -------- AUTHENTICATION ---------
@app.route('/login')
def login():
    nav_items = [
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
    nav_items = [
        {"nav_label": "Login",
         "nav_link": "/login"}
    ]
    return render_template('signup.html', nav_items=nav_items)


@app.route('/signup', methods=['POST'])
def signup_post():

    tg_max_id = conn.getVertexCount("person")
    user_id = f"{tg_max_id + 1}"
    name = request.form.get('name')
    email = request.form.get('email')
    password = generate_password_hash(
        request.form.get('password'), method='sha256')
    gender = request.form.get('gender')
    country = request.form.get('country')
    created_date = date.today().strftime("%Y-%m-%d")

    # user_attributes = {
    #     "username": name,
    #     "email": email,
    #     "date_created": created_date
    # }

    # check if user exists
    user = User.query.filter_by(email=email).first()

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return(redirect(url_for('signup')))

    # add user to tg database
    createNewUser(name, email, password, gender, country)
    # conn.upsertVertex('person', user_id, user_attributes)

    # add user to sqlite database
    # create a new user with form data. Hash password.
    new_user = User(tg_id=user_id, email=email, name=name,
                    password=password)
    # add user to the sqlite database
    db.session.add(new_user)
    db.session.commit()

    # print(req)
    return redirect(url_for('signup_success'))


@app.route('/signupsuccess')
def signup_success():
    nav_items = [
        {"nav_label": "Login",
         "nav_link": "/login"},
        {"nav_label": "Sign Up",
            "nav_link": "/signup"}
    ]
    return render_template('signup_success.html', nav_items=nav_items)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# -------- My PROFILE ---------
@app.route('/my-profile')
@login_required
def my_profile():

    # Call by User ID from TG
    user_id = current_user.tg_id
    my_profile_dict = displayProfilePage(user_id)

    # , tg_id=current_user.tg_id
    return render_template('my_profile.html',
                           nav_items=nav_items_authenticated,
                           my_profile_dict=my_profile_dict,
                           expertise_mapping=expertise_mapping,
                           aspiration_mapping=aspiration_mapping)

# -------- EDIT MY PROFILE --------


@app.route('/edit_about_me', methods=['POST'])
@login_required
def edit_about_me():
    displayName = request.form.get("displayName")
    headline = request.form.get("headline")
    pronouns = request.form.get("pronouns")
    aboutme = request.form.get("aboutme")
    personid = current_user.tg_id
    if request.files["profilePicture"]:
        profilePicture = request.files["profilePicture"]
        profilePictureFilename = f"User{personid}.jpg"
        full_filename = os.path.join(
            app.config['UPLOAD_FOLDER'], profilePictureFilename)
        profilePicture.save(full_filename)
    else:
        profilePictureFilename = request.form.get("hiddenProfilePicture")

    # Write to TG
    update_profile(personid, displayName, profilePictureFilename,
                   headline, pronouns, aboutme, True)

    return redirect(url_for("my_profile"))


# -------- EDIT ASK ME --------
@app.route('/add_ask_me_about', methods=['POST'])
@login_required
def add_ask_me():
    personid = current_user.tg_id
    # personid = 2
    speciality = request.form.get("expertise")
    num = request.form.get("expertiseNum")
    description = request.form.get("describeExpertise")
    proficiency_level = request.form.get("expertiseLevel")
    willing_to_mentor = True

    # Replace with code to write to TG
    add_expertise(personid, speciality, num, description,
                  proficiency_level, willing_to_mentor)

    return redirect(url_for("my_profile"))


@app.route('/edit_ask_me_about', methods=['POST'])
@login_required
def edit_ask_me():
    personid = current_user.tg_id
    # personid = 2
    speciality = request.form.get("expertise")
    num = request.form.get("expertiseNum")
    description = request.form.get("describeExpertise")
    proficiency_level = request.form.get("expertiseLevel")
    willing_to_mentor = True

    # Replace with code to write to TG
    update_expertise(personid, speciality, num, description,
                     proficiency_level, willing_to_mentor)

    return redirect(url_for("my_profile"))


@app.route('/delete_ask_me', methods=['POST'])
@login_required
def delete_ask_me():
    personid = current_user.tg_id
    # personid = 2
    speciality = request.form.get("expertise")
    num = request.form.get("expertiseNum")

    # Replace with code to write to TG
    delete_expertise(personid, speciality, num)

    return redirect(url_for("my_profile"))


# -------- EDIT TELL ME --------
@app.route('/add_tell_me_about', methods=['POST'])
@login_required
def add_tell_me():
    personid = current_user.tg_id
    # personid = 2
    speciality = request.form.get("aspiration")
    num = request.form.get("aspirationNum")
    description = request.form.get("describeAspiration")
    interest_level = request.form.get("aspirationLevel")
    looking_for_mentor = True

    # Replace with code to write to TG
    add_aspiration(personid, speciality, num,
                   description, interest_level, looking_for_mentor)

    return redirect(url_for("my_profile"))


@app.route('/edit_tell_me_about', methods=['POST'])
@login_required
def edit_tell_me():
    personid = current_user.tg_id
    # personid = 2
    speciality = request.form.get("aspiration")
    num = request.form.get("aspirationNum")
    description = request.form.get("describeAspiration")
    interest_level = request.form.get("aspirationLevel")
    looking_for_mentor = True

    # Replace with code to write to TG
    update_aspiration(personid, speciality, num, description,
                      interest_level, looking_for_mentor)

    return redirect(url_for("my_profile"))


@app.route('/delete_tell_me', methods=['POST'])
@login_required
def delete_tell_me():
    personid = current_user.tg_id
    # personid = 2
    speciality = request.form.get("aspiration")
    num = request.form.get("aspirationNum")

    # Replace with code to write to TG
    delete_aspiration(personid, speciality, num)

    return redirect(url_for("my_profile"))

# -------- FIND PEOPLE RESULTS ---------


@app.route('/find_people_to_tell', methods=['POST'])
@login_required
def find_people_to_tell():
    personid = current_user.tg_id
    speciality = request.form.get("expertise_speciality")
    description = request.form.get("expertise_description")
    proficiency_level = request.form.get("proficiency_level")

    mentees = find_mentees(personid, speciality,
                           description, proficiency_level)
    mentees = [i for i in mentees if not (i["id"] == int(personid))]

    return render_template("mentees.html", mentees=mentees, speciality=speciality, nav_items=nav_items_authenticated)


@app.route('/find_people_to_ask', methods=['POST'])
@login_required
def find_people_to_ask():

    personid = current_user.tg_id
    speciality = request.form.get("aspiration_speciality")
    description = request.form.get("aspiration_description")
    interest_level = request.form.get("aspiration_level")

    mentors = find_mentors(personid, speciality, description, interest_level)
    mentors = [i for i in mentors if not (i["id"] == int(personid))]

    return render_template("mentors.html", mentors=mentors, speciality=speciality, nav_items=nav_items_authenticated)


# -------- CHAT ---------
@app.route('/chat_home')
@login_required
def chat_home():
    personid = current_user.tg_id
    friends_list = displayChatList(personid)
    name_map = {int(personid): current_user.name}

    for friend in friends_list:
        name_map[friend["id"]] = friend["name"]

    friend_id = request.args.get('friend_id')

    if friend_id:
        messages = getMessages(personid, friend_id)
    else:
        messages = []

    room = request.args.get('room')

    return render_template('chat.html', nav_items=nav_items_authenticated, friends_list=friends_list, name_map=name_map, username=current_user.name, friend_id=friend_id, room=room, personid=personid, messages=messages)

# SEND MESSAGE HEREEEE


@app.route('/add_chatlist', methods=['POST'])
@login_required
def add_chatlist():
    personid = current_user.tg_id
    friendid = request.form.get("friend_id")
    text = request.form.get("messageText")
    if (int(personid) > int(friendid)):
        room_id = f'{friendid}_to_{personid}'
    else:
        room_id = f'{personid}__to_{friendid}'

    sendMessage(personid, friendid, text, datetime.now())

    return redirect(url_for("chat_home", room=room_id, friend_id=friendid))


@socketio.on('send_message')
def handle_send_message_event(data):
    # Save message to TG
    sendMessage(data["sender"], data["receiver"],
                data["message"], datetime.now())

    if (int(data["sender"]) > int(data["receiver"])):
        room_id = f'{data["receiver"]}_to_{data["sender"]}'
    else:
        room_id = f'{data["sender"]}_to_{data["receiver"]}'
    # Emit message to Client
    socketio.emit('receive_message', data, room=room_id)


@socketio.on('join_room')
def handle_join_room_event(data):
    print(data["sender"])
    if (data["sender"]):
        if (int(data["sender"]) > int(data["receiver"])):
            room_id = f'{data["receiver"]}_to_{data["sender"]}'
        else:
            room_id = f'{data["sender"]}_to_{data["receiver"]}'
    # join_room(data["room"])
    join_room(room_id)
    socketio.emit('join_room_announcement', data)


# -------- VIEW OTHER USERS PROFILE ---------
@app.route('/profile/<int:user_id>')
@login_required
def others(user_id):
    user_id = f'{escape(user_id)}'
    profile_dict = displayProfilePage(user_id)
    personid = current_user.tg_id
    connection_degree = getConnectionDegree(personid, user_id)
    connection_degree_ordinal = toOrdinalNum(connection_degree)

    received_friend_requests = displayFriendRequests(personid)
    received_ids = [i["id"] for i in received_friend_requests]
    if int(user_id) in received_ids:
        received = "True"
    else:
        received = "False"

    sent_friend_requests = displaySentFriendRequests(personid)
    sent_ids = [i["id"] for i in sent_friend_requests]
    if int(user_id) in sent_ids:
        sent = "True"
    else:
        sent = "False"

    # , tg_id=current_user.tg_id
    return render_template('others_profile.html',
                           user_id=user_id,
                           nav_items=nav_items_authenticated,
                           profile_dict=profile_dict,
                           expertise_mapping=expertise_mapping,
                           aspiration_mapping=aspiration_mapping,
                           connection_degree=connection_degree,
                           connection_degree_ordinal=connection_degree_ordinal,
                           received=received,
                           sent=sent)

# -------- FRIENDS ---------


@app.route('/friends')
@login_required
def friends_list():
    personid = current_user.tg_id
    # personid = 1
    friend_list = displayFriendList(personid)
    friend_requests_all = displayFriendRequests(personid)
    blocked_list = displayBlockList(personid)
    sent_friend_requests = displaySentFriendRequests(personid)

    # Get friend requests from only those pending
    friend_requests = [i for i in friend_requests_all if (
        i not in friend_list) and (i not in blocked_list)]
    sent_friend_requests = [i for i in sent_friend_requests if (
        i not in blocked_list)]

    friend_profiles = []
    for friend in friend_list:
        friend_profile = displayProfilePage(friend["id"])
        friend_profile["id"] = friend["id"]
        friend_profiles.append(friend_profile)

    return render_template('friends_list.html', nav_items=nav_items_authenticated, friend_profiles=friend_profiles, friend_requests=friend_requests, sent_friend_requests=sent_friend_requests)


@app.route('/friend_request', methods=['POST'])
@login_required
def send_friend_request():
    personid = current_user.tg_id
    friendid = request.form.get("friend_id")
    send_friendRequest(personid, friendid)

    return '<script>document.location.href = document.referrer</script>'

    # return redirect(url_for("friends_list"))


@app.route('/accept_friend', methods=['POST'])
@login_required
def accept_friend_request():
    personid = current_user.tg_id
    friendid = request.form.get("friend_id")
    accept_friendRequest(personid, friendid)

    return redirect(url_for("friends_list"))


@app.route('/delete_friend', methods=['POST'])
@login_required
def delete_friend_from_list():
    personid = current_user.tg_id
    friendid = request.form.get("delete_id")
    delete_friend(personid, friendid)

    return redirect(url_for("friends_list"))


# -------- BLOCKED ---------
@app.route('/blocked')
@login_required
def blocked_list():
    personid = current_user.tg_id
    # personid = 2
    blocked_list = displayBlockList(personid)

    blocked_profiles = []
    for blocked in blocked_list:
        blocked_profile = displayProfilePage(blocked["id"])
        blocked_profile["id"] = blocked["id"]
        blocked_profiles.append(blocked_profile)

    return render_template('blocked_list.html', blocked_profiles=blocked_profiles, nav_items=nav_items_authenticated)


@app.route('/block_person', methods=['POST'])
@login_required
def block_person_01():
    personid = current_user.tg_id
    blockid = request.form.get("block_id")
    block_person(personid, blockid)
    delete_friend(personid, blockid)

    return redirect(url_for("blocked_list"))


@app.route('/unblock_person', methods=['POST'])
@login_required
def unblock_person_01():
    personid = current_user.tg_id
    blockid = request.form.get("unblock_id")
    unblock_person(personid, blockid)
    return redirect(url_for("blocked_list"))


if __name__ == '__main__':
    socketio.run(app, debug=True)
