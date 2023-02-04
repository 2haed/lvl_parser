import psycopg2 as psycopg2
import requests
import pandas as pd
from bs4 import BeautifulSoup

from config import settings
from app.data.contsants import HEADERS

connection = psycopg2.connect(
    host=settings.database.host,
    database=settings.database.database,
    user=settings.database.user,
    password=settings.database.password
)

URL = 'http://www.volleymsk.ru/ap/team.php?id=948'
page = requests.get(URL, headers=HEADERS)
soup = BeautifulSoup(page.content, 'html.parser')
.