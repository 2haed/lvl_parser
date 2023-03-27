import asyncio
import copy
import logging
import re
import time
import warnings
import aiohttp
import asyncpg
from bs4 import BeautifulSoup
from app.config import settings
from app.parser.data.headers import HEADERS
from app.parser.data.headers import MOBILE_USER_AGENTS

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.basicConfig(filename='data/errors.log', format='%(asctime)s| %(message)s', datefmt='%m-%d-%Y %I:%M:%S',
                    level=logging.ERROR, encoding='UTF-8')


async def get_page_data(session: aiohttp.ClientSession, URL: str, connection_pool: asyncpg.Pool, headers: dict):
    async with session.get(URL, headers=headers) as response:
        try:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            tables = soup.find_all('table')[4]
            table = tables.find_all('table')[7]
            info = (' '.join(table.text.split()).split('Игрок'))
            if 'Тренер' in ' '.join(info):
                info = ' '.join(table.text.split()).split('Тренерский')[0].split('Игрок')
            team_info = info[0]
            players = info[2:]
            nums = re.findall(r'\b\d+\b', team_info)
            inf = {
                'team': ' '.join(team_info.split(':')[1].split()[:-1]),
                'avg_height': nums[-3],
                'avg_age': f'{nums[-2]}.{nums[-1]}'
            }
            for i in players:
                player = {
                    'team': ' '.join(team_info.split(':')[1].split()[:-1]),
                    'name': ' '.join(i.split(':')[1].split()[:-1]),
                    'height': i.split(':')[2].split()[0],
                    'skill_level': re.findall(r'[А-Я][а-я]*', i.split(':')[-2])[0].strip() if i.count(':') == 4 else
                    i.split(':')[
                        -1],
                    'birth_year': i.split(':')[-1].strip() if i.count(':') == 4 else 'NULL'
                }
                if '22/23' in info[0] and 'ДЛВЛ' not in info[0]:
                    async with connection_pool.acquire() as connection:
                        await connection.fetch(
                            'insert into public.players(team, name, height, skill_level, birth_year) '
                            'values ($1, $2, $3, $4, $5) on conflict (name) do update set name = excluded.name',
                            player['team'], player['name'], player['height'], player['skill_level'].strip(),
                            player['birth_year']
                        )
                    async with connection_pool.acquire() as connection:
                        await connection.fetch(
                            'insert into team_stat(team, avg_height, avg_age) '
                            'values ($1, $2, $3) on conflict (team) do update set team = excluded.team, '
                            'avg_height = excluded.avg_height, avg_age = excluded.avg_age',
                            inf['team'], int(inf['avg_height']), round(float(inf['avg_age']))
                        )

        except Exception as ex:
            logging.error(ex)
            # print(ex)


async def main():
    connection_pool = await asyncpg.create_pool(
        host=settings.database.host,
        database=settings.database.database,
        user=settings.database.user,
        password=settings.database.password
    )
    async with connection_pool.acquire() as connection:
        await connection.fetch(
            'create table if not exists players (player_id serial, team text, name text primary key, height text, '
            'skill_level text, birth_year text,'
            'foreign key (team) references team_stat (team));'
        )
    async with connection_pool.acquire() as connection:
        await connection.fetch(
            'alter table team_stat add column if not exists '
            'avg_height int, add column if not exists avg_age int;'
        )
    connector = aiohttp.TCPConnector(limit=50, force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for index, page_num in enumerate(range(7548, 8133)):
            URL = f'http://www.volleymsk.ru/ap/members.php?id={page_num}'
            new_headers = copy.deepcopy(HEADERS)
            new_headers['user-agent'] = MOBILE_USER_AGENTS[index % 10]
            tasks.append(asyncio.create_task(get_page_data(session, URL, connection_pool, new_headers)))
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())