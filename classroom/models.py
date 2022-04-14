from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    db.app = app
    db.init_app(app)

#The virtual classroom model. It contains fields like teacher_id, meeting_information, duration of meeting etc. 
class VirtualClassroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, nullable=False)
    meeting_information = db.Column(db.String(500), nullable=False)
    duration = db.Column(db.String(500), nullable=False)
    date_of_booking = db.Column(db.String(150), nullable=False)
    virtual_classroom_invitees=db.relationship('VirtualClassroomInvitee', backref="virtualClassroomInvitee")
    
    #this action serializes the virtual classroom model.
    def serialize(self):
        return {
            'teacher_id': self.teacher_id,
            'meeting_information': self.meeting_information,
            'duration': self.duration,
            'date_of_booking': self.date_of_booking,
            'virtual_classroom_invitees': [x.serialize() for x in self.virtual_classroom_invitees]
            }

#model to stores details of all the invitee for any virtual meeting. 
class VirtualClassroomInvitee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invitee_id = db.Column(db.String(100), nullable=False)
    meeting_id = db.Column(db.Integer, db.ForeignKey(VirtualClassroom.id))

#it serializes the VirtualClassroomInvitee model.
    def serialize(self):
        return {
            'invitee_id': self.invitee_id,
            'meeting_id':self.meeting_id
        }
