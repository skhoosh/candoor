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


# a = displayProfilePage(2)
print(displayProfilePage("1"))
# print(displayProfilePage("2"))

# a = conn.getVertices("person", select="name,email,pronouns", where="id=6", limit="", sort="", timeout=0)

# print(a)

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