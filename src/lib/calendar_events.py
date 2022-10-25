"""
Getting latest events from Google Calendar
"""

import datetime
import frontmatter
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = '../service_account.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)


def get_events(calendar_id):
    """
    Getting latest events for a calendar_id
    """
    try:
        with build('calendar', 'v3', credentials=credentials) as service:
            # Call the Calendar API
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            print('Getting the upcoming 20 events')
            events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                                  maxResults=20, singleEvents=True,
                                                  orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                print('No upcoming events found.')
                return

            return events

    except HttpError as error:
        print(f'An error occurred: {error}')


def update_event_with_image(calendar_id, event_id, image_url):
    """
    Update the event with new informations
    """

    if image_url != "":
        try:
            with build('calendar', 'v3', credentials=credentials) as service:
                event_detail = service.events().get(calendarId=calendar_id,
                                                    eventId=event_id,
                                                    timeZone="Asia/Ho_Chi_Minh").execute()
                description = event_detail.get('description')
                start = event_detail.get('start').get('date')
                end = event_detail.get('end').get('date')

                print(event_detail)

                # if description[0] != "<":
                formatted = frontmatter.loads(description)

                price = (
                    f"price: {formatted['price']}" if "price" in formatted.keys() else "")
                publisher = (
                    f"publisher: {formatted['publisher']}" if "publisher" in formatted.keys(
                    ) else ""
                )

                description = f"""
                    ---
                    price: {price}
                    publisher: {publisher}
                    image_url: {image_url}
                    ---
                    {formatted.content}
                    """

                print(description)
                try:
                    with build('calendar', 'v3', credentials=credentials) as service:
                        service.events().update(calendarId=calendar_id,
                                                eventId=event_id,
                                                body={
                                                    "description": description,
                                                    "start": {"date": start, "timeZone": 'Asia/Ho_Chi_Minh'},
                                                    "end": {"date": end, "timeZone": 'Asia/Ho_Chi_Minh'},
                                                }).execute()
                        print("Done updating calendar entry")
                        print(event_detail)
                except HttpError as error:
                    print(f'An error occurred: {error}')
        except HttpError as error:
            print(f'An error occurred: {error}')
