from dataclasses import dataclass
from typing import Set, List

import numpy as np

N_DICE = 6  # Number of dice the game is played with
MUST_HAVE_VALUES: Set[int] = set([1, 4])  # Values a player must have in order to score


INF_STAKE = 100000000
ANTE = 1


def roll_dice(n: int) -> List[int]:
    return np.random.randint(1, 7, n).tolist()


class InvalidScoreException(BaseException):
    pass


class Score(int):
    @staticmethod
    def is_valid_score(score: int) -> bool:
        return 0 <= score <= 6 * (N_DICE - len(MUST_HAVE_VALUES))

    def __new__(cls, score, *args, **kwargs):
        if not cls.is_valid_score(score):
            raise InvalidScoreException()
        return super(Score, cls).__new__(cls, score)


@dataclass
class RoundStats:
    """
    Statistics related to a single round.
    """

    round: int
    winner: str
    pot: int
    scores: List[Score]
