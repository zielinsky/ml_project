from dataclasses import dataclass, asdict
from champions import *
from typing import Dict


@dataclass
class Player:
    name: str
    tag: str

    def get_opgg_name(self):
        new_name = self.name.replace(" ", "%20")
        return f"{new_name}-{self.tag}"

    def __hash__(self):
        return hash(self.get_opgg_name())


class Lane(Enum):
    TOP = 1
    JUNGLE = 2
    MID = 3
    ADC = 4
    SUPPORT = 5


lane_name_to_enum = {
    "top": Lane.TOP,
    "jungle": Lane.JUNGLE,
    "mid": Lane.MID,
    "adc": Lane.ADC,
    "support": Lane.SUPPORT,
}


class MatchResult(Enum):
    RED = 1
    BLUE = 2
    REMAKE = 3


class Tier(Enum):
    IRON = "iron"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    EMERALD = "emerald"
    DIAMOND = "diamond"
    MASTER = "master"
    GRANDMASTER = "grandmaster"
    CHALLENGER = "challenger"
    ALL = ""


class ChampionTier(Enum):
    TIER1 = 1
    TIER2 = 2
    TIER3 = 3
    TIER4 = 4
    TIER5 = 5


champion_tier_name_to_enum = {
    "5 Tier": ChampionTier.TIER5,
    "4 Tier": ChampionTier.TIER4,
    "3 Tier": ChampionTier.TIER3,
    "2 Tier": ChampionTier.TIER2,
    "1 Tier": ChampionTier.TIER1,
    "OP Tier": ChampionTier.TIER1,
}

champion_tier_enum_to_name = {
    value: key for key, value in champion_tier_name_to_enum.items()
}


@dataclass
class OpggMatch:
    team_red: list[(Player, Champion, Lane)]
    team_blue: list[(Player, Champion, Lane)]
    winner: MatchResult


@dataclass
class PlayerStatsOnChamp:
    player: Player
    champion: Champion
    mastery: int
    total_games_played: int
    win_rate: float
    kda_ratio: float
    average_gold_per_minute: float
    average_cs_per_minute: float


@dataclass
class PlayerInfo:
    player: Player
    overall_win_rate: float
    rank: str  # type Tier? ===========================================================================================
    total_games_played: int
    level: int
    last_twenty_games_kda_ratio: float
    last_twenty_games_kill_participation: float
    preferred_positions: list[(Lane, float)]
    last_twenty_games_win_rate: float

    def show(self):
        for key, value in asdict(self).items():
            print(f"{key} - {value}")


@dataclass
class ChampStats:
    champion: Champion
    lane: Lane
    champion_tier: ChampionTier
    win_rate: float
    ban_rate: float
    pick_rate: float
    match_up_win_rate: Dict[Champion, float]


@dataclass
class DataEntryForPlayer:
    player_mastery_on_champ: int
    player_wr_on_champ: float
    player_kda_ratio_on_champ: float
    player_gpm_on_champ: float
    player_cspm_on_champ: float
    player_overall_wr: float


@dataclass
class DataEntryTeam:
    total_mastery: int
    average_mastery: float
    average_player_wr: float
    average_champion_specific_player_wr: float
    average_champion_specific_match_up_wr: float


@dataclass
class ChampionEntry:
    tier: int
    wr: float
    br: float
    pr: float
    match_up_wr: float


@dataclass
class DataVector:
    match_result: MatchResult
    blue_team_players_entries: list[DataEntryForPlayer]
    blue_team_champions_entries: list[ChampionEntry]
    blue_team_team_entry: DataEntryTeam
    red_team_players_entries: list[DataEntryForPlayer]
    red_team_champions_entries: list[ChampionEntry]
    red_team_team_entry: DataEntryTeam
