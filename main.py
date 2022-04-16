from tigergraph_settings import *
import pyTigerGraph as tg
import time

startTime = time.time()

conn = tg.TigerGraphConnection(host = hostName, username = userName, password = password)

def getgraphconnection(conn, hostName, userName, password, graphName):
    conn.graphname = graphName
    secret = conn.createSecret()
    authToken = conn.getToken(secret)
    authToken = authToken[0]

    conn = tg.TigerGraphConnection(host=hostName, graphname="candoor", username=userName, password=password,
                                   apiToken=authToken)

    return conn


clearAll = True
createGlobalSchema = True
createGraph = True
connectToGraph = True
loadGraph = True
dropQueries = True
installQueries = True

if clearAll:
    results = conn.gsql("USE GLOBAL DROP ALL")
    print(results)

if createGlobalSchema:
    # create global schema
    globalSchema_gsql = '''
    USE GLOBAL
    CREATE VERTEX person (PRIMARY_ID id INT, name STRING, email STRING, password STRING, profile_picture STRING, profile_header STRING DEFAULT "default_profile_pic.jpg", pronouns STRING, profile_description STRING, open_to_connect BOOL DEFAULT "true", auth_token STRING) WITH primary_id_as_attribute="true"
    CREATE VERTEX gender (PRIMARY_ID gender_identity STRING) WITH primary_id_as_attribute="true"
    CREATE VERTEX location (PRIMARY_ID country STRING) WITH primary_id_as_attribute="true"
    CREATE VERTEX speciality (PRIMARY_ID area STRING) WITH primary_id_as_attribute="true"
    CREATE VERTEX message (PRIMARY_ID id STRING, text STRING, time DATETIME)
    CREATE UNDIRECTED EDGE has_gender (From person, To gender)
    CREATE UNDIRECTED EDGE located_at (From person, To location)
    CREATE UNDIRECTED EDGE has_aspiration (From person, To speciality, num INT, description STRING, interest_level int, looking_for_mentor BOOL DEFAULT "true")
    CREATE UNDIRECTED EDGE has_expertise (From person, To speciality, num INT, description STRING, proficiency_level int, willing_to_mentor BOOL DEFAULT "true")
    CREATE DIRECTED EDGE send_message (From person, To message) WITH REVERSE_EDGE="reverse_send_message"
    CREATE DIRECTED EDGE receive_message (From message, To person) WITH REVERSE_EDGE="reverse_receive_message"
    CREATE UNDIRECTED EDGE friend (From person, To person)
    CREATE DIRECTED EDGE friend_request (From person, To person) WITH REVERSE_EDGE="reverse_friend_request"
    CREATE DIRECTED EDGE block (From person, To person) WITH REVERSE_EDGE="reverse_block"
    '''

    results = conn.gsql(globalSchema_gsql)
    print(results)

if createGraph:
    creategraph_gsql = "CREATE GRAPH candoor (person, gender, location, speciality, message, has_gender, located_at, has_aspiration, has_expertise, send_message, receive_message, friend, friend_request, block)"
    results = conn.gsql(creategraph_gsql)
    print(results)

if connectToGraph:
    conn = getgraphconnection(conn, hostName, userName, password, "candoor")

if loadGraph:
    # create loading jobs
    loadingJobs_gsql = '''
      USE GRAPH candoor
      BEGIN
      CREATE LOADING JOB load_userFile FOR GRAPH candoor {
      DEFINE FILENAME myfile;
      LOAD myfile TO VERTEX person VALUES ($0, $1, $2, $3, $4, $5, $6, $7, $8, $9) USING SEPARATOR=",", EOL="\\n", QUOTE="double";
      LOAD myfile TO VERTEX gender VALUES ($10) USING SEPARATOR=",", EOL="\\n", QUOTE="double";
      LOAD myfile TO EDGE has_gender VALUES ($0, $10) USING SEPARATOR=",", EOL="\\n", QUOTE="double";
      LOAD myfile TO VERTEX location VALUES ($11) USING SEPARATOR=",", EOL="\\n", QUOTE="double";
      LOAD myfile TO EDGE located_at VALUES ($0, $11) USING SEPARATOR=",", EOL="\\n", QUOTE="double";
      }
      CREATE LOADING JOB load_specialityFile FOR GRAPH candoor {
      DEFINE FILENAME myfile;
      LOAD myfile TO VERTEX speciality VALUES ($0) USING SEPARATOR=",", EOL="\\n", QUOTE="double";
      }
      CREATE LOADING JOB load_aspirationFile FOR GRAPH candoor {
      DEFINE FILENAME myfile;
      LOAD myfile TO EDGE has_aspiration VALUES ($0, $1, $2, $3, $4, $5) USING SEPARATOR=",", EOL="\\n", QUOTE="double";
      }
      CREATE LOADING JOB load_expertiseFile FOR GRAPH candoor {
      DEFINE FILENAME myfile;
      LOAD myfile TO EDGE has_expertise VALUES ($0, $1, $2, $3, $4, $5) USING SEPARATOR=",", EOL="\\n", QUOTE="double";
      }
      CREATE LOADING JOB load_messageFile FOR GRAPH candoor {
      DEFINE FILENAME myfile;
      LOAD myfile TO VERTEX message VALUES ($0, $3, $4) USING SEPARATOR=",", EOL="\\n", QUOTE="double";
      LOAD myfile TO EDGE send_message VALUES ($1, $0) USING SEPARATOR=",", EOL="\\n", QUOTE="double";
      LOAD myfile TO EDGE receive_message VALUES ($0, $2) USING SEPARATOR=",", EOL="\\n", QUOTE="double";
      }
      CREATE LOADING JOB load_friendFile FOR GRAPH candoor {
      DEFINE FILENAME myfile;
      LOAD myfile TO EDGE friend VALUES ($0, $1) USING SEPARATOR=",", EOL="\\n", QUOTE="double";
      }
      CREATE LOADING JOB load_friendRequestFile FOR GRAPH candoor {
      DEFINE FILENAME myfile;
      LOAD myfile TO EDGE friend_request VALUES ($0, $1) USING SEPARATOR=",", EOL="\\n", QUOTE="double";
      }
      CREATE LOADING JOB load_blockFile FOR GRAPH candoor {
      DEFINE FILENAME myfile;
      LOAD myfile TO EDGE block VALUES ($0, $1) USING SEPARATOR=",", EOL="\\n", QUOTE="double";
      }
      END

    '''
    results = conn.gsql(loadingJobs_gsql)
    print(results)

    file = "Data/user.csv"
    results = conn.uploadFile(file, fileTag="myfile", jobName="load_userFile")
    print(results)

    file = "Data/speciality.csv"
    results = conn.uploadFile(file, fileTag="myfile", jobName="load_specialityFile")
    print(results)

    file = "Data/aspiration.csv"
    results = conn.uploadFile(file, fileTag="myfile", jobName="load_aspirationFile")
    print(results)

    file = "Data/expertise.csv"
    results = conn.uploadFile(file, fileTag="myfile", jobName="load_expertiseFile")
    print(results)

    file = "Data/message.csv"
    results = conn.uploadFile(file, fileTag="myfile", jobName="load_messageFile")
    print(results)

    file = "Data/friend.csv"
    results = conn.uploadFile(file, fileTag="myfile", jobName="load_friendFile")
    print(results)

    file = "Data/friendRequest.csv"
    results = conn.uploadFile(file, fileTag="myfile", jobName="load_friendRequestFile")
    print(results)

    file = "Data/block.csv"
    results = conn.uploadFile(file, fileTag="myfile", jobName="load_blockFile")
    print(results)

if dropQueries:
    result = conn.gsql("DROP QUERY ALL")
    print(result)

if installQueries:
    queries_gsql = '''
    USE GRAPH candoor
    CREATE QUERY getperson_byemail(STRING email_para) FOR GRAPH candoor {
        start = {person.*};
        result = SELECT s FROM start:s WHERE s.email == email_para;
        PRINT result;
    }
    INSTALL QUERY getperson_byemail

    CREATE QUERY getmaxpersonid() FOR GRAPH candoor {
        MaxAccum<INT> @@maxpersonid;
        start = {person.*};
        result = SELECT s FROM start:s
            ACCUM
                @@maxpersonid += s.id;
        PRINT @@maxpersonid AS result;
    }
    INSTALL QUERY getmaxpersonid

    CREATE QUERY createnewuser(INT id_para, STRING name_para, STRING email_para, STRING password_para, STRING gender_para, STRING country_para) FOR GRAPH candoor {
        # create new person vertex
        INSERT INTO person (PRIMARY_ID, name, email, password) VALUES (id_para, name_para, email_para, password_para);

        start = {gender.*};
        result = SELECT s FROM start:s WHERE s.gender_identity == gender_para;
        IF result.size() == 1 THEN
            # create new gender vertex if it doesn't exist
            INSERT INTO gender (PRIMARY_ID) VALUES (gender_para);
        END;
        INSERT INTO has_gender (FROM, TO) VALUES (id_para person, gender_para gender);

        start2 = {location.*};
        result2 = SELECT s FROM start2:s WHERE s.country == country_para;
        IF result2.size() == 1 THEN
            # create new location vertex if it doesn't exist
            INSERT INTO location (PRIMARY_ID) VALUES (country_para);
        END;
        INSERT INTO located_at (FROM, TO) VALUES (id_para person, country_para location);       
    }
    INSTALL QUERY createnewuser
    
    CREATE QUERY getProfilePage_bypersonid(INT id_para) FOR GRAPH candoor {
        ListAccum<Edge<has_aspiration>> @aspiration;
        ListAccum<Edge<has_expertise>> @expertise;
        SumAccum<INT> @@sp_count = 0;
        
        start = {person.*};
        result = SELECT s FROM start:s - (:e) - speciality:sp
            WHERE s.id == id_para

            ACCUM
                @@sp_count += 1,
                IF e.type == "has_aspiration" THEN
                    s.@aspiration += e
                ELSE IF e.type == "has_expertise" THEN
                    s.@expertise += e
                END;

        IF @@sp_count == 0 THEN
            result2 = SELECT s FROM start:s WHERE s.id == id_para;
            PRINT result2 AS result;
        ELSE
            PRINT result;
        END;
    }
    INSTALL QUERY getProfilePage_bypersonid
    
    CREATE QUERY update_profile(Vertex<person> personid_vertex, STRING name_para, STRING profile_picture_para, STRING profile_header_para, STRING pronouns_para, STRING profile_description_para, BOOL open_to_connect_para) FOR GRAPH candoor {
        start = {personid_vertex};
        UPDATE s FROM start:s
            SET
                s.name = name_para,
                s.profile_picture = profile_picture_para,
                s.profile_header = profile_header_para,
                s.pronouns = pronouns_para,
                s.profile_description = profile_description_para,
                s.open_to_connect = open_to_connect_para;

    }
    INSTALL QUERY update_profile
    
    CREATE QUERY add_aspiration(INT personid_para, STRING speciality_para, INT num_para, STRING description_para, INT interest_level_para, BOOL looking_for_mentor_para) FOR GRAPH candoor {
        # add a new has_aspiration edge and add/update speciality vertex
        INSERT INTO speciality (PRIMARY_ID) VALUES (speciality_para);
        INSERT INTO has_aspiration (FROM, TO, num, description, interest_level, looking_for_mentor) VALUES (personid_para person, speciality_para speciality, num_para, description_para, interest_level_para, looking_for_mentor_para);
    }
    INSTALL QUERY add_aspiration
    
    CREATE QUERY update_aspiration(Vertex<person> personid_vertex, STRING speciality_para, INT num_para, STRING description_para, INT interest_level_para, BOOL looking_for_mentor_para) FOR GRAPH candoor {
        # update has_aspiration edge and add/update speciality vertex
        
        start = {personid_vertex};        
        result = SELECT sp FROM start:s - (has_aspiration:e) - speciality:sp
            WHERE e.num == num_para
            
            ACCUM
                DELETE (e);
                INSERT INTO speciality (PRIMARY_ID) VALUES (speciality_para);
                INSERT INTO has_aspiration (FROM, TO, num, description, interest_level, looking_for_mentor) VALUES (personid_vertex, speciality_para speciality, num_para, description_para, interest_level_para, looking_for_mentor_para);

        SumAccum<INT> @@sp_edge_count;

        # delete speciality vertex if this person is the only one using the vertex
        result2 = SELECT s FROM result:s - (:e) - person:p
            ACCUM
                @@sp_edge_count += 1
            
            POST-ACCUM
                IF @@sp_edge_count == 1 THEN
                    DELETE (s)
                END;
    }
    INSTALL QUERY update_aspiration
    
    CREATE QUERY delete_aspiration(Vertex<person> personid_vertex, INT num_para) FOR GRAPH candoor {
        start = {personid_vertex};
        DELETE e FROM start:s - (has_aspiration:e) - speciality:sp
            WHERE e.num == num_para;
    }
    INSTALL QUERY delete_aspiration
    
    CREATE QUERY reorder_aspiration(Vertex<person> personid_vertex, INT num_para) FOR GRAPH candoor {
        start = {personid_vertex};

        result = SELECT s FROM start:s - (has_aspiration:e) - speciality:sp
            ACCUM
                IF e.num > num_para THEN
                    e.num = e.num - 1
                END;
    }
    INSTALL QUERY reorder_aspiration 

    CREATE QUERY clean_speciality(Vertex<speciality> specialityarea_vertex) FOR GRAPH candoor {
        # delete speciality vertex if no longer in use

        SumAccum<INT> @@sp_edge_count;

        start = {specialityarea_vertex};
        result = SELECT s FROM start:s - (:e) - person:p
            ACCUM
                @@sp_edge_count += 1

            POST-ACCUM
                IF @@sp_edge_count == 1 THEN
                    DELETE (s)
                END;
    }
    INSTALL QUERY clean_speciality

    CREATE QUERY add_expertise(INT personid_para, STRING speciality_para, INT num_para, STRING description_para, INT proficiency_level_para, BOOL willing_to_mentor_para) FOR GRAPH candoor {
        # add a new has_expertise edge and add/update speciality vertex
        INSERT INTO speciality (PRIMARY_ID) VALUES (speciality_para);
        INSERT INTO has_expertise (FROM, TO, num, description, proficiency_level, willing_to_mentor) VALUES (personid_para person, speciality_para speciality, num_para, description_para, proficiency_level_para, willing_to_mentor_para);
    }
    INSTALL QUERY add_expertise
    
    CREATE QUERY update_expertise(Vertex<person> personid_vertex, STRING speciality_para, INT num_para, STRING description_para, INT proficiency_level_para, BOOL willing_to_mentor_para) FOR GRAPH candoor {
        # update has_expertise edge and add/update speciality vertex
        
        start = {personid_vertex};
        result = SELECT sp FROM start:s - (has_expertise:e) - speciality:sp
            WHERE e.num == num_para
            
            ACCUM
                DELETE (e);
                INSERT INTO speciality (PRIMARY_ID) VALUES (speciality_para);
                INSERT INTO has_expertise (FROM, TO, num, description, proficiency_level, willing_to_mentor) VALUES (personid_vertex, speciality_para speciality, num_para, description_para, proficiency_level_para, willing_to_mentor_para);

        SumAccum<INT> @@sp_edge_count;

        # delete speciality vertex if this person is the only one using the vertex
        result2 = SELECT s FROM result:s - (:e) - person:p
            ACCUM
                @@sp_edge_count += 1
            
            POST-ACCUM
                IF @@sp_edge_count == 1 THEN
                    DELETE (s)
                END;
    }
    INSTALL QUERY update_expertise
    
    CREATE QUERY delete_expertise(Vertex<person> personid_vertex, INT num_para) FOR GRAPH candoor {
        start = {personid_vertex};          
        DELETE e FROM start:s - (has_expertise:e) - speciality:sp
            WHERE e.num == num_para;
    }
    INSTALL QUERY delete_expertise
    
    CREATE QUERY reorder_expertise(Vertex<person> personid_vertex, INT num_para) FOR GRAPH candoor {
        start = {personid_vertex};
        result = SELECT s FROM start:s - (has_expertise:e) - speciality:sp
            ACCUM
                IF e.num > num_para THEN
                    e.num = e.num - 1
                END;
    }
    INSTALL QUERY reorder_expertise
        
    CREATE QUERY getSettingsPage_bypersonid(Vertex<person> personid_vertex) FOR GRAPH candoor {
        MapAccum<STRING, STRING> @@settingsPage;
        
        start = {personid_vertex};
        result = SELECT s FROM start:s - ((located_at|has_gender):e) - (location|gender):v

            ACCUM
                IF v.type == "location" THEN
                    @@settingsPage += ("location" -> v.country)
                ELSE IF v.type == "gender" THEN
                    @@settingsPage += ("gender" -> v.gender_identity)
                END
                
            POST-ACCUM
                @@settingsPage += ("email" -> s.email);

        PRINT @@settingsPage AS result;
    }
    INSTALL QUERY getSettingsPage_bypersonid
    
    CREATE QUERY update_userParticulars(Vertex<person> personid_vertex, STRING gender_para, STRING location_para) FOR GRAPH candoor {

        start = {personid_vertex};
        result = SELECT s FROM start:s - ((located_at|has_gender):e) - (location|gender):v

            ACCUM
                DELETE (e)
            
            POST-ACCUM (s)
                INSERT INTO location (PRIMARY_ID) VALUES (location_para);
                INSERT INTO located_at (FROM, TO) VALUES (personid_vertex, location_para location);
                INSERT INTO gender (PRIMARY_ID) VALUES (gender_para);
                INSERT INTO has_gender (FROM, TO) VALUES (personid_vertex, gender_para gender);

    }
    INSTALL QUERY update_userParticulars

    CREATE QUERY update_password(Vertex<person> personid_vertex, STRING password_para) FOR GRAPH candoor {
        start = {personid_vertex};
        UPDATE s FROM start:s
        SET
            s.password = password_para;
    }
    INSTALL QUERY update_password

    CREATE QUERY getBlockList(Vertex<person> personid_vertex) FOR GRAPH candoor {
        start = {personid_vertex};
        result = SELECT b FROM start:s - (block:e) -> person:b
            ORDER BY
                b.name;
        PRINT result;
    }
    INSTALL QUERY getBlockList

    CREATE QUERY add_block(INT personid_para, INT blockid_para) FOR GRAPH candoor {
        INSERT INTO block (FROM, TO) VALUES (personid_para person, blockid_para person);
    }
    INSTALL QUERY add_block

    CREATE QUERY delete_block(Vertex<person> personid_vertex, INT blockid_para) FOR GRAPH candoor {
        start = {personid_vertex};
        result = SELECT b FROM start:s - (block:e) -> person:b
            WHERE b.id == blockid_para
            
            ACCUM
                DELETE (e);
    }
    INSTALL QUERY delete_block

    CREATE QUERY getFriendList(Vertex<person> personid_vertex) FOR GRAPH candoor {
        start = {personid_vertex};
        result = SELECT f FROM start:s - (friend:e) - person:f
            ORDER BY
                f.name;
        PRINT result;
    }
    INSTALL QUERY getFriendList

    CREATE QUERY delete_friend(Vertex<person> personid_vertex, INT friendid_para) FOR GRAPH candoor {
        start = {personid_vertex};
        result = SELECT f FROM start:s - (friend:e) - person:f
            WHERE f.id == friendid_para
            
            ACCUM
                DELETE (e);                
    }
    INSTALL QUERY delete_friend

    CREATE QUERY show_friend_request(Vertex<person> personid_vertex) FOR GRAPH candoor {
        start = {personid_vertex};
        result = SELECT f FROM start:s - (reverse_friend_request:e) -> person:f
            ORDER BY
                f.name;
        PRINT result;
    }
    INSTALL QUERY show_friend_request
    
    CREATE QUERY show_sent_friend_request(Vertex<person> personid_vertex) FOR GRAPH candoor {
        start = {personid_vertex};
        result = SELECT f FROM start:s - (friend_request:e) -> person:f
            ORDER BY
                f.name;
        PRINT result;
    }
    INSTALL QUERY show_sent_friend_request

    CREATE QUERY send_friend_request(INT personid_para, INT friendid_para) FOR GRAPH candoor {
        INSERT INTO friend_request (FROM, TO) VALUES (personid_para person, friendid_para person);
    }
    INSTALL QUERY send_friend_request

    CREATE QUERY accept_friend_request(Vertex<person> personid_vertex, INT friendid_para) FOR GRAPH candoor {
        INSERT INTO friend (FROM, TO) VALUES (personid_vertex, friendid_para person);
        start = {personid_vertex};
        result = SELECT f FROM start:s - (friend_request:e) - person:f
            WHERE f.id == friendid_para
            
            ACCUM
                DELETE (e);
    }
    INSTALL QUERY accept_friend_request
    
    CREATE QUERY show_messages(INT personid_para, INT otherpersonid_para) FOR GRAPH candoor {
        SetAccum<INT> @sender;
        
        start = {person.*};
        result = SELECT m FROM start:s - (_>:e1) - message:m - (_>:e2) - person:p
            WHERE 
                s.id == personid_para AND
                p.id == otherpersonid_para
            
            ACCUM
                IF e1.type == "send_message" THEN
                    m.@sender = s.id
                ELSE
                    m.@sender = otherpersonid_para
                END
            
            ORDER BY m.time;  

        PRINT result;
    }
    INSTALL QUERY show_messages
    
    CREATE QUERY get_chat_list(Vertex<person> personid_vertex) FOR GRAPH candoor {
        start = {personid_vertex};
        result = SELECT p FROM start:s - ((send_message>|reverse_receive_message>):e1) - message:m - ((receive_message>|reverse_send_message>):e2) - person:p
            WHERE p.id != s.id
            ORDER BY p.name;  

        PRINT result;
    }
    INSTALL QUERY get_chat_list

    CREATE QUERY send_a_message(INT personid_para, INT otherpersonid_para, STRING text_para, STRING time_para) FOR GRAPH candoor {
        STRING uniqueMessageId = "p" + to_string(personid_para) + " p" + to_string(otherpersonid_para) + " " + time_para;
        INSERT INTO message (PRIMARY_ID, text, time) VALUES (uniqueMessageId, text_para, to_datetime(time_para));
        INSERT INTO send_message (FROM, TO) VALUES (personid_para person, uniqueMessageId message);
        INSERT INTO receive_message (FROM, TO) VALUES (uniqueMessageId message, otherpersonid_para person);
    }
    INSTALL QUERY send_a_message
    
    CREATE QUERY find_connectiondegree(INT personid_para, INT otherpersonid_para) FOR GRAPH candoor RETURNS (INT) {
        MinAccum<INT> @@connection = 4;

        start = {person.*};
        result1 = SELECT s FROM start:s - (friend:e) - person:p
            WHERE
                s.id == personid_para AND
                p.id == otherpersonid_para

            ACCUM
                @@connection += 1;

        result2 = SELECT s FROM start:s - (friend:e) - person:p - (friend:e2) - person:p2
            WHERE
                s.id == personid_para AND
                p2.id == otherpersonid_para

            ACCUM
                @@connection += 2;
                
        result3 = SELECT s FROM start:s - (friend:e) - person:p - (friend:e2) - person:p2 - (friend:e3) - person:p3
            WHERE
                s.id == personid_para AND
                p2.id != personid_para AND
                p3.id == otherpersonid_para

            ACCUM
                @@connection += 3;

        PRINT @@connection;
        RETURN @@connection;     
    }
    INSTALL QUERY find_connectiondegree

    CREATE QUERY find_twoway_blockdegreeremovedscore(INT personid_para, INT otherpersonid_para) FOR GRAPH candoor RETURNS (INT) {
        # does not check 1st degree two way block as 1st degree blocks should/will be removed completely from interaction
        # a block of 0 is the best. The higher the block score the worse the person will be ranked
        # can consider scoring reverse_block differently from block in the future to not penalise reverse_block as much

        MaxAccum<INT> @@twowayblockdegree = 0;

        start = {person.*};
        result1 = SELECT s FROM start:s - (friend:e) - person:p - ((block>|reverse_block>):b) - person:p2
            WHERE
                s.id == personid_para AND
                p2.id == otherpersonid_para

            ACCUM
                @@twowayblockdegree += 5;

        result2 = SELECT s FROM start:s - (friend:e) - person:p - (friend:e) - person:p2 - ((block>|reverse_block>):b) - person:p3
            WHERE
                s.id == personid_para AND
                p2.id != personid_para AND
                p3.id == otherpersonid_para

            ACCUM
                @@twowayblockdegree += 2;

        PRINT @@twowayblockdegree;
        RETURN @@twowayblockdegree;     
    }
    INSTALL QUERY find_twoway_blockdegreeremovedscore

    CREATE QUERY match_country(INT personid_para, INT otherpersonid_para) FOR GRAPH candoor RETURNS (INT) {
        # returns 1 for match, 0 for no match
        STRING user_country;
        INT match;

        start = {person.*};
        result1 = SELECT l FROM start:s - (located_at:e) - location:l
            WHERE s.id == personid_para
            
            POST-ACCUM
                user_country = l.country;

        result1 = SELECT l FROM start:s - (located_at:e) - location:l
            WHERE s.id == otherpersonid_para
            
            POST-ACCUM
                IF l.country == user_country THEN
                    match = 1
                ELSE
                    match = 0
                END;

        PRINT match;
        RETURN match;     
    }
    INSTALL QUERY match_country

    CREATE QUERY match_gender(INT personid_para, INT otherpersonid_para) FOR GRAPH candoor RETURNS (INT) {
        # returns 1 for match, 0 for no match
        STRING user_gender;
        INT match;

        start = {person.*};
        result1 = SELECT g FROM start:s - (has_gender:e) - gender:g
            WHERE s.id == personid_para
            
            POST-ACCUM
                user_gender = g.gender_identity;

        result1 = SELECT g FROM start:s - (has_gender:e) - gender:g
            WHERE s.id == otherpersonid_para
            
            POST-ACCUM
                IF g.gender_identity == user_gender THEN
                    match = 1
                ELSE
                    match = 0
                END;

        PRINT match;
        RETURN match;     
    }
    INSTALL QUERY match_gender

    CREATE QUERY find_mentors(INT personid_para, STRING speciality_para, INT interest_level_para) FOR GRAPH candoor {
        SetAccum<INT> @@blockids;
        SetAccum<Edge<has_expertise>> @has_expertise;
        SetAccum<Vertex<speciality>> @speciality;
        SumAccum<INT> @score;

        start0 = {person.*};
        userVertexSet = SELECT s FROM start0:s WHERE s.id == personid_para;  

        start = {speciality.*};
        mentorResult = SELECT p FROM start:s - (has_expertise:e) - person:p
            WHERE
                lower(s.area) == lower(speciality_para) AND
                p.id != personid_para AND
                e.willing_to_mentor == True AND
                p.open_to_connect == True
            
            ACCUM
                p.@has_expertise = e,
                p.@speciality = s,
                p.@score += e.proficiency_level - interest_level_para
                
            POST-ACCUM
                p.@score += 4 - find_connectiondegree(personid_para, p.id),
                p.@score = p.@score - find_twoway_blockdegreeremovedscore(personid_para, p.id),
                p.@score += match_country(personid_para, p.id),
                p.@score += match_gender(personid_para, p.id);

        result2 = SELECT p FROM userVertexSet:s - ((block|reverse_block):b) -> person:p
            WHERE s.id == personid_para
            
            POST-ACCUM
                @@blockids += p.id;

        mentorResult2 = SELECT s FROM mentorResult:s
            WHERE NOT @@blockids.contains(s.id)
            ORDER BY s.@score DESC;
            
        PRINT mentorResult2 AS result;
    }
    INSTALL QUERY find_mentors

    CREATE QUERY find_mentees(INT personid_para, STRING speciality_para, INT proficiency_level_para) FOR GRAPH candoor {
        SetAccum<INT> @@blockids;
        SetAccum<Edge<has_aspiration>> @has_aspiration;
        SetAccum<Vertex<speciality>> @speciality;
        SumAccum<INT> @score;

        start0 = {person.*};
        userVertexSet = SELECT s FROM start0:s WHERE s.id == personid_para;  

        start = {speciality.*};
        menteeResult = SELECT p FROM start:s - (has_aspiration:e) - person:p
            WHERE
                lower(s.area) == lower(speciality_para) AND
                p.id != personid_para AND
                e.looking_for_mentor == True AND
                p.open_to_connect == True
            
            ACCUM
                p.@has_aspiration = e,
                p.@speciality = s,
                p.@score += proficiency_level_para - e.interest_level
                
            POST-ACCUM
                p.@score += 4 - find_connectiondegree(personid_para, p.id),
                p.@score = p.@score - find_twoway_blockdegreeremovedscore(personid_para, p.id),
                p.@score += match_country(personid_para, p.id),
                p.@score += match_gender(personid_para, p.id);

        result2 = SELECT p FROM userVertexSet:s - ((block|reverse_block):b) -> person:p
            WHERE s.id == personid_para
            
            POST-ACCUM
                @@blockids += p.id;

        menteeResult2 = SELECT s FROM menteeResult:s
            WHERE NOT @@blockids.contains(s.id)
            ORDER BY s.@score DESC;
            
        PRINT menteeResult2 AS result;
    }
    INSTALL QUERY find_mentees
'''


    results = conn.gsql(queries_gsql)
    print(results)



endTime = time.time()
print("time taken (min)")
print((endTime - startTime)/60)


# useful commands
# results = conn.gsql("USE GLOBAL DROP ALL")
# results = conn.gsql("USE GRAPH candoor SHOW JOB *")
# results = conn.gsql("DROP JOB ALL")
# print(results)