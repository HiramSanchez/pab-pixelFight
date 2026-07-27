import pytest

from pixel_fight.combat.round_rules import (
    MATCH_WIN_SCORE,
    RoundEndReason,
    apply_score,
    match_winner,
    resolve_round,
)


@pytest.mark.parametrize(
    ("health_1", "health_2", "winner"),
    [
        (0, 100, 1),
        (100, 0, 0),
        (-10, 20, 1),
        (20, -10, 0),
    ],
)
def test_ko_awards_the_surviving_player(health_1, health_2, winner):
    result = resolve_round(health_1, health_2)

    assert result.winner_index == winner
    assert result.reason is RoundEndReason.KO


def test_simultaneous_ko_is_a_draw_without_score():
    result = resolve_round(0, 0)

    assert result.winner_index is None
    assert result.reason is RoundEndReason.DRAW
    assert apply_score([1, 2], result) == [1, 2]


@pytest.mark.parametrize(
    ("health_1", "health_2", "winner"),
    [
        (75, 50, 0),
        (50, 75, 1),
    ],
)
def test_timeout_awards_player_with_more_health(health_1, health_2, winner):
    result = resolve_round(health_1, health_2, time_expired=True)

    assert result.winner_index == winner
    assert result.reason is RoundEndReason.TIMEOUT


def test_timeout_with_equal_health_is_a_draw():
    result = resolve_round(40, 40, time_expired=True)

    assert result.winner_index is None
    assert result.reason is RoundEndReason.DRAW


def test_active_round_has_no_result():
    assert resolve_round(100, 100, time_expired=False) is None


def test_score_is_applied_exactly_once_to_the_winner():
    result = resolve_round(100, 0)

    original_score = [1, 1]
    updated_score = apply_score(original_score, result)

    assert original_score == [1, 1]
    assert updated_score == [2, 1]


@pytest.mark.parametrize(
    ("score", "winner"),
    [
        ([MATCH_WIN_SCORE, 0], 0),
        ([0, MATCH_WIN_SCORE], 1),
        ([MATCH_WIN_SCORE - 1, MATCH_WIN_SCORE - 1], None),
    ],
)
def test_match_ends_at_three_round_wins(score, winner):
    assert match_winner(score) == winner


def test_lethal_burn_health_resolves_as_ko_in_the_same_resolution_step():
    health_after_burn = 10 - 10

    result = resolve_round(health_after_burn, 50)

    assert result.winner_index == 1
    assert result.reason is RoundEndReason.KO
