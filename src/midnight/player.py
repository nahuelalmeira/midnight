from typing import Optional, List

from .strategy import CompoundStrategy, AlwaysConservativeStrategy
from .utils import INF_STAKE, Score, ANTE, roll_dice, N_DICE, MUST_HAVE_VALUES


class Player:
    """
    Class that represents a single player.

    Params:

    strategy: Players' compound strategy
    initial_stake: Amount of money the player starts with. If not given, it is setted
    to a default value
    name: Players' name. If not given, it will be assigned automatically
    """

    PLAYER_NUMBER: int = 0  # Counts the number of players that have been created

    @classmethod
    def reset_counter(cls):
        cls.PLAYER_NUMBER = 0

    def __init__(
        self,
        strategy: CompoundStrategy = AlwaysConservativeStrategy(),
        initial_stake: Optional[int] = None,
        name: Optional[str] = None,
    ) -> None:
        Player.PLAYER_NUMBER += 1
        self._name = name if name is not None else f"Player{self.PLAYER_NUMBER}"
        self.strategy = strategy
        self.kept_dice: List[int] = []
        self.initial_stake: int = (
            initial_stake if initial_stake is not None else INF_STAKE
        )
        self.stake = self.initial_stake
        self.wager: int  # Amount of money wagered the current round
        pass

    def __repr__(self) -> str:
        return f"Player(name={self.name}, stake={self.stake}, score={self.score})"

    def __lt__(self, other: "Player") -> bool:
        return self.score < other.score

    @property
    def name(self):
        return self._name

    @property
    def relative_stake(self) -> int:
        return self.stake - self.initial_stake

    def play(
        self,
        top_score: Optional[Score] = None,
        players_left: Optional[int] = None,
        current_pot: Optional[int] = None,
    ):
        """
        Play a round according to the player's compound strategy.
        """
        self.reset()
        self.wager = ANTE
        while not self.has_finished():
            rolled_dice = roll_dice(N_DICE - len(self.kept_dice))
            new_dice_to_keep = self.strategy.play(
                self.kept_dice, rolled_dice, top_score, players_left, current_pot
            )
            self.keep_dice(new_dice_to_keep)
        if self.qualifies():
            self.wager += ANTE
        self.stake -= self.wager

    def keep_dice(self, new_dice_to_keep: List[int]) -> None:
        """
        Add dice to previous kept dice.
        """
        self.kept_dice.extend(new_dice_to_keep)

    def has_finished(self):
        return len(self.kept_dice) == N_DICE

    def qualifies(self) -> bool:
        """
        A player qualifies when they kept a 1 and a 4.
        """
        return MUST_HAVE_VALUES.issubset(self.kept_dice)

    def reset(self) -> None:
        """
        Set the kept dice to 0. This should also reset the player's score.
        """
        self.kept_dice = []
        assert self.score == 0

    @property
    def score(self) -> Score:
        """
        Compute and return player score.
        """
        s = sum(self.kept_dice)
        for must_have_value in MUST_HAVE_VALUES:
            if must_have_value not in self.kept_dice:
                return Score(0)
            else:
                s -= must_have_value
        return Score(s)
