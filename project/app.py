from flask import Flask, render_template, request, redirect, url_for, flash
# from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, join_room
from markupsafe import escape
from models import User, db
# import db

# import TigerGraph
import pyTigerGraph as tg
# import TG functions
# from tg_functions import createNewUser

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
    results = conn.runInstalledQuery("getProfilePage_bypersonid", params={"id_para": personid})

    name = results[0]["result"][0]["attributes"]["name"]
    profile_picture = results[0]["result"][0]["attributes"]["profile_picture"]
    profile_header = results[0]["result"][0]["attributes"]["profile_header"]
    pronouns = results[0]["result"][0]["attributes"]["pronouns"]
    profile_description = results[0]["result"][0]["attributes"]["profile_description"]
    open_to_connect = results[0]["result"][0]["attributes"]["open_to_connect"]


    if "@expertise" in results[0]["result"][0]["attributes"]:
        expertiseList = results[0]["result"][0]["attributes"]["@expertise"]
        expertiseList = [expertise["attributes"] | {"speciality": expertise["to_id"]} for expertise in expertiseList]
        expertiseList = sorted(expertiseList, key = lambda dict: dict["num"])
        # each element in expertiseList has keys "num", "description", "proficiency_level", "willing_to_mentor", "speciality"
    else:
        expertiseList = []

    if "@aspiration" in results[0]["result"][0]["attributes"]:
        aspirationList = results[0]["result"][0]["attributes"]["@aspiration"]
        aspirationList = [aspiration["attributes"] | {"speciality": aspiration["to_id"]} for aspiration in aspirationList]
        aspirationList = sorted(aspirationList, key = lambda dict: dict["num"])
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
    results = conn.runInstalledQuery("clean_speciality", params={"specialityarea_vertex": speciality})


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

    nav_items = [
        {"nav_label": "About",
         "nav_link": "#"},
        {"nav_label": "Messages",
         "nav_link": "/chat_home"},
        {"nav_label": "Logout",
         "nav_link": "/logout"}
    ]

    # , tg_id=current_user.tg_id
    return render_template('my_profile.html', nav_items=nav_items, my_profile_dict=my_profile_dict, expertise_mapping=expertise_mapping)

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
    personid = current_user.tg_id
    # personid = 2
    speciality = request.form.get("expertise")
    num = request.form.get("expertiseNum")
    description = request.form.get("describeExpertise")
    proficiency_level = request.form.get("expertiseLevel")
    willing_to_mentor = True

    # Replace with code to write to TG
    update_expertise(personid, speciality, num, description, proficiency_level, willing_to_mentor)

    return redirect(url_for("my_profile"))

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
    add_expertise(personid, speciality, num, description, proficiency_level, willing_to_mentor)

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


# -------- VIEW OTHER USERS PROFILE ---------
@app.route('/profile/<int:user_id>')
@login_required
def others(user_id):
    user_id = f'{escape(user_id)}'
    profile_dict = displayProfilePage(user_id)

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
        {"nav_label": "Logout",
         "nav_link": "/logout"}
    ]

    # , tg_id=current_user.tg_id
    return render_template('others_profile.html', nav_items=nav_items,  profile_dict=profile_dict, expertise_mapping=expertise_mapping)


if __name__ == '__main__':
    socketio.run(app, debug=True)
