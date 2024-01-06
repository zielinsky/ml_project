from dataclasses import dataclass
from enum import Enum


@dataclass
class Player:
    name: str
    tag: str

    def get_opgg_name(self):
        new_name = self.name.replace(" ", "%20")
        return f"{new_name}-{self.tag}"


class Lanes(Enum):
    TOP = 1
    JUNGLE = 2
    MID = 3
    ADC = 4
    SUPPORT = 5


class MatchResult(Enum):
    RED = 1
    BLUE = 2
    REMAKE = 3


class Tier(Enum):
    IRON = 'iron'
    BRONZE = 'bronze'
    SILVER = 'silver'
    GOLD = 'gold'
    PLATINUM = 'platinum'
    EMERALD = 'emerald'
    DIAMOND = 'diamond'
    MASTER = 'master'
    GRANDMASTER = 'grandmaster'
    CHALLENGER = 'challenger'
    ALL = ''

@dataclass
class Opgg_match:
    team_red: list[((Player, str), Lanes)]  # [((Player, Champion), Line))]
    team_blue: list[((Player, str), Lanes)]
    winner: MatchResult
    # kills : int
    # deaths : int
    # assists : int
    # damage_dealt : int
    # total_gold_earned : int
    # cs_per_minute : float


@dataclass
class Player_info:
    player: Player
    overall_win_rate: float
    rank: str
    total_games_played: int
    level: int
    last_twenty_games_kda_ratio: float
    last_twenty_games_kill_participation: int
    preferred_positions: list[(Lanes, int)]
    last_twenty_games_win_rate: float


@dataclass
class Player_stats_on_champ:
    champion: str
    total_games_played: int
    win_rate: float
    kda_ratio: float
    average_gold_per_minute: float
    average_cs_per_minute: float


@dataclass
class Champ_stats:
    tier: int
    win_rate: float
    ban_rate: float
    pick_rate: float
    matchup_win_rate: list[(str, float)]
