from flask import Blueprint, request, jsonify
import pandas as pd
import ast
import pickle
import base64
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

emailexcel_blueprint = Blueprint('emailexcel_api_routes', __name__, url_prefix='/api/emailexcel')

#Public api EmailExcel: input is the encoded model data to be converted into excel file. It also 
#email them at the required email id.
#inputs: emailid- receiver's email id
#        modeldata -  model data to be converted into excel
#        subject- subject of the email
#        text - text of the email
@emailexcel_blueprint.route('/emailcreatedexcel', methods=['POST'])
def emailcreatedexcel():
    emailid = request.form['emailid']
    dfdata = request.form['modeldata']
    subject = request.form['subject']
    text = request.form['text']
    hug_pickled_str = dfdata
    df = pickle.loads(base64.b64decode(hug_pickled_str.encode()))
    df.to_excel("output.xlsx")
    send_mail("invitescptest@gmail.com",[emailid], subject, text,["output.xlsx"])
    result={'issucessful': True}
    return result

#Action to send an email. 
#inputs: send_from- email id from which mail is to be sent.
#        send_to- list of email ids to send mail to.
#        subject - mail's subject
#        text - mail's text
#        files - a list of path of files to be sent as an attachment
def send_mail(send_from, send_to, subject, text, files=None):
    assert isinstance(send_to, list)

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)


    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()
    smtp.login(send_from, "abcd@1234")
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()