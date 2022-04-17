# Candoor

For this project, we used python version 3.10.0 on Windows, TigerGraph version 3.5.0, and tested using Chrome browser.

Download Python version 3.10 from https://www.python.org/downloads/release/python-3100/ and install it.

Git clone this repository. If you have git installed on your computer, you may do this by typing this command in your terminal:

`git clone https://github.com/skhoosh/candoor.git`


Navigate to the candoor folder:

`cd .\candoor\`


Set-up a virtual environment to install the requirements (e.g. Use venv to create a virtual environment on Windows):

`python -m venv venv`


Activate the virtual environment: 

`.\venv\Scripts\activate`


Our project requires libraries, listed in the requirements.txt file. Install the required packages in the virtual environment:

`pip install -r requirements.txt`

---

### Making a tigergraph account and creating a blank tigergraph database
1. Sign up for a free tigergraph account at https://tgcloud.io/ if you do not have one.
2. When you are signed in to your tigergraph cloud account, click on the "My Solutions" tab on the left hand side.
3. On the right hand side, click on the blue "Create Solution" button to create a new tigergraph database.
4. We used tigergraph version 3.5.0. This option may not be available, go ahead and choose the closest version.
5. For the starter kit, choose the blank template (Blank v3.5.1) and then click next.
6. For the "Instance Settings" page, you may choose your desired cloud platform and preferred region. It is also fine to leave the settings as default, and does not impact performance.
7. For the "Solution Settings" page, set the "Name your Solution" to "candoor", "Set the Initial Password" to "password". You may choose to set your own "Subdomain" name, or leave it blank to let Tigergraph assign one to you.
8. Confirm and submit. TigerGraph will process your submission and you should see a yellow circle indicating that it's processing. It will turn green when it's ready.
10. Go back to "My Solutions" page, and take a look at your solution. Click on your solution to see the details of your database. Take note of the "Domain" address listed. You will need to use this info later on in step 11.
11. If your the Status of your solution is set to a blue circle and stopped, click on the "Solutions Operations" icon ![image](https://user-images.githubusercontent.com/12766571/163662412-58887c92-c81b-4ce1-866e-06665dfb0000.png)
 of your solution and click "Start". It takes a few minutes for tigergraph to set up and run the database. When the database is ready, the "Applications" icon ![image](https://user-images.githubusercontent.com/12766571/163662332-0e1e3907-c973-4fca-ab6b-6940d0e8206f.png) next to it will turn blue. You may click on the "Applications" icon and "GraphStudio" to see the tigergraph database.
11. In tigergraph_settings.py, change the variable "hostName" to the domain name you found in step 9.
 
 
### Setting up the tigergraph database
 1. Run main.py. This creates the graph schema, and installs all of the tigergraph queries. Please be patient, in our tests, it took us about 40mins for the code to run.  as tigergraph takes time to install the queries so they can be run super fast later on.

### Getting started with Candoor!
1. Once the tigergraph database has been setup, run app.py.
2. When the app says it's running, open your browser of choice and head to http://localhost:5000 to access Candoor.
3. Alternatively,  enter the address stated after "wsgi starting up on" into your browser.
4. You may create a new profile, or log on with "audreybot@candoor.com" with the password "password". Please note that we only created a limited number of test profiles, so searching your preferred aspiration/expertise may not populate any search resutls. Some suggested searches are "Engineering" and "Computer Science" to match with our dummy accounts.

---

_Thanks for taking an interest in Candoor. If you have any feedback you would like to give, or would like to stay informed about our project, please fill out our [interest form](https://docs.google.com/forms/d/e/1FAIpQLSd4ZxQMr6pJWh_TXU-yFns7t0eYT_vzWUOEFDEzvEGBum5qNw/viewform?vc=0&c=0&w=1&flr=0&usp=mail_form_link)._

Thank you :>
