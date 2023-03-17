import asyncio
import copy
import logging
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
            row = soup.find_all('td', class_='normaltext')
            all_teams = []
            if 250 < len(row) < 400:
                for i in range(14, 150, 14):
                    if row[i + 1].text != 'Команда':
                        league = ' '.join(''.join(soup.find('h1').text.replace(':::', '').split('>')[3]).split())
                        team = {
                            'team': row[i + 1].text,
                            'league': league if ":" not in league else league.split(':')[0],
                            'team_link': f"http://www.volleymsk.ru{row[i + 1].find('a').get('href')}" if row[
                                                                                                             i + 1].find(
                                'a') is not None else None,
                            'victories': row[i + 2].text,
                            'max_victories': row[i + 3].text,
                            'points': row[i + 4].text,
                            'handicap': row[i + 5].text,
                            'three_zero_three_one': row[i + 6].text,
                            'three_two': row[i + 7].text,
                            'two_three': row[i + 8].text,
                            'one_three_zero_three': row[i + 9].text,
                            'match_points': row[i + 10].text,
                            'match_ratio': row[i + 11].text,
                            'balls': row[i + 12].text,
                            'balls_ratio': row[i + 13].text,
                        }
                        all_teams.append(team)
                    async with connection_pool.acquire() as connection:
                        await connection.fetch(
                            'insert into public.team_stat(team, league, team_link, victories, max_victories, points, '
                            'handicap, three_zero_three_one, three_two, two_three, '
                            'one_three_zero_three, match_points, match_ratio, balls,'
                            'balls_ratio) values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, '
                            '$11, $12, $13, $14, $15) on conflict (team) do update set '
                            'team = excluded.team', team['team'], team['league'], team['team_link'],
                            int(team['victories']),
                            int(team['max_victories']), int(team['points']), team['handicap'],
                            int(team['three_zero_three_one']),
                            int(team['three_two']), int(team['two_three']),
                            int(team['one_three_zero_three']), team['match_points'], team['match_ratio'],
                            team['balls'], team['balls_ratio']
                        )
        except Exception as ex:
            logging.error(ex)
            print(URL, ex)


async def main():
    connection_pool = await asyncpg.create_pool(
        host=settings.database.host,
        database=settings.database.database,
        user=settings.database.user,
        password=settings.database.password
    )
    async with connection_pool.acquire() as connection:
        await connection.fetch(
            'create table IF NOT EXISTS public.team_stat (team_id serial not null , team text not null, league text, '
            'team_link text not null , victories int,'
            'max_victories int, points int, handicap text, three_zero_three_one int, three_two int, two_three int,'
            'one_three_zero_three '
            'int, match_points text, '
            'match_ratio text, balls text, balls_ratio text, primary key (team));')
    connector = aiohttp.TCPConnector(limit=50, force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for index, page_num in enumerate(range(1367, 1401)):
            new_headers = copy.deepcopy(HEADERS)
            new_headers['user-agent'] = MOBILE_USER_AGENTS[index % 10]
            URL = f'http://www.volleymsk.ru/ap/trntable.php?trn={page_num}'
            tasks.append(asyncio.create_task(get_page_data(session, URL, connection_pool, new_headers)))
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
