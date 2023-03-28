from aiogram import Router, types, F
from aiogram.filters import Command
from asyncpg import Connection
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hlink, hbold
from app.config import settings
from app.bot.callback_data.callbacks import TeamData, LeagueData, CommandData
from app.calendar.calendar_client import GoogleCalendar

router = Router()


@router.message(Command("leagues"))
async def get_leagues(message: types.Message, conn: Connection):
    res = await conn.fetch("select distinct league from team_stat order by league")
    builder = InlineKeyboardBuilder()
    for league in res:
        builder.add(types.InlineKeyboardButton(
            text=league[0], callback_data=LeagueData(league_name=league[0]).pack()))
    builder.adjust(3)
    return await message.answer("Выберите лигу", reply_markup=builder.as_markup(resize_keyboard=True))


@router.callback_query(LeagueData.filter())
async def get_league_teams(call: types.CallbackQuery, callback_data: LeagueData, conn: Connection):
    res = await conn.fetch('select team_id, team from team_stat where league = $1 order by 2',
                           callback_data.league_name)
    builder = InlineKeyboardBuilder()
    for league in res:
        builder.add(types.InlineKeyboardButton(
            text=league[1], callback_data=TeamData(team_id=league[0]).pack()))
    builder.adjust(3)
    await call.message.answer(text='Выберите команду', reply_markup=builder.as_markup(resize_keyboard=True))


@router.message(Command("teams"))
async def get_whole_team_list(message: types.Message, conn: Connection):
    res = await conn.fetch("select team_id, team from team_stat order by 2")
    builder = InlineKeyboardBuilder()
    for team in sorted(res):
        builder.add(types.InlineKeyboardButton(
            text=team[1],
            callback_data=TeamData(team_id=int(team[0])).pack()))
    builder.adjust(3)
    return await message.answer("Выберите команду", reply_markup=builder.as_markup(resize_keyboard=True))


@router.callback_query(TeamData.filter())
async def get_team_info(call: types.CallbackQuery, callback_data: TeamData, conn: Connection):
    dict_data = dict(
        await conn.fetchrow('select * from team_stat where team_id = $1', int(callback_data.team_id)))
    new_dict = {
        'Команда': hlink(dict_data['team'], dict_data['team_link']),
        'Лига': hbold(dict_data['league']),
        'Средний рост': hbold(str(dict_data['avg_height']) + ' см'),
        'Средний возраст': hbold(str(dict_data['avg_age']) + ' лет'),
        'Победы': hbold(dict_data['victories']),
        'Очки': hbold(dict_data['points']),
        'Максимальное количество побед': dict_data['max_victories'],
        'Гандикап: победы/очки': (dict_data['handicap']),
        'Игры 3-0/3-1': dict_data['three_zero_three_one'],
        'Игры 3-2': dict_data['three_two'],
        'Игры 2-3': dict_data['two_three'],
        'Игры 1-3/0-3': dict_data['one_three_zero_three'],
        'Партии': dict_data['match_points'],
        'Соотношение партий': dict_data['match_ratio'],
        'Мячи': dict_data['balls'],
        'Соотношение мячей': dict_data['balls_ratio']
    }
    team_data = '\n'.join(f'{key}: {val}' for key, val in new_dict.items())
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text='Показать состав команды',
        callback_data=CommandData(team_id=int(dict_data['team_id']), cmd='mem').pack()
    ), types.InlineKeyboardButton(
        text='Показать расписание игр команды',
        callback_data=CommandData(team_id=int(dict_data['team_id']), cmd='schedule').pack()
    ))
    builder.adjust(1)
    await call.message.answer(f"Статистика команды:"
                              f"\n{team_data}", reply_markup=builder.as_markup(resize_keyboard=True))


@router.callback_query(CommandData.filter(F.cmd == 'schedule'))
async def get_schedule(call: types.CallbackQuery, callback_data: CommandData, conn: Connection):
    game_data = []
    for match in await conn.fetch('select start_time, end_time, location, host.team, host.team_link, guest.team, '
                                  'guest.team_link from schedule as s '
                                  'join team_stat as host on s.host = host.team '
                                  'join team_stat as guest on s.guest = guest.team '
                                  'where guest.team_id = $1 or host.team_id = $1;',
                                  int(callback_data.team_id)):
        dictio = {
            'Начало': match[0].strftime("%b-%d %H:%M"),
            'Конец': match[1].strftime("%b-%d %H:%M"),
            'Хозяева': hlink(match[3], match[4]),
            'Гости': hlink(match[5], match[6]),
            'Место проведения': hlink(match[2], f'https://yandex.ru/maps/?text={match[2]}')
        }
        game_data.append('\n'.join(f'{key}: {val}' for key, val in dictio.items()))
    games_data = f'\n{30 * "-"}\n'.join(game for game in game_data)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='Добавить игры в календарь',
                                           callback_data=CommandData(team_id=int(callback_data.team_id),
                                                                     cmd='add_all').pack()
                                           ))
    builder.adjust(1)
    await call.message.answer(text=f'Расписание матчей:\n{games_data}',
                              reply_markup=builder.as_markup(resize_keyboard=True))


@router.callback_query(CommandData.filter(F.cmd == 'add_all'))
async def insert_events(call: types.CallbackQuery, callback_data: CommandData, conn: Connection):
    obj = GoogleCalendar()
    for match in await conn.fetch('select start_time, end_time, location, host.team, host.team_link, guest.team, '
                                  'guest.team_link from schedule as s '
                                  'join team_stat as host on s.host = host.team '
                                  'join team_stat as guest on s.guest = guest.team '
                                  'where guest.team_id = $1 or host.team_id = $1;',
                                  int(callback_data.team_id)):
        event = {
            'summary': f'{match[3]} против {match[5]}',
            'location': f'{match[2]}',
            'description': f'Игра в любительской волейбольной лиге',
            'start': {
                'dateTime': f'{match[0].isoformat()}',
                'timeZone': 'Europe/Moscow',
            },
            'end': {
                'dateTime': f'{match[1].isoformat()}',
                'timeZone': 'Europe/Moscow'
            }
        }
        obj.add_calendar(settings.calendar.calendar_id)
        obj.add_event(calendar_id=settings.calendar.calendar_id, body=event)
    await call.message.answer(text=f'Календарь обновлен!')


@router.callback_query(CommandData.filter(F.cmd == 'mem'))
async def get_league_teams(call: types.CallbackQuery, callback_data: CommandData, conn: Connection):
    res = await conn.fetch('select name, height, skill_level, birth_year from players join team_stat ts on '
                           'players.team = ts.team where ts.team_id = $1',
                           int(callback_data.team_id))

    if 'NULL' not in ' '.join(res[0]):
        players_data = f'\n{30 * "-"}\n'.join(
            f'Имя: {hbold(game[0])}\nРост: {hbold(game[1])}'
            f'\nМастерство: {hbold(game[2])}\nГод рождения: {hbold(game[3])}'
            for game in res)
    else:
        players_data = f'\n{30 * "-"}\n'.join(
            f'Имя: {hbold(game[0])}\nРост: {hbold(game[1])}\nМастерство: {hbold(game[2])}'
            for game in res)
    await call.message.answer(text=f'Состав команды:\n{players_data}')
