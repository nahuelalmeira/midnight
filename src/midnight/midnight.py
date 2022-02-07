from abc import abstractmethod
from typing import Optional, Set, List, Dict

import numpy as np


N_DICE = 6  # Number of dice the game is played with
MUST_HAVE_VALUES: Set[int] = set([1, 4])  # Values a player must have in order to score


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
        kept_dice: List[int],
        rolled_dice: List[int],
        top_score: Optional[Score],
        players_left: Optional[int],
    ):
        """
        Decides which of the rolled dice have to be kept.
        """
        pass


class BaseStrategy(Strategy):
    """
    Rules:

    - If player does not have a 1 and it is rolled, keep it.
    - If player does not have a 4 and it is rolled, keep it.
    - If no dice has been picked, pick the highest one.
    """

    @staticmethod
    def play(
        kept_dice: List[int],
        rolled_dice: List[int],
        top_score: Optional[Score],
        players_left: Optional[int],
    ) -> List[int]:
        new_dice_to_keep = []
        for value in MUST_HAVE_VALUES:
            if value not in kept_dice and value in rolled_dice:
                new_dice_to_keep.append(value)

        if len(new_dice_to_keep) == 0:
            new_dice_to_keep.append(max(rolled_dice))
        return new_dice_to_keep


class BaseStrategy2(Strategy):
    """
    Rules:

    - If player does not have a 1 and it is rolled, keep it.
    - If player does not have a 4 and it is rolled, keep it.
    - Pick all 6s.
    - If no dice has been picked, pick the highest one.
    """

    @staticmethod
    def play(
        kept_dice: List[int],
        rolled_dice_: List[int],
        top_score: Optional[Score],
        players_left: Optional[int],
    ) -> List[int]:
        rolled_dice = rolled_dice_[:]
        new_dice_to_keep = []
        for value in MUST_HAVE_VALUES:
            if value not in kept_dice and value in rolled_dice:
                new_dice_to_keep.append(value)
                rolled_dice.remove(value)

        value_to_keep = 6
        while value_to_keep in rolled_dice:
            new_dice_to_keep.append(value_to_keep)
            rolled_dice.remove(value_to_keep)

        if len(new_dice_to_keep) == 0:
            new_dice_to_keep.append(max(rolled_dice))
        return new_dice_to_keep


class KeepMaxStrategy(Strategy):
    """
    Rules:

    - Keep always the highest dice.
    """

    @staticmethod
    def play(
        kept_dice: List[int],
        rolled_dice: List[int],
        top_score: Optional[Score],
        players_left: Optional[int],
    ) -> List[int]:
        new_dice_to_keep = [max(rolled_dice)]
        return new_dice_to_keep


class Player:

    PLAYER_NUMBER: int = 0

    def __init__(
        self, strategy: Strategy = BaseStrategy(), name: Optional[str] = None
    ) -> None:
        Player.PLAYER_NUMBER += 1
        self._name = name if name is not None else f"Player{self.PLAYER_NUMBER}"
        self.strategy = strategy
        self.kept_dice: List[int] = []
        pass

    @property
    def name(self):
        return self._name

    def play_hand(
        self,
        top_score: Optional[Score] = None,
        players_left: Optional[int] = None,
    ):
        if self.has_finished():
            return

        rolled_dice = roll_dice(N_DICE - len(self.kept_dice))
        new_dice_to_keep = self.strategy.play(
            self.kept_dice, rolled_dice, top_score, players_left
        )

        self.kept_dice.extend(new_dice_to_keep)

    def has_finished(self):
        return len(self.kept_dice) == N_DICE

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
    def __init__(self, random_seed: Optional[int] = None) -> None:
        self.players: List[Player] = []

        self.n_rounds: int = 0

        # # Set random seed for reproducibility
        np.random.seed(random_seed)

    def add_player(self, player: Player) -> None:
        self.players.append(player)

    def play(self) -> None:
        """
        Run game simulation.
        """

        while not self.has_finished():
            self.play_round()

    def play_round(self) -> None:
        """
        Play one hand for each player, according to each player's strategy.
        """
        self.n_rounds += 1
        # print(f"Round {self.n_rounds}")
        for i, player in enumerate(self.players, start=1):
            players_left = self.n_players - i
            player.play_hand(top_score=self.top_score, players_left=players_left)
            # print(player.name, player.score, player.kept_dice)

    def has_finished(self) -> bool:
        return self.finished_players == self.n_players

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
        return Score(max(list(self.scores.values())))


if __name__ == "__main__":

    player1 = Player(strategy=BaseStrategy())
    player2 = Player(strategy=BaseStrategy2())

    game = Game()

    game.add_player(player1)
    # game.add_player(player2)

    game.play()

    print(game.scores)

    n_games = 10000
    scores = np.zeros((n_games, 2))

    for i in range(n_games):
        game = Game()
        game.add_player(Player(strategy=BaseStrategy()))
        game.add_player(Player(strategy=KeepMaxStrategy()))
        game.play()
        scores[i] = np.array(list((game.scores.values())))

    print(scores.mean(axis=0), scores.std(axis=0))
    print("Player 1 win rate:", (scores[:, 1] < scores[:, 0]).mean())
