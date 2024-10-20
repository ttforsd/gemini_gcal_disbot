from dotenv import load_dotenv
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
from database import database
import pytz
load_dotenv(override=True)



SCOPES = ['https://www.googleapis.com/auth/calendar']
calendar_id = os.getenv('CALENDAR_ID')

def write2gcal(event_dict):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        utc = pytz.UTC
        ukt = pytz.timezone('Europe/London')
        hkt = pytz.timezone('Asia/Hong_Kong')
        service = build('calendar', 'v3', credentials=creds)
        # Call the Calendar API
        event = service.events().insert(calendarId=calendar_id, body=event_dict).execute()
        print('Event created: %s' % (event.get('htmlLink')))
        dt = event.get('start').get('dateTime')
        if dt != None: 
            dt = dt.replace('Z', '+00:00')
            dt = datetime.datetime.fromisoformat(dt)
            hkt = dt.astimezone(hkt)
            ukt = dt.astimezone(ukt)
            dt = dt.strftime("%A %d/%m/%Y %H:%M")
            ukt = ukt.strftime("%A %d/%m/%Y %H:%M")
            hkt = hkt.strftime("%A %d/%m/%Y %H:%M")
        else: 
            dt = event.get('start').get('date')
            if "Z" in dt:
                dt = dt.replace('Z', '+00:00')
            dt = datetime.datetime.fromisoformat(dt)
            hkt = dt.astimezone(hkt)
            ukt = dt.astimezone(ukt)
            dt = dt.strftime("%A %d/%m/%Y")
            ukt = ukt.strftime("%A %d/%m/%Y")
            hkt = hkt.strftime("%A %d/%m/%Y")
        
        return event.get('summary'), ukt, hkt, event.get('htmlLink'), event.get('id')
        return f"Event: {event.get('summary')} on {dt}. Link: {event.get('htmlLink')}"

    except HttpError as error:
        print('An error occurred: %s' % error)
        return f"An error occurred: {error}"
    


def del_event(id):
    if type(id) == tuple:
        id = id[0]
    print("eid", id)
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        # Call the Calendar API
        service.events().delete(calendarId=calendar_id, eventId=id).execute()
        print('Event deleted: %s' % id)
        return f"Event {id} deleted"
    except HttpError as error:
        print('An error occurred: %s' % error)
        return f"An error occurred: {error}"



if __name__ == "__main__":
    del_event("6vb85ielh3hfdpprf02kq7a6fg")