from dataclasses import dataclass
from enum import Enum


MATCH_WIN_SCORE = 3


class RoundEndReason(Enum):
    KO = "ko"
    TIMEOUT = "timeout"
    DRAW = "draw"


@dataclass(frozen=True)
class RoundResult:
    winner_index: int | None
    reason: RoundEndReason

    @property
    def score_delta(self) -> tuple[int, int]:
        if self.winner_index == 0:
            return (1, 0)
        if self.winner_index == 1:
            return (0, 1)
        return (0, 0)


def resolve_round(
    player_1_health: int,
    player_2_health: int,
    time_expired: bool = False,
) -> RoundResult | None:
    player_1_ko = player_1_health <= 0
    player_2_ko = player_2_health <= 0

    if player_1_ko and player_2_ko:
        return RoundResult(None, RoundEndReason.DRAW)
    if player_1_ko:
        return RoundResult(1, RoundEndReason.KO)
    if player_2_ko:
        return RoundResult(0, RoundEndReason.KO)

    if not time_expired:
        return None

    if player_1_health > player_2_health:
        return RoundResult(0, RoundEndReason.TIMEOUT)
    if player_2_health > player_1_health:
        return RoundResult(1, RoundEndReason.TIMEOUT)
    return RoundResult(None, RoundEndReason.DRAW)


def apply_score(score: list[int], result: RoundResult) -> list[int]:
    return [
        score[0] + result.score_delta[0],
        score[1] + result.score_delta[1],
    ]


def match_winner(score: list[int]) -> int | None:
    if score[0] >= MATCH_WIN_SCORE:
        return 0
    if score[1] >= MATCH_WIN_SCORE:
        return 1
    return None
