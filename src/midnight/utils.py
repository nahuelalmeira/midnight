from dataclasses import dataclass
from typing import Iterable, List, Set

import numpy as np

N_DICE = 6  # Number of dice the game is played with
QUALIFIERS: Set[int] = set([1, 4])  # Values a player must have in order to score


INF_STAKE = 100000000
ANTE = 1


def roll_dice(n: int) -> List[int]:
    return np.random.randint(1, 7, n).tolist()


class InvalidScoreException(BaseException):
    pass


class Score(int):
    @staticmethod
    def is_valid_score(score: int) -> bool:
        return 0 <= score <= 6 * (N_DICE - len(QUALIFIERS))

    def __new__(cls, score, *args, **kwargs):
        if not cls.is_valid_score(score):
            raise InvalidScoreException()
        return super(Score, cls).__new__(cls, score)


def score_dice(dice: List[int]) -> Score:
    """
    Compute and return dice score.
    """
    s = sum(dice)
    for must_have_value in QUALIFIERS:
        if must_have_value not in dice:
            return Score(0)
        else:
            s -= must_have_value
    return Score(s)


def dice_qualify(dice: Iterable[int]) -> bool:
    return QUALIFIERS.issubset(dice)


@dataclass
class RoundStats:
    """
    Statistics related to a single round.
    """

    round: int
    winner: str
    pot: int
    scores: List[Score]
