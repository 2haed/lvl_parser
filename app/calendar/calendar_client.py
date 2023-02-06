from google.oauth2 import service_account
from googleapiclient.discovery import build


class GoogleCalendar:
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    FILE_PATH = 'calendar_info.json'

    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            filename=self.FILE_PATH, scopes=self.SCOPES
        )
        self.service = build('calendar', 'v3', credentials=credentials)

    def get_calendar_list(self):
        return self.service.calendarList().list().execute()

    def add_calendar(self, calendar_id):
        calendar_list_entry = {
            'id': calendar_id
        }
        return self.service.calendarList().insert(body=calendar_list_entry).execute()

    def add_event(self, calendar_id, body):
        return self.service.events().insert(calendarId=calendar_id, body=body).execute()

