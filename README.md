# Candoor

_Thanks for taking an interest in Candoor. If you have any feedback you would like to give, or would like to stay informed about our project, please fill out our [interest form](https://docs.google.com/forms/d/e/1FAIpQLSd4ZxQMr6pJWh_TXU-yFns7t0eYT_vzWUOEFDEzvEGBum5qNw/viewform?vc=0&c=0&w=1&flr=0&usp=mail_form_link)._


**Contributers and Contact Information**

Audrey and Stephanie can be contacted at candoorteam@gmail.com


**Problem Statement addressed (or explain your own):**

**The Problem**

As humans we naturally need meaningful connections with others to thrive. Social connections impact almost all aspects of our lives, from our happiness and health to our work prospects, prosperity and material well-being (5). However, in 2018, global health service company Cigna (1) undertook a survey on loneliness. The survey of more than 20,000 US adults, aged 18 and over revealed an average loneliness score of 44 on the UCLA loneliness scale. A score of 43 or higher indicates loneliness. Younger adults born between the mid-1990s and early 2000s had higher loneliness scores of about 48, compared with about 39 for respondents aged 72 and older (2). More recently, due to the pandemic, this issue has only gotten worse. In late 2020, a study by the Making Caring Common Project (part of Harvard Graduate School of Education) (3) found that 43% of young adults reported an increase in loneliness due to the pandemic. 

One of the longest-running studies in social science known as the Harvard Study of Adult Development (6), has been ongoing for more than 80 years and aims to study how to lead healthy and happy lives. Robert Waldinger, the current director of the study, summarised the findings succinctly, stating that “Those who kept warm relationships got to live longer and happier, and the loners often died earlier”. 

Aside from our health and happiness, social isolation or the lack of opportunities to make meaningful connections can also have a negative impact on our job or career prospects. A visualisation provided by Our World in Data (5, 7)  showed that in Spain, up to 84% of people relied on contacts to find a job. Aside from this, not everyone knows how best to advance in their career, or has the privilege or resources to explore their interests. This is especially true for marginilised groups. For example, due to factors like a lack of self-confidence, support and a lack of representation, women currently only make up 28% of the workforce in STEM fields. In The US, data from the Economic Policy Institue showed that in 2020, median hourly wages between different racial groups varied starkly, with Hispanic people earning on average 27% less than their White peers. 

The issue of privilege and unequal access to resources is not new. While disportionately impacting marginalized communities, it has gotten worse over the years. In an analysis of 50 years of economic data by the Urban Institute, the institution showed that the poorest got poorer while the richest got much richer. Between 1963 and 2016, families in America near the bottom 10th percentile of the wealth distribution went from having no wealth on average to being about $1,000 in debt. 

If this problem goes unchecked, we feel that opportunities for social mobility will only decrease, and the income disparity, wider. We would like everyone to have the opportunity to explore their interests, unleash their full potential, and ultimately live fulfilled lives.

**The Challenge**

It is clear from these examples that for the good of society, it would be beneficial to find a way to help foster meaningful relationships between people so that everyone can live life to their fullest potential. We hope to help people foster meaningful connections with each other, by facilitating connections in a safe and mutually beneficial way by connecting aspirants looking to explore a subject, with experts willing to share about the same subject. 

Such an arrangement is most akin to what we know as a Mentor-Mentee relationship. According to LinkedIn, more than 80% of users want a mentor. In 2017, with 490 million users, LinkedIn launched Career Advice, a mentorship program that was unfortunately discontinued in late 2020. While it is possible to find people to connect with by cold texting a prospective connection on such social media sites, LinkedIn found that 80% of people said they experienced anxiety while reaching out. 

Another reason that such mentorship programs fail is that people may be intimidated to be a “mentor”, as they are afraid of the perceived level of commitment, responsibility and expertise required. The term “mentorship” has connotations of high levels of commitment and may be off-putting to people. 

In reality, we believe that everyone has the knowledge to share and everyone has something we want to learn. Therefore, our aim is to make such interactions informal and flexible, so as to foster candour and openness. A quick question about someone else’s experience is something that can still give valuable insights. 

For our project, we decided to create a social networking platform that lets people list down what skills or knowledge they have, that they could shed some light on, with what subjects or topics they're interested in hearing more about. This will ease the process of making connections as people will have a common topic to discuss. It would also smoothen the process of making a “cold call” connection approach that one would otherwise need to do on existing social media sites like LinkedIn, Facebook, Instagram etc. 

Ultimately, we would like to make use of graph technology to provide the framework that will facilitate making these connections. We see the potential in graph technologies in enabling us to provide the best connection suggestions for people so as to promote and ensure a safe and inclusive community. In the future, we hope to use graph databases to build out a skills graph that could provide further insights into what skills are closely linked, so that we may provide users with such suggestions too. 


**Description**: 

Explain what your project is trying to accomplish and how you utilized graph technology to achieve those goals. 
Describe how your submission is relevant to the problem statement and why it is impactful to the world. Remember to link your submission video here. 

Tell us how your entry was the most...					

- Impactful in solving a real world problem 
- Innovative use case of graph
- Ambitious and complex graph
- Applicable graph solution 

Other additions: 

 - **Data**: Give context for the dataset used and give full access to judges if publicly available or metadata otherwise. 
 - **Technology Stack**: Describe technologies and programming languages used. 
 - **Visuals**: Feel free to include other images or videos to better demonstrate your work.
 - Link websites or applications if needed to demonstrate your work. 

## Dependencies
For this project, we used python version 3.10.0 on Windows, TigerGraph version 3.5.0, and tested using Chrome browser.
The Python libraries we used are inlcuded in the [requirements.txt](requirements.txt) file 

## Installation

Download Python version 3.10 from https://www.python.org/downloads/release/python-3100/ and install it. At the bottom, please check the "Add Python 3.10 to PATH" option before clicking "Install Now".

Git clone this repository. If you have git installed on your computer, you may do this by typing this command in your terminal:

`git clone https://github.com/skhoosh/candoor.git`


Navigate to the candoor folder:

`cd .\candoor\`


If you want to, set-up a virtual environment to install the requirements (e.g. Use venv to create a virtual environment on Windows):

`python -m venv venv`


Activate the virtual environment: 

`.\venv\Scripts\activate`


Our project requires libraries, listed in the requirements.txt file. Install the required packages in the virtual environment:

`pip3 install -r requirements.txt`

---

### Making a tigergraph account and creating a blank tigergraph database
1. Sign up for a free tigergraph account at https://tgcloud.io/ if you do not have one.
2. When you are signed in to your tigergraph cloud account, click on the "My Solutions" tab on the left hand side.
3. On the right hand side, click on the blue "Create Solution" button to create a new tigergraph database.
4. We used tigergraph version 3.5.0. This option may not be available, go ahead and choose the closest version.
5. For the starter kit, choose the blank template (Blank v3.5.1) and then click next.
6. For the "Instance Settings" page, you may choose your desired cloud platform and preferred region. It is also fine to leave the settings as default, and does not impact performance.
7. For the "Solution Settings" page, set the "Name your Solution" to "candoor", "Set the Initial Password" to "password". You may choose to set your own "Subdomain" name, or leave it blank to let Tigergraph assign one to you.
8. Confirm and submit. Refresh the page. TigerGraph will process your submission and you should see a yellow circle indicating that it's processing. It will turn green when it's ready.
9. Go back to "My Solutions" page, and take a look at your solution. Click on your candoor solution to bring down a tab to see the details of your database. Take note of the "Domain" address listed. You will need to use this info later on in step 11.
10. If the Status of your solution is set to a blue circle and stopped, click on the "Solutions Operations" icon ![image](https://user-images.githubusercontent.com/12766571/163662412-58887c92-c81b-4ce1-866e-06665dfb0000.png)
 of your solution and click "Start". It takes a few minutes for tigergraph to set up and run the database. When the database is ready, the "Applications" icon ![image](https://user-images.githubusercontent.com/12766571/163662332-0e1e3907-c973-4fca-ab6b-6940d0e8206f.png) next to it will turn blue. You may click on the "Applications" icon and "GraphStudio" to see the tigergraph database.
11. In tigergraph_settings.py, change the variable "hostName" to the domain name you found in step 9. Please keep the "https://" as the first part of the hostName.
 
 
### Setting up the tigergraph database
 1. Run main.py with the command `python main.py`. This creates the graph schema, and installs all of the tigergraph queries. Please be patient, in our tests, it took us about 40mins for the code to run.  as tigergraph takes time to install the queries so they can be run super fast later on.

### Getting started with Candoor!
1. Once the tigergraph database has been setup, navigate to the project directory 
`cd .\candoor\`
3. Run app.py.
` python app.py`
5. When the app says it's running, open your browser of choice and head to http://localhost:5000 to access Candoor.
6. Alternatively,  enter the address stated after "wsgi starting up on" into your browser.
7. You may create a new profile, or log on with "audreybot@candoor.com" with the password "password". Please note that we only created a limited number of test profiles, so searching your preferred aspiration/expertise may not populate any search resutls. Some suggested searches are "Engineering" and "Computer Science" to match with our dummy accounts.

## Known Issues and Future Improvements

Explain known liminations within the project and potential next steps. 

## Reflections

Review the steps you took to create this project and the resources you were provided. Feel free to indiciate room for improvement and general reflections.

## References

Please give credit to other projects, videos, talks, people, and other sources that have inspired and influenced your project. 

---
Thank you :>


