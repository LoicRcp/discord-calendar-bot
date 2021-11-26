from __future__ import print_function
from datetime import datetime, timedelta
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dateutil import parser
import discord
from dotenv import load_dotenv
import os

load_dotenv(r'./.env')

SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events.owned', 'https://www.googleapis.com/auth/calendar.events.owned.readonly' ]

def login():
    creds = None

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

    service = build('calendar', 'v3', credentials=creds)

    return service

def addEvent(day, month, year, subject, description, start=12, duree=1):
    service = login()

    date = datetime(year, month, day, start)
    start = date.isoformat()
    end = (date + timedelta(hours=duree)).isoformat()

    event_result = service.events().insert(calendarId='39tnka5h3lgg91k7ukncsmbn14@group.calendar.google.com',
                                           body={
                                               "summary": subject,
                                               "description": description,
                                               "start": {"dateTime": start, "timeZone": 'Europe/Paris'},
                                               "end": {"dateTime": end, "timeZone": 'Europe/Paris'},
                                           }
                                           ).execute()

    print("created event")
    print("id: ", event_result['id'])
    print("summary: ", event_result['summary'])
    print("starts at: ", event_result['start']['dateTime'])
    print("ends at: ", event_result['end']['dateTime'])
    service.close()


def listEvent():
    service = login()

    now = datetime.now().isoformat() + 'z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='39tnka5h3lgg91k7ukncsmbn14@group.calendar.google.com', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = parser.parse(event['start'].get('dateTime', event['start'].get('date')))
        id = event['id']
        print(f"id: {id}\n"
              f"start: {start}\n"
              f"Titre: {event['summary']}\n\n")


    service.close()


def deleteEvent(id):
    service = login()

    try:
        service.events().delete(calendarId='39tnka5h3lgg91k7ukncsmbn14@group.calendar.google.com', eventId=id).execute()
    except:
        print("L'évènement n'existe pas...")
    service.close()
def showEvent(id):
    service = login()

    event = service.events().get(calendarId='39tnka5h3lgg91k7ukncsmbn14@group.calendar.google.com', eventId=id).execute()

    start = parser.parse(event['start'].get('dateTime', event['start'].get('date')))
    end = parser.parse(event['end'].get('dateTime', event['end'].get('date')))
    titre = event['summary']
    description = event['description']

    print(f"id: {id}\n"
          f"Titre: {titre}\n"
          f"Description: {description}\n"
          f"start: {start}\n"
          f"end: {end}")


    service.close()





client = discord.Client()

botToken = os.getenv('botToken')


@client.event
async def on_ready():

    botReady = True
    print("Bot ready !")


@client.event
async def on_message(message):
    if botReady:
        if message.content.startswith("!cal"):
            print("Working")

botReady = False
client.run(botToken)