from flask import Blueprint, jsonify, request
import requests

from models import VirtualClassroom,VirtualClassroomInvitee, db

classroom_blueprint = Blueprint('classroom_api_routes', __name__, url_prefix="/api/classroom")

USER_API_URL = 'http://127.0.0.1:5001/api/user'

#get the current logged in or in session user details.
def get_user(api_key):
    headers = {
        'Authorization': api_key
    }

    response = requests.get(USER_API_URL, headers=headers)
    if response.status_code != 200:
        return {'message': 'Not Authorized'}

    user = response.json()
    return user

#save the virtual classroom details in virtualclassroom model. It also saves the detail related to the 
#invitee of the virtual classroom into VirtualClassroomInvitee.
@classroom_blueprint.route('/create', methods=['POST'])
def create_classrooms():
    try:
        vc = VirtualClassroom()
        vc.teacher_id = request.form['teacher_id']
        vc.meeting_information = request.form['meeting_information']
        vc.duration = request.form['duration']
        vc.date_of_booking = request.form['date_of_booking']

        studentids=request.form['invitees_id']
        idarray = studentids.split(',')

        for id in idarray:
            vci=VirtualClassroomInvitee()
            vci.invitee_id=id
            vc.virtual_classroom_invitees.append(vci)
        db.session.add(vc)
        db.session.commit()


        response = {'message': 'Virtual classroom Create', 'result': vc.serialize()}
    except Exception as e:
        print(str(e))
        response = {'message': 'Virtual classroom creation failed'}

    return jsonify(response)

#It gets the scheduled virtual classroom details by the user id or invitee id. 
@classroom_blueprint.route('/<invitee_id>', methods=['GET'])
def get_meeting(invitee_id):
    meetings = VirtualClassroomInvitee.query.filter_by(invitee_id=invitee_id).all()
    meets = [meet.serialize() for meet in meetings]
    scheduled_classes=[]
    print(meets)
    for m in meets:
        vc = VirtualClassroom.query.filter_by(id = m['meeting_id']).first()
        scheduled_classes.append(vc.serialize())
    response = {"result":scheduled_classes}
    return jsonify(response)