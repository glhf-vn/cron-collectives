from datetime import datetime, timedelta
from dateutil import tz
import os
from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from discord_webhook import DiscordWebhook, DiscordEmbed

load_dotenv()
webhook_url = os.environ.get('DISCORD_UPDATES_WEBHOOK')
google_key = os.environ.get('GOOGLE_API_KEY')


def get_the_events(calendarId):
    events_list = ''

    try:
        service = build('calendar', 'v3', developerKey=google_key)

        # Call the Calendar API
        today = datetime.utcnow().date()
        today = datetime(today.year, today.month, today.day,
                         tzinfo=tz.gettz('Asia/Ho_Chi_Minh'))
        today_utc = datetime(today.year, today.month, today.day,
                             tzinfo=tz.tzutc()).isoformat()  # 'Z' indicates UTC time
        tomorrow = today + timedelta(1)
        tomorrow_utc = tomorrow.isoformat()
        events_result = service.events().list(calendarId=calendarId, timeMin=today_utc, timeMax=tomorrow_utc,
                                              maxResults=20, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            # print('No upcoming events found.')
            return

        # Prints the start and name of the next 20 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            eid = event['htmlLink'].split('eid=')
            events_list += event['summary'] + '\n'

        return events_list

    except HttpError as error:
        print('An error occurred: %s' % error)


def webhooks(lists):
    current_date = datetime.date(datetime.now()).strftime("%d/%m/%Y")

    webhook = DiscordWebhook(url=webhook_url)
    embed = DiscordEmbed(
        title=f"Phát hành hôm nay - {current_date}",
        # color='fee304',
        url='https://manga.glhf.vn/'
    )
    embed.set_author(
        name="Lịch phát hành / manga.glhf.vn",
        url="https://manga.glhf.vn/",
        icon_url="https://res.cloudinary.com/glhfvn/image/upload/v1650536017/LOGO_shomth.png"
    )
    embed.set_thumbnail(
        url="https://res.cloudinary.com/glhfvn/image/upload/v1652066199/releases.png")
    embed.set_timestamp()

    if (all(entry['events'] == None for entry in lists)):
        return

    for publisher in lists:
        if (publisher['events'] != None):
            embed.add_embed_field(
                name=f'{publisher["icon"]} {publisher["name"]}', value=publisher['events'], inline=False)
    webhook.add_embed(embed)
    response = webhook.execute()


lists = [
    {
        'name': 'NXB Kim Đồng',
        'icon': '<:nxbkimdong:973132429483184138>',
        'events': get_the_events('kim0qh2rt2k3pts7mhs9pdf84s@group.calendar.google.com'),
    },
    {
        'name': 'NXB Trẻ',
        'icon': '<:nxbtre:973132427935502356>',
        'events': get_the_events('55vfna92d05k21up0brcmsbq0o@group.calendar.google.com'),
    },
    {
        'name': 'AMAK',
        'icon': '<:amak:973128525647319040>',
        'events': get_the_events('fjevdjbpr2m9r5gooaigs3595s@group.calendar.google.com'),
    },
    {
        'name': 'Hikari',
        'icon': '<:hikari:973132428715626516>',
        'events': get_the_events('d4oi2g1csqm6d2a0e71j6fpjuo@group.calendar.google.com'),
    },
    {
        'name': 'Ichi Light Novels',
        'icon': '<:ichiln:973132429147652106>',
        'events': get_the_events('s4m05q1nrpuq7p40ml2ct30jh8@group.calendar.google.com'),
    },
    {
        'name': 'IPM',
        'icon': '<:ipm:973127092004880444>',
        'events': get_the_events('7ht69okrmeph6snctucjn77vt0@group.calendar.google.com'),
    },
    {
        'name': 'SkyComics',
        'icon': '<:skycomics:973132403440758814>',
        'events': get_the_events('aammvnpdffcsq4oen8er6e6v10@group.calendar.google.com'),
    },
    {
        'name': 'Tsuki LightNovels',
        'icon': '<:tsuki:973132863228743730>',
        'events': get_the_events('5kjai0tie7kubu4nqls4j8e3uk@group.calendar.google.com'),
    },
    {
        'name': 'Uranix',
        'icon': '<:uranix:973132428656934962>',
        'events': get_the_events('5756jhpd8sj8doer4j39tsopl0@group.calendar.google.com'),
    },
    {
        'name': 'WingsBooks',
        'icon': '<:wingsbooks:973128536292474880>',
        'events': get_the_events('1eajtmaus1kib4s8mgd3cp82ho@group.calendar.google.com'),
    }
]

webhooks(lists)
