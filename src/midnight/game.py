from collections import defaultdict
from typing import Optional, List, Any, Dict

import numpy as np
import pandas as pd

from .player import Player
from .utils import RoundStats, Score


class NoPlayerException(BaseException):
    pass


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
