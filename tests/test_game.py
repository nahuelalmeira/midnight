from unittest.mock import Mock

import pytest

from midnight.game import Game, NoPlayerException


class TestGame:
    def test_no_players_raises_exception(self):
        game = Game()
        with pytest.raises(NoPlayerException):
            game.play()

    def test_sort_players(self):
        game = Game()
        game.players = ["Player1", "Player2", "Player3"]
        game.round_first_player = 1
        assert game.sort_players() == ["Player2", "Player3", "Player1"]

    def test_top_score(self):
        game = Game()
        player1 = Mock()
        player1.score = 5
        player2 = Mock()
        player2.score = 2
        player3 = Mock()
        player3.score = 7
        game.players = [player1, player2, player3]
        assert game.top_score == 7
