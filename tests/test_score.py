import pytest

from midnight.utils import InvalidScoreException, Score


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
