import asyncio
import re
import warnings
import aiohttp
import asyncpg
from bs4 import BeautifulSoup
from config import settings
from data.contsants import HEADERS

warnings.filterwarnings("ignore", category=DeprecationWarning)


async def get_page_data(session: aiohttp.ClientSession, URL: str, connection_pool: asyncpg.Pool, headers: dict):
    async with session.get(URL, headers=headers) as response:
        try:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            tables = soup.find_all('table')[4]
            table = tables.find_all('table')[7]
            info = (' '.join(table.text.split()).split('Игрок'))
            team_info = info[0]
            players = info[2:]
            nums = re.findall(r'\b\d+\b', team_info)
            inf = {
                'Команда': ' '.join(team_info.split(':')[1].split()[:-1]),
                'Рост': nums[-3],
                'Возраст': f'{nums[-2]}.{nums[-1]}'
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
                async with connection_pool.acquire() as connection:
                    await connection.fetch(
                        'insert into public.players(team, name, height, skill_level, birth_year) '
                        'values ($1, $2, $3, $4, $5) on conflict (name) do update set name = excluded.name',
                        player['team'], player['name'], player['height'], player['skill_level'],
                        player['birth_year'],
                    )
        except Exception as ex:
            print(ex)
            print()
            print(URL)


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
        row = await connection.fetch('select team_link from team_stat')
    async with aiohttp.ClientSession() as session:
        tasks = []
        for page_num in range(7548, 8133):
            URL = f'http://www.volleymsk.ru/ap/members.php?id={page_num}'
            tasks.append(asyncio.create_task(get_page_data(session, URL, connection_pool, HEADERS)))
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
