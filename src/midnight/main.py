from collections import defaultdict
from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional, Set, List, Dict, Any, Iterable

import numpy as np
import pandas as pd

N_DICE = 6  # Number of dice the game is played with
MUST_HAVE_VALUES: Set[int] = set([1, 4])  # Values a player must have in order to score
INF_STAKE = 100000000
ANTE = 1


def roll_dice(n: int) -> List[int]:
    return np.random.randint(1, 7, n).tolist()


class InvalidScoreException(BaseException):
    pass


class NoPlayerException(BaseException):
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


class SimpleStrategy:
    """
    Abstract class for simple strategies. These strategies depend only on the
    current player roll.
    """

    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def play(
        cls,
        kept_dice: List[int],
        rolled_dice: List[int],
    ) -> List[int]:
        """
        Decides which of the rolled dice have to be kept.
        """
        pass

    @staticmethod
    def dice_qualify(dice: Iterable[int]) -> bool:
        return MUST_HAVE_VALUES.issubset(dice)


class ConservativeStrategy(SimpleStrategy):
    """
    Rules:

    For each roll:
        If player does not qualify:
            Keep the required dice if they were rolled, otherwise keep highest.
        Else:
            If one dice left, keep all 4, 5 or 6.
            If two dice left, keep all 5 or 6
            Else, keep all 6
    """

    @classmethod
    def play(
        cls,
        kept_dice: List[int],
        rolled_dice: List[int],
    ) -> List[int]:
        """
        Decides which of the rolled dice have to be kept.
        """
        new_dice_to_keep = []
        if cls.dice_qualify(kept_dice):
            new_dice_to_keep += cls.keep_when_qualifies(rolled_dice)
        else:
            for value in MUST_HAVE_VALUES:
                if value not in kept_dice and value in rolled_dice:
                    new_dice_to_keep.append(value)
                    rolled_dice.remove(value)
            if len(new_dice_to_keep) == 0:
                new_dice_to_keep.append(max(rolled_dice))
            elif cls.dice_qualify(kept_dice + new_dice_to_keep):
                new_dice_to_keep += cls.keep_when_qualifies(rolled_dice)
        return new_dice_to_keep

    @staticmethod
    def keep_when_qualifies(rolled_dice):
        if len(rolled_dice) == 1:
            values_to_keep = [4, 5, 6]
        elif len(rolled_dice) == 2:
            values_to_keep = [5, 6]
        else:
            values_to_keep = [6]
        return [value for value in rolled_dice if value in values_to_keep]


class CompoundStrategy:
    """
    Abstract class for compound strategies. These strategies choose among the
    simple strategies according to external variables, such as the current highest
    score, the pot size relative to the player wager and the number players left.
    """

    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def play(
        kept_dice: List[int],
        rolled_dice: List[int],
        top_score: Optional[Score],
        players_left: Optional[int],
        current_pot: Optional[int],
    ) -> List[int]:
        """
        Decides which of the rolled dice have to be kept.
        """
        pass


class AlwaysConservativeStrategy(CompoundStrategy):
    """
    Use always a conservative strategy, no matter the external variables.
    """

    @staticmethod
    def play(
        kept_dice: List[int],
        rolled_dice: List[int],
        top_score: Optional[Score],
        players_left: Optional[int],
        current_pot: Optional[int],
    ) -> List[int]:
        return ConservativeStrategy().play(kept_dice, rolled_dice)


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


class Game:
    """
    Class that represents a Midnight game.

    Params:

    n_rounds: number of rounds to be played
    random_seed: seed to setup random number generatr
    """

    def __init__(self, n_rounds: int = 1, random_seed: Optional[int] = None) -> None:
        self.players: List[Player] = []
        self.round_first_player: int = 0
        self.rounds_played: int = 0
        self._game_stats: Dict[str, List[Any]] = defaultdict(list)
        self.n_rounds = n_rounds  # Number of rounds to be played
        self.current_pot: int = 0  # Pot at play in current round
        self.last_round_stats: RoundStats

        # Set random seed for reproducibility
        np.random.seed(random_seed)

    def add_player(self, player: Player) -> None:
        self.players.append(player)

    def play(self) -> None:
        """
        Run game simulation.
        """
        if self.n_players == 0:
            raise NoPlayerException

        while not self.has_finished():
            self.play_round()
            self.save_round_stats()

    def play_round(self) -> None:
        """
        Play a single round and save associated statistics.
        """
        top_scored_players = self.roll()

        if len(top_scored_players) == 1:  # There is a single winner
            winner = top_scored_players[0]
            winner.stake += self.current_pot
            self.round_winner = winner.name
            self.last_round_stats = RoundStats(
                self.rounds_played,
                winner.name,
                self.current_pot,
                self.scores,
            )
            self.current_pot = 0
        else:  # There is a tie
            self.last_round_stats = RoundStats(
                self.rounds_played,
                "Tie",
                self.current_pot,
                self.scores,
            )

        # Last tied player starts next round. If no tie, then the winner starts.
        self.round_first_player = self.players.index(top_scored_players[-1])

        self.rounds_played += 1

    def roll(self) -> List[Player]:
        """
        Roll dice for each player, according to their strategies. The player who
        begins the round is given by the `sort_players` method.
        """
        players = self.sort_players()
        for i, player in enumerate(players, start=1):
            players_left = self.n_players - i
            player.play(
                top_score=self.top_score,
                players_left=players_left,
                current_pot=self.current_pot,
            )
            self.current_pot += player.wager

        # top_score = max([player.score for player in players])
        top_score = self.top_score
        top_scored_players = [player for player in players if player.score == top_score]
        return top_scored_players

    def sort_players(self) -> List[Player]:
        first_player = self.round_first_player
        return self.players[first_player:] + self.players[:first_player]

    def has_finished(self) -> bool:
        """
        Return wether all rounds have been played.
        """
        return self.rounds_played == self.n_rounds

    def save_round_stats(self):

        round_stats = {
            "ROUND": self.last_round_stats.round,
            "POT": self.last_round_stats.pot,
            "WINNER": self.last_round_stats.winner,
            "SCORES": self.last_round_stats.scores,
        }
        for key, value in round_stats.items():
            self._game_stats[key].append(value)

    @property
    def n_players(self) -> int:
        """
        Number of players.
        """
        return len(self.players)

    @property
    def scores(self) -> List[Score]:
        return [player.score for player in self.players]

    @property
    def top_score(self) -> Score:
        return Score(max(self.scores))

    @property
    def stakes(self) -> List[int]:
        return [player.stake for player in self.players]

    @property
    def relative_stakes(self) -> List[int]:
        return [player.relative_stake for player in self.players]

    def get_game_stats(self) -> pd.DataFrame:
        return pd.DataFrame(self._game_stats)

    def get_player_scores(self, player_index: int) -> List[Score]:
        return [row[player_index] for row in self.get_game_stats()["SCORES"].values]

    def get_all_scores(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                player.name: self.get_player_scores(i)
                for i, player in enumerate(self.players)
            }
        )


if __name__ == "__main__":

    n_rounds = 10000
    n_players = 2
    initial_stake = 1000

    print("-----------------")
    print("Game settings")
    print(f"Number of players: {n_players}")
    print(f"Number of rounds: {n_rounds}")
    print(f"Initial stake: {initial_stake}")
    print("-----------------")
    print()

    game = Game(n_rounds=n_rounds)
    for i in range(n_players):
        player = Player(
            strategy=AlwaysConservativeStrategy(), initial_stake=initial_stake
        )
        game.add_player(player)

    # Play game
    game.play()

    print("-----------------")
    print("Game stats")
    stats = game.get_game_stats()
    print(stats.head(10))
    print("-----------------")
    print()
    print(f"Final relative stakes: {game.relative_stakes}")
    print()

    print("-----------------")
    print("Scores")
    scores = game.get_all_scores()
    print(scores.head())
    print("-----------------")
    print()

    print("-----------------")
    print("Qualification rate per player:")
    print((scores > 0).mean())
    print("-----------------")
    print()

    print("-----------------")
    print("Win rate per player:")
    print(stats["WINNER"].value_counts(normalize=True))
    print("-----------------")
    print()
