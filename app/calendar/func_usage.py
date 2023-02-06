import datetime

from app.calendar.calendar_client import GoogleCalendar
from config import settings

team_name = 'Основа'
opponent_name = 'Спартак'
location = 'метро Сокольники'
date_time = datetime.datetime.fromisoformat('2023-01-19 21:00:00.000000')

print(date_time)

event = {
    'summary': f'{team_name} - {opponent_name}',
    'location': f'{location}',
    'start': {
        'dateTime': f'{date_time}',
        'timeZone': 'Europe/Moscow',
    },
    'end': {
        'dateTime': f'{date_time}',
        'timeZone': 'Europe/Moscow'
    }
}
obj = GoogleCalendar()
obj.add_event(calendar_id=settings.calendar.calendar_id, body=event)
