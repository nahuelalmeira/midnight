from collections import defaultdict
from abc import abstractmethod
from typing import Optional, Set, List, Dict, Any

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


class Score(int):
    @staticmethod
    def is_valid_score(score: int) -> bool:
        return 0 <= score <= 6 * (N_DICE - len(MUST_HAVE_VALUES))

    def __new__(cls, score, *args, **kwargs):
        if not cls.is_valid_score(score):
            raise InvalidScoreException()
        return super(Score, cls).__new__(cls, score)


class Strategy:
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


class BaseStrategy(Strategy):
    """
    Rules:

    - If player does not have a 1 and it is rolled, pick it.
    - If player does not have a 4 and it is rolled, pick it.
    - If no dice has been picked, pick the highest one.
    """

    @staticmethod
    def play(
        picked_dice: List[int],
        rolled_dice: List[int],
        top_score: Optional[Score],
        players_left: Optional[int],
        current_pot: Optional[int],
    ) -> List[int]:
        new_dice_to_pick = []
        for value in MUST_HAVE_VALUES:
            if value not in picked_dice and value in rolled_dice:
                new_dice_to_pick.append(value)

        if len(new_dice_to_pick) == 0:
            new_dice_to_pick.append(max(rolled_dice))
        return new_dice_to_pick


class BaseStrategy2(Strategy):
    """
    Rules:

    - If player does not have a 1 and it is rolled, pick it.
    - If player does not have a 4 and it is rolled, pick it.
    - Pick all 6s.
    - If no dice has been picked, pick the highest one.
    """

    @staticmethod
    def play(
        picked_dice: List[int],
        rolled_dice_: List[int],
        top_score: Optional[Score],
        players_left: Optional[int],
        current_pot: Optional[int],
    ) -> List[int]:
        rolled_dice = rolled_dice_[:]
        new_dice_to_pick = []
        for value in MUST_HAVE_VALUES:
            if value not in picked_dice and value in rolled_dice:
                new_dice_to_pick.append(value)
                rolled_dice.remove(value)

        value_to_pick = 6
        while value_to_pick in rolled_dice:
            new_dice_to_pick.append(value_to_pick)
            rolled_dice.remove(value_to_pick)

        if len(new_dice_to_pick) == 0:
            new_dice_to_pick.append(max(rolled_dice))
        return new_dice_to_pick


class PickMaxStrategy(Strategy):
    """
    Rules:

    - Pick always the highest dice.
    """

    @staticmethod
    def play(
        picked_dice: List[int],
        rolled_dice: List[int],
        top_score: Optional[Score],
        players_left: Optional[int],
        current_pot: Optional[int],
    ) -> List[int]:
        new_dice_to_pick = [max(rolled_dice)]
        return new_dice_to_pick


class Player:

    PLAYER_NUMBER: int = 0

    @classmethod
    def reset_counter(cls):
        cls.PLAYER_NUMBER = 0

    def __init__(
        self,
        initial_stake: Optional[int] = None,
        strategy: Strategy = BaseStrategy(),
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
        self.wager = 2 * ANTE
        while not self.has_finished():
            rolled_dice = roll_dice(N_DICE - len(self.picked_dice))
            new_dice_to_pick = self.strategy.play(
                self.picked_dice, rolled_dice, top_score, players_left, current_pot
            )
            self.pick_dice(new_dice_to_pick)
        if self.qualifies():
            self.wager -= ANTE
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
        self.current_pot: int  # Pot at play in current hand
        self.hand_winner: Player  # Last hand winner
        self.hand_n_rounds: int  # Number of rounds in last hand

        # # Set random seed for reproducibility
        np.random.seed(random_seed)

    def add_player(self, player: Player) -> None:
        self.players.append(player)

    def play(self) -> None:
        """
        Run game simulation.
        """

        while not self.has_finished():
            self.play_hand()

    def play_hand(self) -> None:
        """
        Play one hand for each player, according to each player's strategy.
        """

        players = self.sort_players()
        self.current_pot = 0
        n_rounds = 0
        while len(players) > 1:
            self.reset_players(self.players)
            players = self.play_round(players)
            n_rounds += 1
            # print(self.hands_played, n_rounds, end="\t")
            # for player in self.players:
            #    print(player.score, end="; ")
            # print()

        winner = players[0]
        winner.stake += self.current_pot
        self.hand_winner = winner
        self.hand_n_rounds = n_rounds

        self.save_hand_stats()
        # print(self.hands_played, self.hand_n_rounds, self.top_score, self.hand_winner)

        self.hand_first_player = (self.hand_first_player + 1) % self.n_players
        self.hands_played += 1

        self.reset_players(self.players)

    def play_round(self, players):

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
        players = [player for player in players if player.score == top_score]
        return players

    def sort_players(self) -> List[Player]:
        first_player = self.hand_first_player
        return self.players[first_player:] + self.players[:first_player]

    def has_finished(self) -> bool:
        return self.hands_played == self.n_hands

    def save_hand_stats(self):

        hand_stats = {
            "HAND": self.hands_played,
            "ROUNDS": self.hand_n_rounds,
            "WINNER": self.hand_winner.name,
            "SCORES": [player.score for player in self.players],
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
    def scores(self) -> Dict[str, int]:
        return {player.name: player.score for player in self.players}

    @property
    def top_score(self) -> Score:
        return Score(max([player.score for player in self.players]))

    @property
    def round_winner(self) -> Player:
        return list(sorted(self.players, reverse=True))[0]

    @property
    def stakes(self) -> Dict[str, int]:
        return {player.name: player.stake for player in self.players}

    @property
    def relative_stakes(self) -> Dict[str, int]:
        return {player.name: player.relative_stake for player in self.players}

    @property
    def game_stats(self) -> pd.DataFrame:
        return pd.DataFrame(self._game_stats)


if __name__ == "__main__":

    player1 = Player(strategy=BaseStrategy())
    player2 = Player(strategy=BaseStrategy2())

    game = Game()

    game.add_player(player1)
    # game.add_player(player2)

    game.play()

    print(game.scores)

    n_hands = 10000

    Player.reset_counter()
    player1 = Player(strategy=BaseStrategy())
    player2 = Player(strategy=BaseStrategy())
    player3 = Player(strategy=BaseStrategy())

    game = Game(n_hands=n_hands)
    game.add_player(player1)
    game.add_player(player2)
    game.add_player(player3)
    game.play()

    df = game.game_stats
    print(df.head())
    print(df["ROUNDS"].value_counts().sort_index())
    print(df["WINNER"].value_counts(normalize=True))
