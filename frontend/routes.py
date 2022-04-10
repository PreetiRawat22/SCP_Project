from flask import Blueprint, render_template, session, redirect, request, flash, url_for, send_file, send_from_directory
from flask_login import current_user

import forms
from api.book_client import BookClient
from api.user_api import UserClient
from api.classroom_api import ClassroomClient
from werkzeug.utils import secure_filename
from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import requests
from flask import Response
import json
from datetime import datetime, timedelta
#from helper.queue_helper import SQSHelper
from helper.s3_helper import Upload_File
import webbrowser


blueprint = Blueprint('frontend', __name__)

def get_event():
    event =            {
  'summary': 'Google I/O 2015',
  'location': '800 Howard St., San Francisco, CA 94103',
  'description': 'A chance to hear more about Google\'s developer products.',
  'start': {
    'dateTime': '2015-05-28T09:00:00-07:00',
    'timeZone': 'America/Los_Angeles',
  },
  'end': {
    'dateTime': '2015-05-28T17:00:00-07:00',
    'timeZone': 'America/Los_Angeles',
  },
  'recurrence': [
    'RRULE:FREQ=DAILY;COUNT=2'
  ],
  'attendees': [
    {'email': 'lpage@example.com'},
    {'email': 'sbrin@example.com'},
  ],
  'reminders': {
    'useDefault': False,
    'overrides': [
      {'method': 'email', 'minutes': 24 * 60},
      {'method': 'popup', 'minutes': 10},
    ],
  },
}
    return event

@blueprint.context_processor
def cart_count():
    count = 0
    order = session.get('order')
    if order:
        for item in order.get('order_items'):
            count += item['quantity']

    return {'cart_items': count}


@blueprint.route('/', methods=['GET'])
def index():
    if current_user.is_authenticated:
        #session['order'] = OrderClient.get_order_from_session()
         session['order']={}
    try:
        books = BookClient.get_books()
        session['books']=books
    except:
        books = {'result': []}

    return render_template('index.html', books=books)


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
                print(session['user'].get("role"))

                #order = OrderClient.get_order()
                #if order.get('result'):
                 #   session['order'] = order['result']
                session['books']=BookClient.get_books()
                session['order'] = {}
                flash('Welcome back')
                return redirect(url_for('frontend.index'))
            else:
                flash('Cannot Login')
        else:
            flash('Cannot Login')

    return render_template('login.html', form=form)


@blueprint.route('/logout', methods=['GET'])
def logout():
    session.clear()
    flash('Logged out')
    return redirect(url_for('frontend.index'))


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


@blueprint.route('/checkout', methods=['GET'])
def checkout():
    if 'user' not in session:
        flash('Please login')
        return redirect(url_for('frontend.login'))

    if 'order' not in session:
        flash("Please add some books to the cart")
        return redirect(url_for("frontend.index"))

    order = OrderClient.get_order()

    if len(order['result']['order_items']) == 0:
        flash("Please add some books to the cart")
        return redirect(url_for("frontend.index"))

    OrderClient.checkout()

    return redirect(url_for('frontend.thank_you'))


@blueprint.route('/thank-you', methods=['GET'])
def thank_you():
    if 'user' not in session:
        flash('Please login')
        return redirect(url_for('frontend.login'))

    if 'order' not in session:
        flash("Please add some books to the cart")
        return redirect(url_for("frontend.index"))

    session.pop('order', None)
    flash("Your order is processing.")

    return render_template('thankyou.html')

@blueprint.route('/add_book', methods=['POST','GET'])
def add_book():
    form = forms.AddNewBookForm()
    print("before post")
    if request.method == 'POST':
        print("after post")
        if form.validate_on_submit():
            print("after submit")
            bookname = form.name.data
            book = BookClient.add_book(form)
            print(book)
            if book:
                f = form.upload.data
                filename = secure_filename(f.filename)
                print(filename)
                #f.save('uploads/' + bookname+'.pdf')
                upload_file=Upload_File()
                if(upload_file.create_bucket('scpprojbucket')):
                    isFileUploaded=upload_file.upload_file('scpprojbucket',f,filename)
                    print(isFileUploaded)
                    #if file is uploaded then save the details in the database. 
                    if(isFileUploaded):
                        flash("book added.")
                    else:
                        flash('book not added'+bookname)
            else:
                flash('book not added'+bookname)
    
    return render_template('add_book.html', form=form)

@blueprint.route('/google_api', methods=['POST','GET'])
def google_api():
    scopes = ['https://www.googleapis.com/auth/calendar']
    flow = InstalledAppFlow.from_client_secrets_File("client_secret.json", scopes=scopes)
    flow.run_console()

   
@blueprint.route('/search_books', methods=['POST','GET'])
def search_books():
    if current_user.is_authenticated:
        #session['order'] = OrderClient.get_order_from_session()
         session['order']={}
    try:
        books = BookClient.get_books()
    except:
        books = {'result': []}
   
    return render_template('search_book.html', books=books)

@blueprint.route('/download/<name>', methods=['GET'])
def download(name):
    #path = "uploads/"+str(name)+".pdf"
    #return(send_file(path, as_attachment=True)
    flash("file download")
    file_nm=str(name)+'.pdf'
    uploaded_file_object=Upload_File()
    url=uploaded_file_object.get_object_access_url('scpprojbucket', file_nm)
    webbrowser.open(url, new=2, autoraise=True)
    flash("file download")
    return render_template('search_book.html', books=session["books"])
   

@blueprint.route('/scheduled_classes', methods=['GET'])
def scheduled_classes():
    #path = "uploads/"+str(name)+".pdf"
    #return(send_file(path, as_attachment=True)
    userid=session['user'].get("id")
    classes = ClassroomClient.get_scheduled_meetings(userid)
    print(classes['result'])
    return render_template('scheduled_classes.html', classes=classes)
    
@blueprint.route('/classroom_booking', methods=['GET','POST'])
def classroom_booking():
    students=UserClient.get_users()
    return render_template('book_meeting.html', students=students)

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
        #print('attendent email are'+attendent_emails)
        use_google_calender(meetingtime, attendent_emails, meetingduration,meetingtitle)
        saved_classroom=ClassroomClient.create_classroom(form)
        session['classroom'] = saved_classroom['result']
    flash("Notified "+ str(studentnames))
    students=UserClient.get_users()
    return render_template('book_meeting.html', students=students)

@blueprint.route('/create_assignment', methods=['POST','GET'])
def createassignment():
    form = forms.CreateAssignmentForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            sids = form.studentids.data
            book = BookClient.add_book(form)
            if book:
                f = form.upload.data
                filename = secure_filename(f.filename)
                print(filename)
                f.save('uploads/' + bookname+'.pdf')
                flash("book added.")
            else:
                flash('book not added'+bookname)
    
    return render_template('create_assignment.html', form=form)


def use_google_calender(state_date, emails,meetingduration, title):
    credentials=pickle.load(open("token.pkl", "rb"))
    print(credentials)
    #start_time=datetime(2022, 3, 22, 19, 30)
    start_time=datetime.strptime(state_date, '%Y-%m-%dT%H:%M')
    end_time=start_time+timedelta(hours=float(meetingduration))
    time_zone='Asia/Kolkata'
    if credentials: 
        service = build("calendar", "v3", credentials=credentials)
        result=service.calendarList().list().execute()
        print(result['items'][0]['id'])
        calender_id=result['items'][0]['id']
        calendar_events= service.events().list(calendarId=calender_id).execute()
        print(calendar_events['items'][0])
        event={
        'summary': title,
        #'location': '800 Howard St., San Francisco, CA 94103',
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
        event = service.events().insert(calendarId=calender_id, 
        conferenceDataVersion= 1,body=event, sendNotifications=True).execute()
        print('Event created: %s' % (event.get('htmlLink')))
        #create_event=service.events.insert(calendarId=calender_id, body=event).execute()
        #print(create_event)
    else:      
        scopes = ['https://www.googleapis.com/auth/calendar']
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes=scopes)
        credentials = flow.run_console()
        pickle.dump(credentials, open("token.pkl","wb"))
        credentials=pickle.load(open("token.pkl", "rb"))
        service = build("calendar", "v3", credentials=credentials)
        result=service.calendarList().list().execute()
        print(result['items'][0]['id'])
        calender_id=result['items'][0]['id']
        calendar_events= service.events().list(calendarId=calender_id).execute()
        print(calendar_events['items'][0])
        event={
        'summary': 'Google I/O 2015',
        'location': '800 Howard St., San Francisco, CA 94103',
        'description': 'A chance to hear more about Google\'s developer products.',
        'start': {
        'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': time_zone,
        },
        'end': {
        'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': time_zone,
        },
        #'attendees': [
        #{'email': 'advik.dangwal0909@gmail.com'}
        #],
        'attendees': emails,
        'reminders': {
        'useDefault': False,
        'overrides': [
        {'method': 'email', 'minutes': 24 * 60},
        {'method': 'popup', 'minutes': 10},
        ],
        },
        }
        event = service.events().insert(calendarId=calender_id, body=event, sendNotifications=True).execute()
        print('Event created: %s' % (event.get('htmlLink')))
    
