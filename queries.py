import pyTigerGraph as tg
from datetime import datetime

from uuid import uuid4
rand_token = uuid4()


hostName = "https://candoor.i.tgcloud.io"
userName = "tigergraph"
password = "password"
conn = tg.TigerGraphConnection(host = hostName, username = userName, password = password)

conn.graphname = "candoor"
secret = conn.createSecret()
authToken = conn.getToken(secret)
authToken = authToken[0]

conn = tg.TigerGraphConnection(host=hostName, graphname="candoor", username=userName, password=password,
                               apiToken=authToken)



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
                "@speciality": el["attributes"]["@speciality"][0],
                "@has_aspiration": el["attributes"]["@has_aspiration"][0]["attributes"],
                "@score": el["attributes"]["@score"]}

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
                "@speciality": el["attributes"]["@speciality"][0],
                "@has_expertise": el["attributes"]["@has_expertise"][0]["attributes"],
                "@score": el["attributes"]["@score"]}

        mentorList.append(temp)

    return mentorList

def createNewUser(name, email, password, gender, country):
    # check if user exists in system
    checkUser = conn.runInstalledQuery("getperson_byemail", params={"email_para": email})

    if len(checkUser[0]["result"]) == 1:
        # user found
        return False
    else:
        maxid = conn.runInstalledQuery("getmaxpersonid")[0]["result"]
        conn.runInstalledQuery("createnewuser", params={"id_para": maxid + 1, "name_para": name, "email_para": email, "password_para": password, "gender_para": gender, "country_para": country})


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


def displaySettingsPage(personid):
    results = conn.runInstalledQuery("getSettingsPage_bypersonid", params={"personid_vertex": personid})

    email = results[0]["result"]["email"]
    gender = results[0]["result"]["gender"]
    location = results[0]["result"]["location"]

    settings_page_dict = {"email": email,
                          "gender": gender,
                          "location": location}
    return settings_page_dict

def update_userParticulars(personid, gender, location):
    params = {"personid_vertex": personid,
              "gender_para": gender,
              "location_para": location}
    results = conn.runInstalledQuery("update_userParticulars", params=params)

def updatepassword(personid, newpassword):
    params = {"personid_vertex": personid,
              "password_para": newpassword}
    results = conn.runInstalledQuery("update_password", params=params)


def update_profile(personid, name, profile_picture, profile_header, pronouns, profile_description, open_to_connect):
    params = {"personid_vertex": personid,
              "name_para": name,
              "profile_picture_para": profile_picture,
              "profile_header_para": profile_header,
              "pronouns_para": pronouns,
              "profile_description_para": profile_description,
              "open_to_connect_para": open_to_connect}
    results = conn.runInstalledQuery("update_profile", params=params)

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
    results = conn.runInstalledQuery("clean_speciality", params={"specialityarea_vertex": speciality})




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



def displayBlockList(personid):
    results = conn.runInstalledQuery("getBlockList", params={"personid_vertex": personid})

    blockList = []
    for person in results[0]["result"]:
        blockList.append({"name": person["attributes"]["name"], "id": person["attributes"]["id"]})

    return blockList


def block_person(personid, blockid):
    results = conn.runInstalledQuery("add_block", params={"personid_para": personid, "blockid_para": blockid})


def unblock_person(personid, blockid):
    results = conn.runInstalledQuery("delete_block", params={"personid_vertex": personid, "blockid_para": blockid})

def displayFriendList(personid):
    results = conn.runInstalledQuery("getFriendList", params={"personid_vertex": personid})

    friendList = []
    for person in results[0]["result"]:
        friendList.append({"name": person["attributes"]["name"], "id": person["attributes"]["id"]})

    return friendList

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



def getConnectionDegree(personid, otherpersonid):
    results = conn.runInstalledQuery("find_connectiondegree", params={"personid_para": personid, "otherpersonid_para": otherpersonid})

    return results[0]["@@connection"]


check = createNewUser("Audrey", "audrey@gmail.com", "password", "Female", "Singapore")
print(check)
profile_dict = displayProfilePage(1)
settings_dict = displaySettingsPage(1)
update_userParticulars(1, "NB", "Singapore")

update_profile(1, "Audrey", "audrey.jpg", "Candoor cofounder", "", "Validation engineer by day, tigergrapher at night.", True)
add_aspiration(1,"tigergraph",4,"want to master tg",1,True)
update_aspiration(1,"Machine Learning",1,"I'm interested to learn machine learning.",3,True)
delete_aspiration(1,"medicine",2)

add_expertise(1,"tigergraph gsql",2,"I have some expertise writing gsql tigergraph queries for the Million Dollar Hackathon.",1,True)
update_expertise(1,"GSQL (tigergraph)",2,"I have some expertise writing gsql tigergraph queries for the Million Dollar Hackathon.",1,True)
delete_expertise(1,"engineering",1)


updatepassword(1, "password2")
blockList = displayBlockList(2)
block_person(2, 3)
unblock_person(2, 3)

send_friendRequest(5, 1)
displayFriendRequests(1)
accept_friendRequest(1, 5)
displayFriendList(1)
delete_friend(1, 5)


sendMessage(2, 1, "hi", datetime.now())
sendMessage(1, 2, "Isn't candoor amazing??", datetime.now())
sendMessage(1, 2, "yes :)))", datetime.now())
displayChatList(1)
getMessages(1, 2)

getConnectionDegree(1,2)

find_mentees(1, "engineering", "I've done validation engineering for 5 years. Feel free to ask.", 4)
find_mentors(1, "machine learning", "I'm interested to learn machine learning.", 3)
