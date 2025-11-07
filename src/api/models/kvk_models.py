from dataclasses import asdict, dataclass
from enum import Enum
from datetime import datetime
from typing import Any

type link = str

@dataclass
class JSONSeriazableDataclass:
    def to_json(self):
        return asdict(self)

@dataclass
class Scenario:
    rank: int
    leaderboardId: int
    scenarioName: str
    aimType: str
    authors: list[str]
    description: str
    plays: int
    entries: int

@dataclass
class Score:
    steamId: str
    rank: int
    steamAccountName: str
    kovaaksPlusActive: bool
    fov: int
    hash: str
    cm360: float
    epoch: int
    kills: int
    score: float
    avgFps: float
    avgTtk: float
    fovScale: str
    vertSens: float
    horizSens: float
    resolution: str
    sensScale: str
    accuracyDamage: int
    challengeStart: datetime
    scenarioVersion: str
    clientBuildVersion: str
    webappUsername: str

@dataclass
class PlayerSearchResult:
    username: str
    avatar: str

@dataclass
class PlaylistScenario:
    scenarioName: str
    playCount: int

@dataclass
class Playlist:
    playlistName: str
    playlistCode: str
    playlistId: int
    authorName: str
    description: str
    scenarioList: list[PlaylistScenario]
    authorSteamId: str
    subscribers: str
    webappUsername: str
    steamAccountName: str

@dataclass
class Profile:
    playerId: int
    username: str
    created: datetime
    steamId: str
    clientBuildVersion: str
    lastAccess: datetime
    steamAccountName: str
    steamAccountAvatar: str
    admin: bool
    coach: bool
    staff: bool
    videos: list[str]
    # ...
    
@dataclass
class BenchmarkRank:
    icon: str
    name: str
    color: str
    frame: link
    description: str
    playercard_large: link
    playercard_small: link


@dataclass
class BenchmarkScenario:
    score: int
    leaderboard_rank: int
    scenario_rank: int
    rank_maxes: list[int]
    leaderboard_id: int

@dataclass
class BenchmarkCategory:
    benchmark_progress: int
    category_rank: int
    rank_maxes: list[int]
    scenarios: dict[str, BenchmarkScenario]


@dataclass
class Benchmark(JSONSeriazableDataclass):
    benchmark_progress: int
    overall_rank: int
    categories: dict[str, BenchmarkCategory]
    ranks: list[BenchmarkRank]
    

'''
For example:
{
    "voltaic-begin": ["Iron": 10.1],
    "viscose": ["Celadon": 10.1]
}
'''
@dataclass
class RankPercentiles(list[Benchmark]):
    pass


class LeaderboardFilter(Enum):
    GLOBAL = 1
    VIP = 2
    FRIENDS = 3
    MY_POSITION = 4

class UnsupportedFilter(Exception): pass
class NoCredentials(Exception): pass
