import pytest

from midnight.utils import InvalidScoreException, Score, score_dice


class TestScore:
    def test_valid_score_0(self):
        assert Score(0) == 0

    def test_valid_score_24(self):
        assert Score(24) == 24

    def test_negative_score(self):
        with pytest.raises(InvalidScoreException):
            Score(-1)

    def test_too_high_score(self):
        with pytest.raises(InvalidScoreException):
            Score(25)


class TestScoreDice:
    def test_score_is_zero(self):
        assert score_dice([1, 5, 6]) == 0

    def test_score_is_nonzero(self):
        assert score_dice([1, 4, 5, 6])

    def test_score_is_largest(self):
        assert score_dice([1, 4, 6, 6, 6, 6]) == 24

    def test_score_is_lowest(self):
        assert score_dice([1, 4, 1, 1, 1, 1]) == 4
