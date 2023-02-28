import asyncio
import datetime
import warnings
import aiohttp
import asyncpg
from bs4 import BeautifulSoup
from app.config import settings
from app.parser.data.headers import HEADERS

warnings.filterwarnings("ignore", category=DeprecationWarning)


async def get_page_data(session: aiohttp.ClientSession, url: str, connection_pool: asyncpg.Pool, headers: dict):
    async with session.get(url, headers=headers) as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        table = soup.find('table', id='rasp')
        for tr in table.find_all('tr')[1:]:
            row = tr.find_all('td')
            match = {
                'date_time': f'{"-".join(row[0].text.split()[1].replace(",", "").split("-")[::-1])} {row[0].text.split()[2]}:00',
                'host': row[1].text,
                'guest': row[2].text,
                'location': row[3].text,
            }
            async with connection_pool.acquire() as connection:
                await connection.fetch(
                    'insert into public.schedule(start_time, end_time, host, guest, location) values ($1, $2, $3, '
                    '$4, $5) on conflict ( '
                    'start_time, end_time, host, guest, location) do update set start_time = excluded.start_time',
                    datetime.datetime.fromisoformat(match['date_time']),
                    datetime.datetime.fromisoformat(match['date_time']) + datetime.timedelta(hours=2),
                    match['host'], match['guest'], match['location']
                )


async def main():
    connection_pool = await asyncpg.create_pool(
        host=settings.database.host,
        database=settings.database.database,
        user=settings.database.user,
        password=settings.database.password
    )
    async with connection_pool.acquire() as connection:
        await connection.fetch(
            'create table IF NOT EXISTS schedule (start_time timestamp, '
            'end_time timestamp, host text, guest text, location text, '
            'foreign key (host) references team_stat (team), foreign key '
            '(guest) references team_stat (team));'
        )
        await connection.fetch(
            'create unique index IF NOT EXISTS schedule_date_time_host_guest_location_uindex '
            'on schedule (start_time, end_time, host, guest, location); '
        )
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(1367, 1401):
            tasks.append(
                get_page_data(session, f'http://www.volleymsk.ru/ap/rasp.php?id={i}', connection_pool, HEADERS))
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())