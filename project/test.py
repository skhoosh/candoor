import pyTigerGraph as tg

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

# tg_max_id = conn.getVertexCount("person")
# print(tg_max_id)

def displayBlockList(personid):
    results = conn.runInstalledQuery("getBlockList", params={"personid_vertex": personid})

    blockList = []
    for person in results[0]["result"]:
        blockList.append({"name": person["attributes"]["name"], "id": person["attributes"]["id"]})

    return blockList

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

# a = displayProfilePage(2)
# print(displayProfilePage("1"))
# print(displayProfilePage("2"))

# print(displayBlockList(4))

# print(find_mentees(1, "engineering", "I've done validation engineering for 5 years. Feel free to ask.", 4))

# a = conn.getVertices("person", select="name,email,pronouns", where="id=6", limit="", sort="", timeout=0)

# print(a)

def displayFriendList(personid):
    results = conn.runInstalledQuery("getFriendList", params={"personid_vertex": personid})

    friendList = []
    for person in results[0]["result"]:
        friendList.append({"name": person["attributes"]["name"], "id": person["attributes"]["id"]})

    return friendList


# print(displayFriendList(2))

# b= conn.gsql('select name,email from person where id==6')
# print(b)
a = {'name': 'Stephanie Bot', 
    'profile_picture': 'user2.jpg', 
    'profile_header': 'GIS specialist', 
    'pronouns': 'she/her', 
    'profile_description': 'My background is in GIS and computing, looking to switch careers.', 
    'open_to_connect': True, 
    'expertiseList': [
        {'num': 1, 
        'description': "I'm pretty good at python.", 
        'proficiency_level': 4, 
        'willing_to_mentor': False, 
        'speciality': 'computer science'}, 
        {'num': 2, 
        'description': 'I use ML and GIS at work.', 
        'proficiency_level': 3, 
        'willing_to_mentor': True, 
        'speciality': 'machine learning'}
        ], 
    'aspirationList': [
        {'num': 0, 'description': '', 
        'interest_level': 0, 
        'looking_for_mentor': True, 
        'speciality': 'civil engineering'}, 
        {'num': 1, 
        'description': 'I like to do art for fun.', 
        'interest_level': 2, 
        'looking_for_mentor': False, 
        'speciality': 'art'}]
        }

def getMessages(personid, otherpersonid):
    results = conn.runInstalledQuery("show_messages", params={"personid_para": personid, "otherpersonid_para": otherpersonid})

    messageList = []
    for message in results[0]["result"]:
        messageList.append({"sender": message["attributes"]["@sender"][0], "text": message["attributes"]["text"], "time": message["attributes"]["time"]})

    return messageList

print(getMessages(1,2))


b =[{'sender': 1, 'text': "Hi Stephanie, I'm interested to learn more about machine learning. Is it ok if you could give me some pointers on where to start? Thanks.", 'time': '2022-03-27 09:26:03'}, 
{'sender': 2, 'text': 'hi', 'time': '2022-04-15 02:28:52'}, 
{'sender': 1, 'text': "Isn't candoor amazing??", 'time': '2022-04-15 02:28:53'}, 
{'sender': 1, 'text': 'yes :)))', 'time': '2022-04-15 02:28:53'}]

def displayChatList(personid):
    results = conn.runInstalledQuery("get_chat_list", params={"personid_vertex": personid})

    chatList = []
    for person in results[0]["result"]:
        chatList.append({"name": person["attributes"]["name"], "id": person["attributes"]["id"]})

    return chatList

# print(displayChatList(1))

c = [{'name': 'Stephanie Bot', 'id': 2},{'name': 'Stephanie Bot', 'id': 3}, {'name': 'Stephanie Bot', 'id': 6} ]