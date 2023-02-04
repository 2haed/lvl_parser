import asyncio
import datetime
import warnings
import aiohttp
import asyncpg
from bs4 import BeautifulSoup
from config import settings
from app.data.contsants import HEADERS

warnings.filterwarnings("ignore", category=DeprecationWarning)


async def get_page_data(session: aiohttp.ClientSession, URL: str, connection_pool: asyncpg.Pool, headers: dict):
    async with session.get(URL, headers=headers) as response:
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
                    'insert into public.schedule(date_time, host, guest, location) values ($1, $2, $3, $4) on conflict ('
                    'date_time, host, guest, location) do update set date_time = excluded.date_time',
                    datetime.datetime.fromisoformat(match['date_time']), match['host'], match['guest'], match['location']
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
            'create table IF NOT EXISTS schedule (date_time timestamp, host text, guest text, location text, foregin key (host) references team (name), foreign key (guest) references team (name));'
        )
        await connection.fetch(
            'create unique index IF NOT EXISTS schedule_date_time_host_guest_location_uindex on schedule (date_time, '
            'host, guest, location); '
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
