from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, IntegerField, RadioField, FileField
from wtforms.validators import DataRequired, InputRequired

#LoginForm for the login
class LoginForm(FlaskForm):
    #name of the user
    username = StringField('Username', validators=[DataRequired()])
    #password of the user
    password = PasswordField('Password', validators=[DataRequired()])
    #submit button
    submit = SubmitField('Login')

#RegistrationFrom for the registration. 
class RegistrationForm(FlaskForm):
    #name of the user
    username = StringField('Username', validators=[DataRequired()])
    #password of the user
    password = PasswordField('Password', validators=[DataRequired(8)])
    #role of the user. for example teacher or student
    role=RadioField('Role', choices=[('teacher','teacher'),('student','student')])
    #emailid of the user
    email = StringField('Email', validators=[DataRequired()])
    #submit button
    submit = SubmitField('Register')

#AddNewBookForm for the adding new book.
class AddNewBookForm(FlaskForm):
    #name of the book
    name = StringField('Name', validators=[DataRequired()])
    #slug or prepublished name of the book
    slug = StringField('Slug', validators=[DataRequired()])
    #name of the author of book
    author_name = StringField('Author Name')
    #publishing year of the book
    published_year= StringField('Published Year')
    #electronic copy of the book to be uploaded
    upload = FileField("Please select an image to upload", validators=[InputRequired()])
    #submit button
    submit = SubmitField('Add Book')

#CreateAssignmentForm for the assignment creation by the teachers.
class CreateAssignmentForm(FlaskForm):
    #student id to whom assignment is to be assigned.
    student_ids=StringField('Student Id', validators=[DataRequired()])
    #upload assignment
    upload = FileField("Please select a file to upload", validators=[InputRequired()])
    #maximum marks of the assignment
    maximum_marks=IntegerField('maximum marks')
    #topic or subject of the assignment
    assignment_topic=StringField('Assignment Topic', validators=[DataRequired()])
    #submit field
    submit = SubmitField('Create Assignment')
    
    