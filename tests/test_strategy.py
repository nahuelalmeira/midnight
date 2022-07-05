import pandas as pd

from midnight.strategy import ConservativeStrategy, MiddleStrategy


class TestConservativeStrategy:
    def test_scoring_probability(self):
        expected = 1 - (2 * (5 / 6) ** 21 - (4 / 6) ** 21)
        nsamples = 10000
        obtained = (
            1
            - pd.Series(ConservativeStrategy().sample(nsamples)).value_counts(
                normalize=True
            )[0]
        )
        epsilon = 1e-2
        assert obtained - epsilon < expected < obtained + epsilon

    def test_dont_keep_repeated_qualifiers(self):

        kept_dice = []
        rolled_dice = [1, 1, 6, 3, 3, 3]
        assert ConservativeStrategy.play(kept_dice, rolled_dice) == [1]

    def test1(self):

        kept_dice = []
        rolled_dice = [1, 4, 6, 3, 3, 3]
        assert ConservativeStrategy.play(kept_dice, rolled_dice) == [1, 4, 6]

    def test2(self):

        kept_dice = []
        rolled_dice = [1, 5, 6, 3, 3, 3]
        assert ConservativeStrategy.play(kept_dice, rolled_dice) == [1]

    def test3(self):

        kept_dice = [1]
        rolled_dice = [1, 4, 6, 3, 3]
        assert ConservativeStrategy.play(kept_dice, rolled_dice) == [4, 6]

    def test4(self):

        kept_dice = [1, 4, 6]
        rolled_dice = [5, 4, 3]
        assert ConservativeStrategy.play(kept_dice, rolled_dice) == [5]

    def test5(self):

        kept_dice = [1, 4, 6, 6]
        rolled_dice = [5, 4]
        assert ConservativeStrategy.play(kept_dice, rolled_dice) == [5, 4]

    def test6(self):

        kept_dice = [1, 4, 6, 6, 6]
        rolled_dice = [4]
        assert ConservativeStrategy.play(kept_dice, rolled_dice) == [4]

    def test7(self):

        kept_dice = [1, 4, 6, 6, 6]
        rolled_dice = [3]
        assert ConservativeStrategy.play(kept_dice, rolled_dice) == [3]

    def test8(self):

        kept_dice = [4, 6, 6, 6]
        rolled_dice = [1, 5]
        assert ConservativeStrategy.play(kept_dice, rolled_dice) == [1, 5]

    def test9(self):

        kept_dice = [4, 6, 6, 6]
        rolled_dice = [1, 4]
        assert ConservativeStrategy.play(kept_dice, rolled_dice) == [1, 4]

    def test10(self):

        kept_dice = [4, 6, 6, 6]
        rolled_dice = [1, 3]
        assert ConservativeStrategy.play(kept_dice, rolled_dice) == [1]

    def test11(self):

        kept_dice = []
        rolled_dice = [1, 4, 6, 6, 6, 5]
        assert ConservativeStrategy.play(kept_dice, rolled_dice) == [1, 4, 6, 6, 6, 5]

    def test12(self):

        kept_dice = []
        rolled_dice = [1, 4, 6, 6, 6, 4]
        assert ConservativeStrategy.play(kept_dice, rolled_dice) == [1, 4, 6, 6, 6, 4]

    def test13(self):

        kept_dice = []
        rolled_dice = [1, 4, 6, 6, 6, 3]
        assert ConservativeStrategy.play(kept_dice, rolled_dice) == [1, 4, 6, 6, 6]

    def test14(self):

        kept_dice = []
        rolled_dice = [1, 4, 6, 6, 5, 2]
        assert ConservativeStrategy.play(kept_dice, rolled_dice) == [1, 4, 6, 6, 5]


class TestMiddleStrategy:
    def test1(self):

        kept_dice = []
        rolled_dice = [1, 4, 6, 5, 3, 3]
        assert MiddleStrategy.play(kept_dice, rolled_dice) == [1, 4, 6]

    def test2(self):

        kept_dice = []
        rolled_dice = [1, 4, 6, 6, 3, 3]
        assert MiddleStrategy.play(kept_dice, rolled_dice) == [1, 4, 6, 6]

    def test3(self):

        kept_dice = []
        rolled_dice = [1, 6, 5, 3, 3, 3]
        assert MiddleStrategy.play(kept_dice, rolled_dice) == [1, 6]

    def test4(self):

        kept_dice = []
        rolled_dice = [1, 6, 6, 3, 3, 3]
        assert MiddleStrategy.play(kept_dice, rolled_dice) == [1, 6]

    def test5(self):

        kept_dice = []
        rolled_dice = [1, 4, 5, 3, 3, 3]
        assert MiddleStrategy.play(kept_dice, rolled_dice) == [1]

    def test6(self):
        kept_dice = [1]
        rolled_dice = [4, 5, 3, 3, 3]
        assert MiddleStrategy.play(kept_dice, rolled_dice) == [4]
