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

    result = f"created event\n" \
             f"id: {event_result['id']}\n" \
             f"description: {event_result['summary']}\n" \
             f"starts at: {event_result['start']['dateTime']}\n" \
             f"ends at: {event_result['end']['dateTime']}"


    result = discord.Embed(title=event_result['summary'], description="Ajout r??ussi")
    result.set_author(name='Lxrry#3744',
                        icon_url="https://cdn.discordapp.com/attachments/913878490728783873/913881031675891752/er48r4.jpg")
    result.add_field(name="Description", value=event_result['description'],inline=False)
    result.add_field(name="ID", value=event_result['id'], inline=False)

    # print("created event")
    # print("id: ", event_result['id'])
    # print("summary: ", event_result['summary'])
    # print("starts at: ", event_result['start']['dateTime'])
    # print("ends at: ", event_result['end']['dateTime'])
    service.close()

    return result


def listEvent(nb):
    service = login()

    now = datetime.now().isoformat() + 'z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='39tnka5h3lgg91k7ukncsmbn14@group.calendar.google.com', timeMin=now,
                                          maxResults=nb, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    service.close()
    if not events:
        print('No upcoming events found.')
    else:
        return events

    # for event in events:
    #     start = parser.parse(event['start'].get('dateTime', event['start'].get('date')))
    #     id = event['id']
    #
    #
    #
    #     print(f"id: {id}\n"
    #           f"start: {start}\n"
    #           f"Titre: {event['summary']}\n\n")





def deleteEvent(id):
    service = login()

    try:
        service.events().delete(calendarId='39tnka5h3lgg91k7ukncsmbn14@group.calendar.google.com', eventId=id).execute()
    except:
        print("L'??v??nement n'existe pas...")
    service.close()
def showEvent(id):
    service = login()

    event = service.events().get(calendarId='39tnka5h3lgg91k7ukncsmbn14@group.calendar.google.com', eventId=id).execute()

    start = parser.parse(event['start'].get('dateTime', event['start'].get('date')))
    end = parser.parse(event['end'].get('dateTime', event['end'].get('date')))
    titre = event['summary']
    description = event['description']


    service.close()
    return event

    # print(f"id: {id}\n"
    #       f"Titre: {titre}\n"
    #       f"Description: {description}\n"
    #       f"start: {start}\n"
    #       f"end: {end}")


    # service.close()





client = discord.Client()

botToken = os.getenv('botToken')


@client.event
async def on_ready():
    global botReady
    botReady = True
    print("Bot ready !")


@client.event
async def on_message(message):
    if botReady:
        try:
            if message.content.startswith("!cal"):
                print(message.content)
                if "help" in message.content:

                    helpmess = discord.Embed(title="Aide CalendarBot",
                                             description= "Ce bot permet de consulter, ajouter ou supprimer facilement les diff??rents ??v??nements d'un calendrier.",
                                             color=0xFF5733)
                    helpmess.set_author(name='Lxrry#3744', icon_url="https://cdn.discordapp.com/attachments/913878490728783873/913881031675891752/er48r4.jpg")

                    helpmess.add_field(name="Le pr??fixe", value="`!cal` est le pr??fixe devant chaque commande du bot", inline=False)
                    helpmess.add_field(name="Afficher l'aide", value="Affiche ce message d'aide\n - !cal help", inline=False)
                    helpmess.add_field(name="Ajouter un ??v??nement", value="Ajoute un ??v??nement\n- !cal add\n\n ARGUMENTS:\n"
                                                                          "date: jj-mm-aaaa\n"
                                                                          "titre: Le titre de l'??v??nement\n"
                                                                          "desc: La description de l'??v??nement\n\n"
                                                                          "OPTIONNEL\n"
                                                                          "start: 14h\n"
                                                                          "duree: 2h", inline=False)
                    helpmess.add_field(name="Voir les ev??nements", value="Affiche la liste des X prochains ??v??nements (X est un nombre)\n"
                                                                         " - !cal all X", inline=False)
                    helpmess.add_field(name="Voir UN ev??nement en d??tail", value="Affiche les d??tails de l'??v??nement ayant l'id X\nAfficher la liste de tout les events pour avoir les ID"
                                                                         " - !cal show ID", inline=False)

                    helpmess.add_field(name="Supprimer un ??v??nement",
                                       value="Supprime l'??v??nement ayant l'id X\nAfficher la liste de tout les events pour avoir les ID"
                                             " - !cal del ID", inline=False)


                    await message.channel.send(embed=helpmess)
                    return
                if "all" in message.content:
                    nb = None
                    parts = message.content.split(" ")
                    for part in parts:
                        if part.isnumeric():
                            nb = int(part)

                    if nb == None:
                        nb = 1000
                    events = listEvent(nb)
                    messageToSend = discord.Embed(title="Listes des ??v??nements", color=0xFF5733)

                    messageToSend.set_author(name='Lxrry#3744', icon_url="https://cdn.discordapp.com/attachments/913878490728783873/913881031675891752/er48r4.jpg")
                    for event in events:
                        id = event['id']
                        start = parser.parse(event['start'].get('dateTime', event['start'].get('date')))
                        end = parser.parse(event['end'].get('dateTime', event['end'].get('date')))


                        titre = event['summary']
                        description = event['description']

                        messageToSend.add_field(name=titre, value=f"- Description: {description}\n"
                                                                  f"- D??but: {start.date()} - {start.time()}\n"
                                                                  f"- Fin: {end.date()} - {end.time()}\n"
                                                                  f"- ID: {id}",
                                                inline=False
                                                )

                        # messageToSend += f"id: {id}\n" \
                        #                 f"Titre: {titre}\n"\
                        #                 f"Description: {description}\n"\
                        #                 f"start: {start}\n"\
                        #                 f"end: {end}\n\n"

                    await message.channel.send(embed=messageToSend)
                    return

                if "add" in message.content:
                    temp = message.content
                    temp = temp.split('\n')

                    day = None
                    month = None
                    year = None
                    titre = None
                    desc = None
                    start = None
                    duree = None

                    for part in temp:
                        if "date" in part:

                            date = str.strip(part.split(':')[1]).split("-")
                            day = int(date[0])
                            month = int(date[1])
                            year = int(date[2])
                        if "titre" in part:

                            titre = str.strip(part.split(":")[1])
                        if "desc" in part:
                            desc = str.strip(part.split(":")[1])
                        if "start" in part:
                            start = int(str.strip(part.split(":")[1]).split("h")[0])
                        if "duree" in part:
                            duree = int(str.strip(part.split(":")[1]).split("h")[0])

                    if day != None and month != None and year != None and titre != None and desc != None:
                        if start != None and duree != None:
                            result = addEvent(day=day, month=month, year=year, subject=titre, description=desc, start=start, duree=duree)
                        else:
                            result = addEvent(day=day, month=month, year=year, subject=titre, description=desc)
                        await message.channel.send(embed=result)
                    else:
                        await message.channel.send("La commande est incompl??te...")

                if "del" in message.content:
                    temp = message.content.split(" ")
                    id = temp[-1]
                    deleteEvent(id)
                    await message.channel.send(f"Le message ayant pour ID: {id} ?? ??t?? supprim??.")
                if "show" in message.content:
                    temp = message.content.split(" ")
                    id = temp[-1]
                    event = showEvent(id)

                    messageToSend = discord.Embed(title="Listes des ??v??nements", color=0xFF5733)

                    messageToSend.set_author(name='Lxrry#3744',
                                             icon_url="https://cdn.discordapp.com/attachments/913878490728783873/913881031675891752/er48r4.jpg")

                    id = event['id']
                    start = parser.parse(event['start'].get('dateTime', event['start'].get('date')))
                    end = parser.parse(event['end'].get('dateTime', event['end'].get('date')))

                    titre = event['summary']
                    description = event['description']

                    messageToSend.add_field(name=titre, value=f"- Description: {description}\n"
                                                              f"- D??but: {start.date()} - {start.time()}\n"
                                                              f"- Fin: {end.date()} - {end.time()}\n"
                                                              f"- ID: {id}",
                                            inline=False
                                            )


                    await message.channel.send(embed=messageToSend)
        except Exception as e:
            print("Erreur: " + str(e))








botReady = False
client.run(botToken)