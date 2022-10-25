"""
Getting events, and uploading to the database
"""
import os
import sys
import argparse
from dotenv import load_dotenv

import cloudinary
from cloudinary.api import resource
from cloudinary.utils import cloudinary_url

from lib.discord_webhook import send_cover_webhook
from lib.calendar_events import get_events, update_event_with_image
from lib.cloudinary_upload import upload_cover


load_dotenv()
WEBHOOK_URL = os.environ.get('DISCORD_UPDATES_WEBHOOK')

cloudinary.config(cloud_name=os.environ.get('CLOUDINARY_NAME'),
                  api_key=os.environ.get('CLOUDINARY_KEY'),
                  api_secret=os.environ.get('CLOUDINARY_SECRET'))

CALENDARS = {
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
    description='Upload cover to the CDN, then push the notification on Discord')
parser.add_argument(
    "calendar",
    metavar="calendar_name",
    help=f"Get the releases of a calendar. Available params: {list(CALENDARS.keys())}",
    type=str)
parser.add_argument(
    "--webhook",
    help="Push the notification on Discord?",
    type=bool,
    default=False)
args = parser.parse_args()


def main():
    "Main function"
    calendar_id = CALENDARS.get(args.calendar)
    if calendar_id is not None:
        # Get the upcoming 20 events from Google Calendar
        events = get_events(calendar_id)

        # Prints the start and name of the next 20 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_id = event['id']

            # [time] title
            print(f"[{start}] {event['summary']}")

            url = cloudinary_url(
                "covers/" + event_id,
                format="jpg",
                crop="fit"
            )
            try:
                # If the covers with id exists
                resource("covers/" + event_id)
                print(f'Already uploaded: {url}\n')
            except cloudinary.exceptions.NotFound:
                # Upload the cover (successfully), then run the webhook. Else cancel the job
                print("Begin uploading? [y/N/stop] ")
                prompt = input()

                if (prompt in ['y', 'Y', 'yes']):
                    print("Enter the url: ")
                    source_url = input()

                    # upload image here
                    try:
                        image_url = upload_cover(event_id, source_url)[0]
                        if args.webhook is True:
                            send_cover_webhook(WEBHOOK_URL,
                                               event['summary'],
                                               event['start']['date'],
                                               image_url)
                        update_event_with_image(calendar_id=calendar_id,
                                                event_id=event_id,
                                                image_url=image_url)
                    except Exception as exc:
                        raise exc

                elif (prompt in ["n", "N", "no"]):
                    print("Pass, continue to check\n")

                else:
                    sys.exit()

    else:
        print("Calendar not found, please try again")


if __name__ == "__main__":
    main()
