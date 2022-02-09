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
    round: int
    winner: str
    pot: int
    scores: List[Score]


class SimpleStrategy:
    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def play(
        cls,
        picked_dice: List[int],
        rolled_dice: List[int],
    ) -> List[int]:
        """
        Decides which of the rolled dice have to be picked.
        """
        pass

    @staticmethod
    def dice_qualify(dice: Iterable[int]) -> bool:
        return MUST_HAVE_VALUES.issubset(dice)


class ConservativeStrategy(SimpleStrategy):
    """
    Rules:

    TODO: add rules
    """

    @classmethod
    def play(
        cls,
        picked_dice: List[int],
        rolled_dice: List[int],
    ) -> List[int]:

        new_dice_to_pick = []
        if cls.dice_qualify(picked_dice):
            new_dice_to_pick += cls.pick_when_qualifies(rolled_dice)
        else:
            for value in MUST_HAVE_VALUES:
                if value not in picked_dice and value in rolled_dice:
                    new_dice_to_pick.append(value)
                    rolled_dice.remove(value)
            if len(new_dice_to_pick) == 0:
                new_dice_to_pick.append(max(rolled_dice))
            elif cls.dice_qualify(picked_dice + new_dice_to_pick):
                new_dice_to_pick += cls.pick_when_qualifies(rolled_dice)
        return new_dice_to_pick

    @staticmethod
    def pick_when_qualifies(rolled_dice):
        values_to_keep = set([6])
        if len(rolled_dice) == 2:
            values_to_keep.add(5)
        elif len(rolled_dice) == 1:
            values_to_keep = values_to_keep.union([4, 5])
        return [value for value in rolled_dice if value in values_to_keep]


class CompoundStrategy:
    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def play(
        picked_dice: List[int],
        rolled_dice: List[int],
        top_score: Optional[Score],
        players_left: Optional[int],
        current_pot: Optional[int],
    ) -> List[int]:
        """
        Decides which of the rolled dice have to be picked.
        """
        pass


class AlwaysConservativeStrategy(CompoundStrategy):
    @staticmethod
    def play(
        picked_dice: List[int],
        rolled_dice: List[int],
        top_score: Optional[Score],
        players_left: Optional[int],
        current_pot: Optional[int],
    ) -> List[int]:
        """
        Decides which of the rolled dice have to be picked.
        """
        return ConservativeStrategy().play(picked_dice, rolled_dice)


class Player:

    PLAYER_NUMBER: int = 0

    @classmethod
    def reset_counter(cls):
        cls.PLAYER_NUMBER = 0

    def __init__(
        self,
        initial_stake: Optional[int] = None,
        strategy: CompoundStrategy = AlwaysConservativeStrategy(),
        name: Optional[str] = None,
    ) -> None:
        Player.PLAYER_NUMBER += 1
        self._name = name if name is not None else f"Player{self.PLAYER_NUMBER}"
        self.strategy = strategy
        self.picked_dice: List[int] = []
        self.initial_stake: int = (
            initial_stake if initial_stake is not None else INF_STAKE
        )
        self.stake = self.initial_stake
        self.wager: int  # Amount of money wagered the current hand
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
        self.wager = ANTE
        while not self.has_finished():
            rolled_dice = roll_dice(N_DICE - len(self.picked_dice))
            new_dice_to_pick = self.strategy.play(
                self.picked_dice, rolled_dice, top_score, players_left, current_pot
            )
            self.pick_dice(new_dice_to_pick)
        if self.qualifies():
            self.wager += ANTE
        self.stake -= self.wager

    def pick_dice(self, new_dice_to_pick: List[int]) -> None:
        self.picked_dice.extend(new_dice_to_pick)

    def has_finished(self):
        return len(self.picked_dice) == N_DICE

    def qualifies(self) -> bool:
        return MUST_HAVE_VALUES.issubset(self.picked_dice)

    def reset(self) -> None:
        self.picked_dice = []

    @property
    def score(self) -> Score:
        """
        Compute and return player score.
        """

        s = sum(self.picked_dice)
        for must_have_value in MUST_HAVE_VALUES:
            if must_have_value not in self.picked_dice:
                return Score(0)
            else:
                s -= must_have_value
        return Score(s)


class Game:
    def __init__(self, random_seed: Optional[int] = None, n_hands: int = 1) -> None:
        self.players: List[Player] = []
        self.hand_first_player: int = 0
        self.hands_played: int = 0
        self._game_stats: Dict[str, List[Any]] = defaultdict(list)
        self.n_hands = n_hands  # Number of hands to be played
        self.current_pot: int = 0  # Pot at play in current hand
        self.last_round_stats: RoundStats

        # # Set random seed for reproducibility
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
        Play one hand for each player, according to each player's strategy.
        """
        self.reset_players(self.players)

        winners = self.roll()

        if len(winners) == 1:  # There is a single winner
            winner = winners[0]
            winner.stake += self.current_pot

            # Last winner starts next hand
            self.hand_first_player = self.players.index(winner)

            self.hand_winner = winner.name
            self.last_round_stats = RoundStats(
                self.hands_played,
                winner.name,
                self.current_pot,
                self.scores,
            )
            self.current_pot = 0

        else:  # There is a tie

            # Last tied player starts next hand
            self.hand_first_player = self.players.index(winners[-1])

            self.last_round_stats = RoundStats(
                self.hands_played,
                "Tie",
                self.current_pot,
                self.scores,
            )
        self.hands_played += 1

    def roll(self) -> List[Player]:
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
        winners = [player for player in players if player.score == top_score]
        return winners

    def sort_players(self) -> List[Player]:
        first_player = self.hand_first_player
        return self.players[first_player:] + self.players[:first_player]

    def has_finished(self) -> bool:
        return self.hands_played == self.n_hands

    def save_round_stats(self):

        hand_stats = {
            "ROUND": self.last_round_stats.round,
            "POT": self.last_round_stats.pot,
            "WINNER": self.last_round_stats.winner,
            "SCORES": self.last_round_stats.scores,
        }
        for key, value in hand_stats.items():
            self._game_stats[key].append(value)

    def reset_players(self, players) -> None:
        for player in players:
            player.reset()

    @property
    def n_players(self) -> int:
        return len(self.players)

    @property
    def finished_players(self) -> int:
        return sum([player.has_finished() for player in self.players])

    @property
    def scores(self) -> List[Score]:
        return [player.score for player in self.players]

    @property
    def top_score(self) -> Score:
        return Score(max([player.score for player in self.players]))

    @property
    def stakes(self) -> List[int]:
        return [player.stake for player in self.players]

    @property
    def relative_stakes(self) -> List[int]:
        return [player.relative_stake for player in self.players]

    @property
    def game_stats(self) -> pd.DataFrame:
        return pd.DataFrame(self._game_stats)

    def get_player_scores(self, player_index: int) -> List[Score]:
        return [row[player_index] for row in self.game_stats["SCORES"].values]

    def get_scores(self) -> pd.DataFrame:
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

    game = Game(n_hands=n_rounds)
    for i in range(n_players):
        player = Player(
            strategy=AlwaysConservativeStrategy(), initial_stake=initial_stake
        )
        game.add_player(player)

    # Play game
    game.play()

    print("-----------------")
    print("Game stats")
    stats = game.game_stats
    print(stats.head(10))
    print("-----------------")
    print()
    print(f"Final relative stakes: {game.relative_stakes}")
    print()

    print("-----------------")
    print("Scores")
    scores = game.get_scores()
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
