import re

import psycopg2 as psycopg2
import requests
from bs4 import BeautifulSoup

from app.config import settings
from app.parser.data.headers import HEADERS
from app.parser.data.headers import MOBILE_USER_AGENTS

URL = 'http://www.volleymsk.ru/ap/members.php?id=7548'
lastURL = 'http://www.volleymsk.ru/ap/members.php?id=7983'
page = requests.get(lastURL, headers=HEADERS)
soup = BeautifulSoup(page.content, 'html.parser')
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
print(players)
for i in players:
    player = {
        'Команда': ' '.join(team_info.split(':')[1].split()[:-1]),
        'ФИО': ' '.join(i.split(':')[1].split()[:-1]),
        'Рост': i.split(':')[2].split()[0],
        'Мастерство': re.findall(r'[А-Я][а-я]*', i.split(':')[-2])[0] if i.count(':') == 4 else i.split(':')[-1],
        'Год рождения': i.split(':')[-1].strip() if i.count(':') == 4 else None
    }
    print(player)
for k, v in inf.items():
    print(k, ':', type(v))
print(float(inf['Возраст']))