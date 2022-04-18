import requests
from flask import session
from . import EMAIL_EXCEL_URL

#ExcelExcelclient to communicate with external library.
class EmailExcelClient:
    
    
    @staticmethod
    def email_excel(data, email, subject, text):
        output=None
        payload = {
            'modeldata': data,
            'emailid': email,
            'subject':subject,
            'text':text
        }
        url = EMAIL_EXCEL_URL + '/api/emailexcel/emailcreatedexcel'
        response = requests.request("POST", url=url, data=payload)
        if response:
            output = response.json()
        return output

    