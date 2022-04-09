import pyTigerGraph as tg

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


check = createNewUser("Audrey", "audrey@gmail.com", "password", "Female", "Singapore")
print(check)
profile_dict = displayProfilePage(1)

add_aspiration(1,"tigergraph",4,"want to master tg",1,True)
update_aspiration(1,"Machine Learning",1,"I'm interested to learn machine learning.",3,True)
delete_aspiration(1,"medicine",2)

add_expertise(1,"tigergraph gsql",2,"I have some expertise writing gsql tigergraph queries for the Million Dollar Hackathon.",1,True)
update_expertise(1,"GSQL (tigergraph)",2,"I have some expertise writing gsql tigergraph queries for the Million Dollar Hackathon.",1,True)
delete_expertise(1,"engineering",1)
