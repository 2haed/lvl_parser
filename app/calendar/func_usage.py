import datetime
from aiogc import events, models
from app.calendar.calendar_client import GoogleCalendar
from app.config import settings

team_name = 'Основа'
opponent_name = 'Спартак'
location = 'метро Сокольники'
date_time = datetime.datetime.fromisoformat('2023-01-19 21:00:00.000000')

event = {
    'summary': f'{team_name} - {opponent_name}',
    'location': f'{location}',
    'description': f'Игра в любительской волейбольной лиге',
    'start': {
        'dateTime': f'{date_time.isoformat()}',
        'timeZone': 'Europe/Moscow',
    },
    'end': {
        'dateTime': f'{(date_time + datetime.timedelta(hours=2)).isoformat()}',
        'timeZone': 'Europe/Moscow'
    }
}
obj = GoogleCalendar()
obj.add_calendar(calendar_id=settings.calendar.calendar_id)
obj.add_event(calendar_id=settings.calendar.calendar_id, body=event)
