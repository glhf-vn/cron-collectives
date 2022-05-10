import datetime
import requests
import io
import re
import os
from dotenv import load_dotenv
from sys import exit
from PIL import Image
import argparse

from discord_webhook import DiscordWebhook, DiscordEmbed

import cloudinary
from cloudinary.uploader import upload
from cloudinary.api import resource
from cloudinary.utils import cloudinary_url

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


load_dotenv()
webhook_url = os.environ.get('DISCORD_UPDATES_WEBHOOK')
c_name = os.environ.get('CLOUDINARY_NAME')
c_key = os.environ.get('CLOUDINARY_KEY')
c_secret = os.environ.get('CLOUDINARY_SECRET')
google_key = os.environ.get('GOOGLE_API_KEY')

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

cloudinary.config(cloud_name=c_name, api_key=c_key, api_secret=c_secret)

# as per recommendation from @freylis, compile once only
CLEANR = re.compile('<.*?>')


def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext


def webhooks(title, description, release_date, url):
    publisher = cleanhtml(description.split("Nhà xuất bản")[1].split(":")[
                          1].split("Giá dự kiến")[0]).lstrip()
    price = cleanhtml(description.split("Giá dự kiến")
                      [1].split(":")[1]).lstrip()

    webhook = DiscordWebhook(url=webhook_url)
    embed = DiscordEmbed(
        title=title,
        url='https://manga.glhf.vn/'
    )
    embed.set_author(
        name="Cập nhật ảnh bìa / manga.glhf.vn",
        url="https://manga.glhf.vn/",
        icon_url="https://res.cloudinary.com/glhfvn/image/upload/v1650536017/LOGO_shomth.png"
    )
    embed.set_image(url=url)
    embed.add_embed_field(name="Nhà xuất bản", value=publisher, inline=False)
    embed.add_embed_field(name="Ngày phát hành", value=release_date)
    embed.add_embed_field(name="Giá dự kiến", value=price)
    embed.set_timestamp()

    webhook.add_embed(embed)
    response = webhook.execute()


def upload_cover(eid):
    print("Begin uploading? [y/N/stop] ")
    prompt = input()

    if (prompt in ['y', 'Y', 'yes']):
        buffer = io.BytesIO()
        size = 1000, 1000

        print("Enter the url: ")
        source_url = input()

        with Image.open(requests.get(source_url, stream=True).raw) as im:
            im.thumbnail(size)
            im.save(buffer, format='JPEG', quality=90)
            response = upload(
                buffer.getvalue(),
                public_id="covers/" + eid,
                eager=dict(
                    height=800,
                    crop="scale"
                ),
            )

            url, options = cloudinary_url(
                response['public_id'],
                format=response['format'],
            )

            print(f"Complete uploading, url: {url}\n")
            return True

    elif (prompt in ["n", "N", "no"]):
        print("Pass, continue to check\n")
        return False

    else:
        exit()


def get_events(calendarId):
    try:
        service = build('calendar', 'v3', developerKey=google_key)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        #now = "2022-05-15T00:00:00.000Z"
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId=calendarId, timeMin=now,
                                              maxResults=20, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        # Prints the start and name of the next 20 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            eid = event['htmlLink'].split('eid=')
            print(f"[{start}] {event['summary']}")
            url, options = cloudinary_url(
                "covers/" + eid[1],
                format="jpg",
                crop="fit"
            )
            try:
                # If the covers with eid exists
                resource("covers/" + eid[1])
                print(f'Already uploaded: {url}\n')
            except:
                # Upload the cover (successfully), then run the webhook. Else cancel the job
                if upload_cover(eid[1]):
                    webhooks(event['summary'], event['description'],
                             event['start']['date'], url)

    except HttpError as error:
        print('An error occurred: %s' % error)


events = {
    'kim': 'kim0qh2rt2k3pts7mhs9pdf84s@group.calendar.google.com',
    'tre': '55vfna92d05k21up0brcmsbq0o@group.calendar.google.com',
    'ipm': '7ht69okrmeph6snctucjn77vt0@group.calendar.google.com',
    'amak': 'fjevdjbpr2m9r5gooaigs3595s@group.calendar.google.com',
    'sky': 'aammvnpdffcsq4oen8er6e6v10@group.calendar.google.com',
    'tsuki': '5kjai0tie7kubu4nqls4j8e3uk@group.calendar.google.com',
    'uranix': '5756jhpd8sj8doer4j39tsopl0@group.calendar.google.com',
    'wings': '1eajtmaus1kib4s8mgd3cp82ho@group.calendar.google.com',
    'hikari': 'd4oi2g1csqm6d2a0e71j6fpjuo@group.calendar.google.com',
    'ichi': 's4m05q1nrpuq7p40ml2ct30jh8@group.calendar.google.com'
}


parser = argparse.ArgumentParser(
    description='Upload cover to the CDN.')
parser.add_argument(
    "--calendar", help=f"Get the releases of a calendar. Available params: {list(events.keys())}", type=str, required=True)
args = parser.parse_args()


if events.get(args.calendar) != None:
    get_events(events.get(args.calendar))
else:
    print("Calendar not found, please try again")
