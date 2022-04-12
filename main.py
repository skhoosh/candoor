import pyTigerGraph as tg

hostName = "https://candoor01.i.tgcloud.io"
userName = "tigergraph"
password = "password"
conn = tg.TigerGraphConnection(host = hostName, username = userName, password = password)


def getgraphconnection(conn, hostName, userName, password, graphName):
    conn.graphname = graphName
    secret = conn.createSecret()
    authToken = conn.getToken(secret)
    authToken = authToken[0]

    conn = tg.TigerGraphConnection(host=hostName, graphname="candoor", username=userName, password=password,
                                   apiToken=authToken)

    return conn


clearAll = False
createGlobalSchema = False
createGraph = False
connectToGraph = True
loadGraph = False
dropQueries = True
installQueries = True

if clearAll:
    results = conn.gsql("USE GLOBAL DROP ALL")
    print(results)

if createGlobalSchema:
    # create global schema
    globalSchema_gsql = '''
    USE GLOBAL
    CREATE VERTEX person (PRIMARY_ID id INT, name STRING, email STRING, password STRING, profile_picture STRING, profile_header STRING, pronouns STRING, profile_description STRING, open_to_connect BOOL DEFAULT "true", auth_token STRING) WITH primary_id_as_attribute="true"
    CREATE VERTEX gender (PRIMARY_ID gender_identity STRING) WITH primary_id_as_attribute="true"
    CREATE VERTEX location (PRIMARY_ID country STRING) WITH primary_id_as_attribute="true"
    CREATE VERTEX speciality (PRIMARY_ID area STRING) WITH primary_id_as_attribute="true"
    CREATE VERTEX message (PRIMARY_ID id INT, text STRING, time DATETIME)
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

    CREATE QUERY getperson_byid(INT id_para) FOR GRAPH candoor {
        start = {person.*};
        result = SELECT s FROM start:s WHERE s.id == id_para;
        PRINT result;
    }
    INSTALL QUERY getperson_byid

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


'''




    results = conn.gsql(queries_gsql)
    print(results)



# useful commands
# results = conn.gsql("USE GLOBAL DROP ALL")
# results = conn.gsql("USE GRAPH candoor SHOW JOB *")
# results = conn.gsql("DROP JOB ALL")
# print(results)


'''

    '''