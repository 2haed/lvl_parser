from aiogram.filters.callback_data import CallbackData


class TeamData(CallbackData, prefix="t"):
    team_id: int
    team_name: str = None


class LeagueData(CallbackData, prefix="league"):
    league_name: str


class CommandData(CallbackData, prefix="cmd_"):
    cmd: str
    team_name: str = None
    team_id: int

