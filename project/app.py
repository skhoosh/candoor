import os
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
# from tg_functions import createNewUser

# create data for input into tg
import uuid
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

# -------- TG FUNCTIONS -----------


def createNewUser(name, email, password, gender, country):
    # check if user exists in system
    checkUser = conn.runInstalledQuery(
        "getperson_byemail", params={"email_para": email})

    if len(checkUser[0]["result"]) == 1:
        # user found
        return False
    else:
        maxid = conn.runInstalledQuery("getmaxpersonid")[0]["result"]
        conn.runInstalledQuery("createnewuser", params={"id_para": maxid + 1, "name_para": name,
                               "email_para": email, "password_para": password, "gender_para": gender, "country_para": country})


def displayProfilePage(personid):
    # personid needs to exist in database
    results = conn.runInstalledQuery(
        "getProfilePage_bypersonid", params={"id_para": personid})

    name = results[0]["result"][0]["attributes"]["name"]
    profile_picture = results[0]["result"][0]["attributes"]["profile_picture"]
    profile_header = results[0]["result"][0]["attributes"]["profile_header"]
    pronouns = results[0]["result"][0]["attributes"]["pronouns"]
    profile_description = results[0]["result"][0]["attributes"]["profile_description"]
    open_to_connect = results[0]["result"][0]["attributes"]["open_to_connect"]

    if "@expertise" in results[0]["result"][0]["attributes"]:
        expertiseList = results[0]["result"][0]["attributes"]["@expertise"]
        expertiseList = [expertise["attributes"] | {
            "speciality": expertise["to_id"]} for expertise in expertiseList]
        expertiseList = sorted(expertiseList, key=lambda dict: dict["num"])
        # each element in expertiseList has keys "num", "description", "proficiency_level", "willing_to_mentor", "speciality"
    else:
        expertiseList = []

    if "@aspiration" in results[0]["result"][0]["attributes"]:
        aspirationList = results[0]["result"][0]["attributes"]["@aspiration"]
        aspirationList = [aspiration["attributes"] | {
            "speciality": aspiration["to_id"]} for aspiration in aspirationList]
        aspirationList = sorted(aspirationList, key=lambda dict: dict["num"])
        # each element in aspirationList has keys "num", "description", "interest_level", "looking_for_mentor", "speciality"
    else:
        aspirationList = []

    profile_page_dict = {"name": name,
                         "profile_picture": profile_picture,
                         "profile_header": profile_header,
                         "pronouns": pronouns,
                         "profile_description": profile_description,
                         "open_to_connect": open_to_connect,
                         "expertiseList": expertiseList,
                         "aspirationList": aspirationList}

    return profile_page_dict


def add_expertise(personid, speciality, num, description, proficiency_level, willing_to_mentor):
    params = {"personid_para": personid,
              "speciality_para": speciality,
              "num_para": num,
              "description_para": description,
              "proficiency_level_para": proficiency_level,
              "willing_to_mentor_para": willing_to_mentor}
    results = conn.runInstalledQuery("add_expertise", params=params)


def update_expertise(personid, speciality, num, description, proficiency_level, willing_to_mentor):
    params = {"personid_vertex": personid,
              "speciality_para": speciality,
              "num_para": num,
              "description_para": description,
              "proficiency_level_para": proficiency_level,
              "willing_to_mentor_para": willing_to_mentor}
    results = conn.runInstalledQuery("update_expertise", params=params)


def delete_expertise(personid, speciality, num):
    params = {"personid_vertex": personid,
              "num_para": num}
    results = conn.runInstalledQuery("delete_expertise", params=params)
    results = conn.runInstalledQuery("reorder_expertise", params=params)
    results = conn.runInstalledQuery("clean_speciality", params={
                                     "specialityarea_vertex": speciality})


def add_aspiration(personid, speciality, num, description, interest_level, looking_for_mentor):
    params = {"personid_para": personid,
              "speciality_para": speciality,
              "num_para": num,
              "description_para": description,
              "interest_level_para": interest_level,
              "looking_for_mentor_para": looking_for_mentor}
    results = conn.runInstalledQuery("add_aspiration", params=params)


def update_aspiration(personid, speciality, num, description, interest_level, looking_for_mentor):
    params = {"personid_vertex": personid,
              "speciality_para": speciality,
              "num_para": num,
              "description_para": description,
              "interest_level_para": interest_level,
              "looking_for_mentor_para": looking_for_mentor}
    results = conn.runInstalledQuery("update_aspiration", params=params)


def delete_aspiration(personid, speciality, num):
    params = {"personid_vertex": personid,
              "num_para": num}
    results = conn.runInstalledQuery("delete_aspiration", params=params)
    results = conn.runInstalledQuery("reorder_aspiration", params=params)
    results = conn.runInstalledQuery("clean_speciality", params={
                                     "specialityarea_vertex": speciality})


def displayFriendList(personid):
    results = conn.runInstalledQuery("getFriendList", params={
                                     "personid_vertex": personid})

    friendList = []
    for person in results[0]["result"]:
        friendList.append(
            {"name": person["attributes"]["name"], "id": person["attributes"]["id"]})

    return friendList


def displayBlockList(personid):
    results = conn.runInstalledQuery(
        "getBlockList", params={"personid_vertex": personid})

    blockList = []
    for person in results[0]["result"]:
        blockList.append(
            {"name": person["attributes"]["name"], "id": person["attributes"]["id"]})

    return blockList


def displayChatList(personid):
    results = conn.runInstalledQuery("get_chat_list", params={"personid_vertex": personid})

    chatList = []
    for person in results[0]["result"]:
        chatList.append({"name": person["attributes"]["name"], "id": person["attributes"]["id"]})

    return chatList

def getMessages(personid, otherpersonid):
    results = conn.runInstalledQuery("show_messages", params={"personid_para": personid, "otherpersonid_para": otherpersonid})

    messageList = []
    for message in results[0]["result"]:
        messageList.append({"sender": message["attributes"]["@sender"][0], "text": message["attributes"]["text"], "time": message["attributes"]["time"]})

    return messageList

def sendMessage(personid, otherpersonid, text, time):
    results = conn.runInstalledQuery("send_a_message", params={"personid_para": personid, "otherpersonid_para": otherpersonid, "text_para": text, "time_para": str(time)})


def update_profile(personid, name, profile_picture, profile_header, pronouns, profile_description, open_to_connect):
    params = {"personid_vertex": personid,
              "name_para": name,
              "profile_picture_para": profile_picture,
              "profile_header_para": profile_header,
              "pronouns_para": pronouns,
              "profile_description_para": profile_description,
              "open_to_connect_para": open_to_connect}
    results = conn.runInstalledQuery("update_profile", params=params)

def find_mentees(personid, speciality, description, proficiency_level):
    # returns ordered by score mentee list
    # does not make use of description yet, but may in the future
    # each result has keys as listed in temp.
    # note that the key @has_aspiration is a dict with keys ["num", "description", "interest_level", "looking_for_mentor"]

    params = {"personid_para": personid,
              "speciality_para": speciality,
              "proficiency_level_para": proficiency_level}
    results = conn.runInstalledQuery("find_mentees", params=params)

    menteeList = []

    for el in results[0]["result"]:
        # return only relevent parameters (for example, we don't want to return the password)
        temp = {"id": el["attributes"]["id"],
                "name": el["attributes"]["name"],
                "email": el["attributes"]["email"],
                "profile_picture": el["attributes"]["profile_picture"],
                "profile_header": el["attributes"]["profile_header"],
                "pronouns": el["attributes"]["pronouns"],
                "profile_description": el["attributes"]["profile_description"],
                "open_to_connect": el["attributes"]["open_to_connect"],
                "speciality": el["attributes"]["@speciality"][0],
                "has_aspiration": el["attributes"]["@has_aspiration"][0]["attributes"],
                "score": el["attributes"]["@score"]}

        menteeList.append(temp)

    return menteeList

def find_mentors(personid, speciality, description, interest_level):
    # returns ordered by score mentor list
    # does not make use of description yet, but may in the future
    # each result has keys as listed in temp.
    # note that the key @has_expertise is a dict with keys ["num", "description", "proficiency_level", "willing_to_mentor"]

    params = {"personid_para": personid,
              "speciality_para": speciality,
              "interest_level_para": interest_level}
    results = conn.runInstalledQuery("find_mentors", params=params)

    mentorList = []

    for el in results[0]["result"]:
        # return only relevent parameters (for example, we don't want to return the password)
        temp = {"id": el["attributes"]["id"],
                "name": el["attributes"]["name"],
                "email": el["attributes"]["email"],
                "profile_picture": el["attributes"]["profile_picture"],
                "profile_header": el["attributes"]["profile_header"],
                "pronouns": el["attributes"]["pronouns"],
                "profile_description": el["attributes"]["profile_description"],
                "open_to_connect": el["attributes"]["open_to_connect"],
                "speciality": el["attributes"]["@speciality"][0],
                "has_expertise": el["attributes"]["@has_expertise"][0]["attributes"],
                "score": el["attributes"]["@score"]}

        mentorList.append(temp)

    return mentorList

def getConnectionDegree(personid, otherpersonid):
    results = conn.runInstalledQuery("find_connectiondegree", params={"personid_para": personid, "otherpersonid_para": otherpersonid})

    return results[0]["@@connection"]

def delete_friend(personid, friendid):
    results = conn.runInstalledQuery("delete_friend", params={"personid_vertex": personid, "friendid_para": friendid})


def displayFriendRequests(personid):
    results = conn.runInstalledQuery("show_friend_request", params={"personid_vertex": personid})

    friendRequestList = []
    for person in results[0]["result"]:
        friendRequestList.append({"name": person["attributes"]["name"], "id": person["attributes"]["id"]})

    return friendRequestList

def send_friendRequest(personid, friendid):
    results = conn.runInstalledQuery("send_friend_request", params={"personid_para": personid, "friendid_para": friendid})

def accept_friendRequest(personid, friendid):
    results = conn.runInstalledQuery("accept_friend_request", params={"personid_vertex": personid, "friendid_para": friendid})

def block_person(personid, blockid):
    results = conn.runInstalledQuery("add_block", params={"personid_para": personid, "blockid_para": blockid})

def unblock_person(personid, blockid):
    results = conn.runInstalledQuery("delete_block", params={"personid_vertex": personid, "blockid_para": blockid})


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
                    password=password)
    # add user to the sqlite database
    db.session.add(new_user)
    db.session.commit()

    # add user to tg database
    createNewUser(name, email, password, gender, country)
    # conn.upsertVertex('person', user_id, user_attributes)

    # print(req)
    return redirect(url_for('signup_success'))


@app.route('/signupsuccess')
def signup_success():
    return render_template('signup_success.html')


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

    # Call by User ID from TG
    user_id = current_user.tg_id
    my_profile_dict = displayProfilePage(user_id)

    expertise_mapping = {
        0: "Hobbyist",
        1: "Novice - Students or entry-level",
        2: "Intermediate - Some experience applying theory to practice",
        3: "Advanced - Professional and practical experience",
        4: "Expert - Field experts"
    }

    aspiration_mapping = {
        0: "Looking for a new hobby",
        1: "Student or entry-level skill building",
        2: "Looking for a potential career switch",
        3: "How can I build my career and be an expert at this?"
    }

    nav_items = [
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

    # , tg_id=current_user.tg_id
    return render_template('my_profile.html', nav_items=nav_items, my_profile_dict=my_profile_dict, expertise_mapping=expertise_mapping, aspiration_mapping=aspiration_mapping)

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
        profilePictureFilename = f"{personid}_pp.jpg"
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], profilePictureFilename)
        profilePicture.save(full_filename)
    else: 
        profilePictureFilename=request.form.get("hiddenProfilePicture")

    # Write to TG 
    update_profile(personid, displayName, profilePictureFilename, headline, pronouns, aboutme, True)

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
    add_aspiration(f"{personid}", f"{speciality}", num,
                   f"{description}", f"{interest_level}", f"{looking_for_mentor}")

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
    nav_items = [
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

    personid = current_user.tg_id
    speciality = request.form.get("expertise_speciality")
    description = request.form.get("expertise_description")
    proficiency_level = request.form.get("proficiency_level")

    mentees = find_mentees(personid, speciality, description, proficiency_level)
    mentees = [i for i in mentees if not (i["id"] == int(personid))]

    return render_template("mentees.html", mentees=mentees, speciality=speciality, nav_items=nav_items)

@app.route('/find_people_to_ask', methods=['POST'])
@login_required
def find_people_to_ask():
    nav_items = [
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

    personid = current_user.tg_id
    speciality = request.form.get("aspiration_speciality")
    description = request.form.get("aspiration_description")
    interest_level = request.form.get("aspiration_level")

    mentors = find_mentors(personid, speciality, description, interest_level)
    mentors = [i for i in mentors if not (i["id"] == int(personid))]


    return render_template("mentors.html", mentors=mentors, speciality=speciality, nav_items=nav_items)


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



# -------- CHAT ---------
@app.route('/chat_home')
@login_required
def chat_home():
    personid = current_user.tg_id
    # personid = 1
    # friends_list = [
    #     {"name": "Mary Jane Tan", "id":1},
    #     {"name": "John Teo", "id": 2},
    #     {"name": "Jane Brown", "id": 3}
    # ]
    friends_list = displayChatList(personid)
    name_map = {int(personid): current_user.name}

    for friend in friends_list:
        name_map[friend["id"]] = friend["name"]

    friend_id = request.args.get('friend_id')
    # room = request.args.get('room')
    if friend_id: 
        messages = getMessages(personid, friend_id)
    else:
        messages = []

    nav_items = [
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

    room = request.args.get('room')

    return render_template('chat_home_test.html', nav_items=nav_items, friends_list=friends_list, name_map=name_map, username=current_user.name, friend_id=friend_id, room=room, personid=personid, messages=messages)

@app.route('/add_chatlist', methods=['POST'])
@login_required
def add_chatlist():
    personid = current_user.tg_id
    friendid = request.form.get("friend_id")
    text = "Hello"
    sendMessage(personid, friendid, text, datetime.now())

    return redirect(url_for("chat_home"))





@socketio.on('send_message')
def handle_send_message_event(data):
    # Save message to TG 
    sendMessage(data["sender"], data["receiver"], data["message"], datetime.now())
    # Emit message to Client
    socketio.emit('receive_message', data, room=data['room'])


@socketio.on('join_room')
def handle_join_room_event(data):
    join_room(data["room"])
    socketio.emit('join_room_announcement', data)



# -------- VIEW OTHER USERS PROFILE ---------
@app.route('/profile/<int:user_id>')
@login_required
def others(user_id):
    user_id = f'{escape(user_id)}'
    profile_dict = displayProfilePage(user_id)
    personid = current_user.tg_id 
    connection_degree = getConnectionDegree(personid, user_id)

    expertise_mapping = {
        0: "Hobbyist",
        1: "Novice - Students or entry-level",
        2: "Intermediate - Some experience applying theory to practice",
        3: "Advanced - Professional and practical experience",
        4: "Expert - Field experts"
    }

    nav_items = [
        {"nav_label": "About",
         "nav_link": "#"},
        {"nav_label": "Messages",
         "nav_link": "/chat_home"},
        {"nav_label": "My Profile",
         "nav_link": "/my-profile"},
           {"nav_label": "Blocked",
         "nav_link": "/blocked"},
        {"nav_label": "Logout",
         "nav_link": "/logout"}
    ]

    # , tg_id=current_user.tg_id
    return render_template('others_profile.html', nav_items=nav_items,  profile_dict=profile_dict, expertise_mapping=expertise_mapping, connection_degree = connection_degree)

# -------- FRIENDS ---------
@app.route('/friends')
@login_required
def friends_list():
    personid = current_user.tg_id
    # personid = 1
    friend_list = displayFriendList(personid)
    friend_requests_all = displayFriendRequests(personid)
    blocked_list = displayBlockList(personid)


    # Get friend requests from only those pending
    friend_requests = [i for i in friend_requests_all if (i not in friend_list) and (i not in blocked_list)]

    friend_profiles = []
    for friend in friend_list:
        friend_profile = displayProfilePage(friend["id"])
        friend_profile["id"] = friend["id"]
        friend_profiles.append(friend_profile)

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

    return render_template('friends_list.html', nav_items=nav_items, friend_profiles=friend_profiles, friend_requests=friend_requests)

@app.route('/friend_request', methods=['POST'])
@login_required
def send_friend_request():
    personid = current_user.tg_id
    friendid = request.form.get("friend_id")
    send_friendRequest(personid, friendid)

    return redirect(url_for("friends_list"))

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
    nav_items = [
        {"nav_label": "Me",
         "nav_link": "/my-profile"},
        {"nav_label": "Messages",
         "nav_link": "/chat_home"},
        {"nav_label": "Friends",
         "nav_link": "/friends"},
        {"nav_label": "Logout",
         "nav_link": "/logout"}
    ]

    personid = current_user.tg_id
    # personid = 2
    blocked_list = displayBlockList(personid)

    blocked_profiles = []
    for blocked in blocked_list:
        blocked_profile = displayProfilePage(blocked["id"])
        blocked_profile["id"] = blocked["id"]
        blocked_profiles.append(blocked_profile)

    return render_template('blocked_list.html', blocked_profiles=blocked_profiles, nav_items=nav_items)

@app.route('/block_person', methods=['POST'])
@login_required
def block_person_01():
    personid = current_user.tg_id
    blockid = request.form.get("block_id")
    block_person(personid, blockid)
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
