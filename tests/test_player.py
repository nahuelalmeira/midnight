import pytest

from midnight.player import Player


@pytest.fixture
def player():
    return Player()


@pytest.fixture
def mock_strategy_1_4():
    class MockStrategy:
        def play(self, *args):
            return [1, 4]

    return MockStrategy()


@pytest.fixture
def mock_strategy_1():
    class MockStrategy:
        def play(self, *args):
            return [1]

    return MockStrategy()


class TestPlayer:
    def test_does_qualifies(self, player):
        player.kept_dice = [1, 4]
        assert player.qualifies()

    def test_does_not_qualifies(self, player):
        player.kept_dice = [1, 5]
        assert not player.qualifies()

    def test_has_finished(self, player):
        player.kept_dice = [1, 1, 1, 3, 4, 5]
        assert player.has_finished()

    def test_has_not_finished(self, player):
        player.kept_dice = [1, 3, 4, 5]
        assert not player.has_finished()

    def test_keep_dice(self, player):
        player.kept_dice = [1]
        player.keep_dice([2, 2])
        assert player.kept_dice == [1, 2, 2]

    def test_score_is_zero(self, player):
        player.kept_dice = [1, 5, 6]
        assert player.score == 0

    def test_score_is_nonzero(self, player):
        player.kept_dice = [1, 4, 5, 6]
        assert player.score == 11

    def test_name(self):
        player = Player(name="John")
        assert player.name == "John"

    def test_initial_relative_stake(self):
        player = Player(initial_stake=10)
        assert player.relative_stake == 0

    def test_different_relative_stake(self):
        player = Player(initial_stake=10)
        player.stake = 5
        assert player.relative_stake == -5

    def test_play(self, player, mock_strategy_1_4):

        # mocker.patch("midnight.main.roll_dice", return_value=[1])

        player.strategy = mock_strategy_1_4
        player.play()
        assert player.kept_dice == [1, 4, 1, 4, 1, 4]

    def test_play_stake_does_qualifies(self, player, mock_strategy_1_4):
        player.stake = 2
        player.strategy = mock_strategy_1_4
        player.play()
        assert player.stake == 1

    def test_play_stake_does_not_qualifies(self, player, mock_strategy_1):
        player.stake = 2
        player.strategy = mock_strategy_1
        player.play()
        assert player.stake == 0
