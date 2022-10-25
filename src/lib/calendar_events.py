"""
Getting latest events from Google Calendar
"""

import os.path
import datetime
import frontmatter
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(ROOT_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(ROOT_DIR, 'token.json')


def authenticate():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds


def get_events(calendar_id):
    """
    Getting latest events for a calendar_id
    """
    creds = authenticate()
    try:
        with build('calendar', 'v3', credentials=creds) as service:
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


def update_event_with_image(calendar_id, event_id, image_url, publisher):
    """
    Update the event with new informations
    """

    creds = authenticate()

    if image_url != "":
        try:
            with build('calendar', 'v3', credentials=creds) as service:
                event = service.events().get(calendarId=calendar_id,
                                             eventId=event_id).execute()

                # if description[0] != "<":
                formatted = frontmatter.loads(event.get('description'))

                price = (
                    f"price: {formatted['price']}" if "price" in formatted.keys() else "")

                event['description'] = f"""---\n{price}\npublisher: {publisher}\nimage_url: {image_url}\n---"""

                updated_event = service.events().update(calendarId=calendar_id,
                                                        eventId=event['id'],
                                                        body=event).execute()
                print(
                    f"Done updating calendar entry\n{updated_event['updated']}")
        except HttpError as error:
            print(f'An error occurred: {error}')
