from aiogram import Router, types, F
from aiogram.filters import Command
from asyncpg import Connection
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.callback_data.callbacks import TeamData, LeagueData, CommandData

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
    res = await conn.fetch('select team_id, team from team_stat where league = $1',
                           callback_data.league_name)
    builder = InlineKeyboardBuilder()
    for league in res:
        builder.add(types.InlineKeyboardButton(
            text=league[1], callback_data=TeamData(team_id=league[0]).pack()))
    builder.adjust(3)
    await call.message.answer(text='Выберите команду', reply_markup=builder.as_markup(resize_keyboard=True))


@router.message(Command("teams"))
async def get_whole_team_list(message: types.Message, conn: Connection):
    res = await conn.fetch("select team_id, team from team_stat")
    builder = InlineKeyboardBuilder()
    for team in res:
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
        'Команда': dict_data['team'],
        'Ссылка на команду': dict_data['team_link'],
        'Лига': dict_data['league'],
        'Победы': dict_data['victories'],
        'Максимальное количество побед': dict_data['max_victories'],
        'Очки': dict_data['points'],
        'Гандикап: победы/очки': dict_data['handicap'],
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
    await call.message.answer(f"Статистика команды:\n{team_data}", reply_markup=builder.as_markup(resize_keyboard=True))


@router.callback_query(CommandData.filter(F.cmd == 'schedule'))
async def get_league_teams(call: types.CallbackQuery, callback_data: CommandData, conn: Connection):
    game_data = []
    for match in await conn.fetch('select start_time, end_time, host, guest, location from schedule right join team_stat on '
                                  'team_stat.team = schedule.host or '
                                  'team_stat.team = schedule.guest where team_id = $1 or team_id = $1 ',
                                  int(callback_data.team_id)):
        dictio = {
            'Начало': match[0],
            'Конец': match[1],
            'Хозяева': match[2],
            'Гости': match[3],
            'Место проведения': match[4]
        }
        game_data.append('\n'.join(f'{key}: {val}' for key, val in dictio.items()))
    games_data = f'\n{30*"-"}\n'.join(game for game in game_data)
    await call.message.answer(text=f'Расписание матчей:\n{games_data}')
