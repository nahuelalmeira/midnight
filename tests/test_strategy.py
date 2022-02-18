from midnight.strategy import ConservativeStrategy, MiddleStrategy


class TestConservativeStrategy:
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
        assert ConservativeStrategy.play(kept_dice, rolled_dice) == [5]

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
