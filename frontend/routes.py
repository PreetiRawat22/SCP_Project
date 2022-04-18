from flask import Blueprint, render_template, session, redirect, request, flash, url_for, send_file, send_from_directory, jsonify
from flask_login import current_user

import forms
from api.book_client import BookClient
from api.user_api import UserClient
from api.classroom_api import ClassroomClient
from api.emailexcel_client import EmailExcelClient
from werkzeug.utils import secure_filename
from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import requests
from flask import Response
import json
from datetime import datetime, timedelta
from helper.queue_helper import SQSHelper
from helper.s3_helper import Upload_File
import webbrowser
import pandas as pd
import base64
from flask import Markup

blueprint = Blueprint('frontend', __name__)


#api endpoint to direct to landing page
@blueprint.route('/', methods=['GET'])
def index():
    return render_template('index.html')

#Registers the new users. user can be a teacher and student.
@blueprint.route('/register', methods=['POST', 'GET'])
def register():
    form = forms.RegistrationForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data

            if UserClient.user_exists(username):
                flash("Please try another user name")
                return render_template('register.html', form=form)
            else:
                user = UserClient.create_user(form)
                if user:
                    flash("Registered. Please login.")
                    return redirect(url_for('frontend.index'))
        else:
            flash("Errors")

    return render_template('register.html', form=form)

#To login into the application.
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            api_key = UserClient.login(form)
            if api_key:
                session['user_api_key'] = api_key
                user = UserClient.get_user()
                session['user'] = user['result']
                session['books']=BookClient.get_books()
                flash('Welcome back {}'.format(session['user'].get("username")))
                return redirect(url_for('frontend.index'))
            else:
                flash('Cannot Login')
        else:
            flash('Cannot Login')

    return render_template('login.html', form=form)

#To logout from the application.
@blueprint.route('/logout', methods=['GET'])
def logout():
    session.clear()
    flash('Logged out')
    return render_template('thankyou.html')

#get book details using slug id. 
@blueprint.route('/book/<slug>', methods=['GET', 'POST'])
def book_details(slug):
    response = BookClient.get_book(slug)
    book = response['result']

    form = forms.ItemForm(book_id=book['id'])

    if request.method == 'POST':
        if 'user' not in session:
            flash("Please Login")
            return redirect(url_for('frontend.login'))

        order = OrderClient.add_to_cart(book_id=book['id'], quantity=1)
       
        session['order'] = order['result']
        flash("Book added to the cart")

    return render_template('book_info.html', book=book, form=form)

#adds a new book into the database.
@blueprint.route('/add_book', methods=['POST','GET'])
def add_book():
    form = forms.AddNewBookForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            bookname = form.name.data
            slug=form.slug.data
            f = form.upload.data
            filename = secure_filename(f.filename)
            #checks the uploaded filename with entered filename
            if filename!=bookname+'.pdf':
                flash("Wrong file uploaded. Please upload {}".format(bookname))
            elif filename==bookname+'.pdf':
                isBookExists=BookClient.book_exists(bookname, slug)
                if(isBookExists==False):
                    upload_file=Upload_File()
                    if(upload_file.create_bucket('scpprojbucket')):
                        isFileUploaded=upload_file.upload_file('scpprojbucket',f,filename)
                        #if file is uploaded then save the details in the database. 
                        if(isFileUploaded):
                            book = BookClient.add_book(form)
                            flash("book added.")
                        else:
                            flash('book not added'+bookname)
                    else:
                            flash('book not added'+bookname)
                else:
                    flash("book {} and slug {} already exists.".format(filename, slug))
            else:
                flash('book not added'+bookname)
    
    return render_template('add_book.html', form=form)

#endpoint to direct to search_book.html. It displays all the books with searching option.
@blueprint.route('/search_books', methods=['POST','GET'])
def search_books():
    if current_user.is_authenticated:
         session['order']={}
    try:
        books = BookClient.get_books()
    except:
        books = {'result': []}
   
    return render_template('search_book.html', books=books)

#It download the book of a particular name. 
@blueprint.route('/download/<name>', methods=['GET'])
def download(name):
    file_nm=str(name)+'.pdf'
    uploaded_file_object=Upload_File()
    url=uploaded_file_object.get_object_access_url('scpprojbucket', file_nm)
    flash(Markup('file download. click <a href={0} class="alert-link">here</a>'.format(url)))
    return render_template('search_book.html', books=session["books"])
   
#shows the scheduled classes to the students.
@blueprint.route('/scheduled_classes', methods=['GET'])
def scheduled_classes():
    userid=session['user'].get("id")
    classes = ClassroomClient.get_scheduled_meetings(userid)
    return render_template('scheduled_classes.html', classes=classes)
    
#It directs to the book_meeting.html.
@blueprint.route('/classroom_booking', methods=['GET','POST'])
def classroom_booking():
    students=UserClient.get_users()
    return render_template('book_meeting.html', students=students)

#It gets all students.
@blueprint.route('/get_students', methods=['GET','POST'])
def get_students():
    students=UserClient.get_students()
    session['students']=students
    form = forms.CreateAssignmentForm()
    return render_template('create_assignment.html', students=students, form=form)

#blocks the calender of the invitee for the meeting using google apis like google meet and google calender.
@blueprint.route('/block_calendar', methods=['GET', 'POST'])
def block_calender():
    form = request.form
    if request.method == 'POST':
        studentsid = form.get('studentids')
        studentnames=form.get('studentsmeet')
        meetingtime=form.get('Meetingtime')
        meetingduration=form.get('meeting_duration')
        meetingtitle=form.get('meeting_information')
        attendent_emails=[]
        organizer_email=session['user'].get("email")
        idarray = studentsid.split(',')
        for id in idarray:
            userdetail = UserClient.get_userbyid(id)
            attendent_email=userdetail["result"].get("email")
            attendent_emails.append({"email":attendent_email})
        attendent_emails.append({"email":organizer_email })
        use_google_calender(meetingtime, attendent_emails, meetingduration,meetingtitle)
        saved_classroom=ClassroomClient.create_classroom(form)
        session['classroom'] = saved_classroom['result']
    flash("Notified "+ str(studentnames))
    students=UserClient.get_users()
    return render_template('book_meeting.html', students=students)

#It helps in emailing the details of all the books in the form of an excel using the 
#library EmailExcel.
@blueprint.route('/email_excel', methods=['POST', 'GET'])
def email_excel():
    books = session['books']
    df = pd.DataFrame(books['result'], columns=['name', 'author_name', 'published_year'])
    try:
        pickled = pickle.dumps(df)
        pickled_b64 = base64.b64encode(pickled)
        useremailid=session['user'].get("email")
        email_subject="Details of books are attached"
        email_text="Please find attached books details."
        result=EmailExcelClient.email_excel(pickled_b64, useremailid, email_subject, email_text)
        if(result['issucessful']):
            flash("details of all book is mailed to {}.".format(useremailid))
    except Exception as e:
        print(str(e))
        flash("issue while emailing the excel file of book details.")
    return redirect(url_for('frontend.search_books'))

#It creates the assignment for a student by the teacher.
@blueprint.route('/create_assignment', methods=['POST','GET'])
def createassignment():
    form = forms.CreateAssignmentForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            sids = form.student_ids.data
            attendent_emails=[]
            organizer_email=session['user'].get("email")
            idarray = sids.split(',')
            f = form.upload.data
            filename = secure_filename(f.filename)
            try:
                for id in idarray:
                    userdetail = UserClient.get_userbyid(id)
                    attendent_email=userdetail["result"].get("email")
                    attendent_emails.append(attendent_email)
                attendent_emails.append(organizer_email)
                #upload assignment file to s3
                upload_file=Upload_File()
                if(upload_file.create_bucket('scpprojbucket')):
                    isFileUploaded=upload_file.upload_file('scpprojbucket',f,filename)
                    #if file is uploaded then save the details in the database. 
                    if(isFileUploaded):
                        #get file url from s3
                        uploaded_file_object=Upload_File()
                        url=uploaded_file_object.get_object_access_url('scpprojbucket', filename)
                        #push message to the SQS queue
                        sqsobj= SQSHelper()       
                        data={"emailIds": attendent_emails, "assignment_url": str(url)}
                        #checks if message is sent successfully. 
                        isMessageSent=sqsobj.send_message(data)
                        if(isMessageSent):
                            flash("assignment {} sent successfully.".format(filename))
                        else:
                            flash('issue sending the assignment {}'.format(filename))
                    else:

                        flash('issue sending the assignment {}'.format(filename))
                else:
                    flash('issue sending the assignment {}'.format(filename))
            except Exception as e:
                print(str(e))
                flash('issue sending the assignment {}'.format(filename))
                
    return render_template('create_assignment.html', students=session['students'], form=form)

#private method to access google calender and google meet for sending the invitation for virutal classrooms.
def use_google_calender(state_date, emails,meetingduration, title):
    credentials=pickle.load(open("token.pkl", "rb"))
    start_time=datetime.strptime(state_date, '%Y-%m-%dT%H:%M')
    end_time=start_time+timedelta(hours=float(meetingduration))
    time_zone='Europe/Dublin'
    try: 
        service = build("calendar", "v3", credentials=credentials)
        result=service.calendarList().list().execute()
        calender_id=result['items'][0]['id']
        calendar_events= service.events().list(calendarId=calender_id).execute()
        #event is created holding all the details of the meeting like start time, end time and timezone.
        event={
        'summary': title,
        'description': title,
        'start': {
        'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': time_zone,
        },
        'end': {
        'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': time_zone,
        },
        "conferenceData": {
        "createRequest": {
        "conferenceSolutionKey": {
          "type": "hangoutsMeet"
        },
        "requestId": "some-random-string2"
        }
        },
        'attendees': emails,
        'reminders': {
        'useDefault': False,
        'overrides': [
        {'method': 'email', 'minutes': 24 * 60},
        {'method': 'popup', 'minutes': 10},
        ],
        },
        }
        #event is inserted into the calender of the user with google meet link.
        event = service.events().insert(calendarId=calender_id, 
        conferenceDataVersion= 1,body=event, sendNotifications=True).execute()
        print('Event created: %s' % (event.get('htmlLink')))
    except Exception as e:
        #incase of an exception a token has to be created again, as it might have been expired. 
        print(str(e))
        scopes = ['https://www.googleapis.com/auth/calendar']
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes=scopes)
        credentials = flow.run_console()
        pickle.dump(credentials, open("token.pkl","wb"))
        credentials=pickle.load(open("token.pkl", "rb"))
        service = build("calendar", "v3", credentials=credentials)
        result=service.calendarList().list().execute()
        calender_id=result['items'][0]['id']
        calendar_events= service.events().list(calendarId=calender_id).execute()
        event={
        'summary': title,
        'description': title,
        'start': {
        'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': time_zone,
        },
        'end': {
        'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': time_zone,
        },
        "conferenceData": {
        "createRequest": {
        "conferenceSolutionKey": {
          "type": "hangoutsMeet"
        },
        "requestId": "some-random-string2"
        }
        },
        'attendees': emails,
        'reminders': {
        'useDefault': False,
        'overrides': [
        {'method': 'email', 'minutes': 24 * 60},
        {'method': 'popup', 'minutes': 10},
        ],
        },
        }
        event = service.events().insert(calendarId=calender_id, conferenceDataVersion= 1,
        body=event, sendNotifications=True).execute()
        print('Event created: %s' % (event.get('htmlLink')))
    
