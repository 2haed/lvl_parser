import psycopg2 as psycopg2
import requests
from bs4 import BeautifulSoup
import asyncio
import datetime
import warnings
import aiohttp
import asyncpg
from bs4 import BeautifulSoup
from app.config import settings
from app.parser.data.headers import HEADERS


# connection = psycopg2.connect(
#     host=settings.database.host,
#     database=settings.database.database,
#     user=settings.database.user,
#     password=settings.database.password
# )
#
# URL = 'http://www.volleymsk.ru/ap/members.php?id=7550'
# page = requests.get(URL, headers=HEADERS)
# soup = BeautifulSoup(page.content, 'html.parser')
# tables = soup.find_all('table')
# for table in tables:
#     if len(table) > 30:
#         for i in table:
#             print(' '.join(i.text.split()))
#
#
#
# warnings.filterwarnings("ignore", category=DeprecationWarning)


async def get_page_data(session: aiohttp.ClientSession, url: str, connection_pool: asyncpg.Pool, headers: dict):
    async with session.get(url, headers=headers) as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        tables = soup.find_all('table')
        for table in tables:
            if len(table) > 30:
                info = [' '.join(i.text.split()) for i in table]
                
                # member = {
                #     'date_time': f'{"-".join(row[0].text.split()[1].replace(",", "").split("-")[::-1])} {row[0].text.split()[2]}:00',
                #     'host': row[1].text,
                #     'guest': row[2].text,
                #     'location': row[3].text,
                # }
            # async with connection_pool.acquire() as connection:
            #     await connection.fetch(
            #         'insert into public.schedule(start_time, end_time, host, guest, location) values ($1, $2, $3, '
            #         '$4, $5) on conflict ( '
            #         'start_time, end_time, host, guest, location) do update set start_time = excluded.start_time',
            #         datetime.datetime.fromisoformat(match['date_time']),
            #         datetime.datetime.fromisoformat(match['date_time']) + datetime.timedelta(hours=2),
            #         match['host'], match['guest'], match['location']
            #     )


async def main():
    connection_pool = await asyncpg.create_pool(
        host=settings.database.host,
        database=settings.database.database,
        user=settings.database.user,
        password=settings.database.password
    )
    async with connection_pool.acquire() as connection:
        await connection.fetch(
            'create table IF NOT EXISTS team_members (team_name text, name text, height int, skill text, '
            'birthday int, foreign key (team_name) references team_stat (team));'
        )
        # await connection.fetch(
        #     'create unique index IF NOT EXISTS team_member_index '
        #     'on team_members (team_id, name, height, skill, birthday); '
        # )
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(7548, 8133):
            tasks.append(
                get_page_data(session, f'http://www.volleymsk.ru/ap/members.php?id={i}', connection_pool, HEADERS))
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())