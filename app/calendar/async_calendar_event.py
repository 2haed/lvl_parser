import asyncio
import datetime
import warnings

from google.oauth2 import service_account
import aiohttp

from aiogc import events, models, Time
from googleapiclient.discovery import build

from config import settings

warnings.filterwarnings("ignore", category=DeprecationWarning)

credentials = service_account.Credentials.from_service_account_file(filename='calendar_info.json',
                                                                    scopes=['https://www.googleapis.com/auth/calendar'],
                                                                    )
service = build('calendar', 'v3', credentials=credentials)
team_name = 'Основа'
opponent_name = 'Спартак'
location = 'метро Сокольники'
date_time_start = Time('2023-02-06 21:00:00')
date_time_end = Time('2023-02-06 23:00:00')


async def main():
    async with aiohttp.ClientSession() as session:
        event = models.Event(
            summary=f'{team_name} - {opponent_name}',
            location=f'{location}',
            start=date_time_start,
            end=date_time_end,
        )
        await events.insert(
            calendar_id=settings.calendar.calendar_id,
            event=event,
            session=session,
            credentials=credentials,
        )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
