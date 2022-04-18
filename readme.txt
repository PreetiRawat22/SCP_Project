#E-School Platform


Requirement:-
===================
Aws account
GitHub account
===================


Execution:-
===================
The Application Consists of 5 micro-services namely - Book, User, Classroom, Front-end and Email Excel. Each microservice has been deployed separately on a different AWS EC2 instance. 

Under each folder of the microservice, .env file has been created to activate the virtual environment.
-To activate the virtual environment, run the following command -
    source .env/bin/activate


Under each folder of the microservice, you will find a requirements.txt file.

-To install the packages for this project, please execute the following command for each microservice.
    pip install -r requirements.txt (Please make sure you are in the same path/directory as that of the requirements.txt file)

Once the packages are installed, try to run the project using the following command -
    python app.py runserver

Make sure to run the frontend service app.py file to start the application.

You will see the application running on your local address. You can browse the website by copy pasting the link in your browser.
===================



AWS Cloud:-
===================
To deploy the website on public cloud, we are using Amazon Web Services (AWS) Elastic Container (EC2) instance.
Link for the deployed website -----> http://54.147.235.223:5004/
===================