from abc import abstractmethod
from typing import List, Iterable, Optional

from .utils import MUST_HAVE_VALUES, Score


class SimpleStrategy:
    """
    Abstract class for simple strategies. These strategies depend only on the
    current player roll.
    """

    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def play(
        cls,
        kept_dice: List[int],
        rolled_dice: List[int],
    ) -> List[int]:
        """
        Decides which of the rolled dice have to be kept.
        """
        pass

    @staticmethod
    def dice_qualify(dice: Iterable[int]) -> bool:
        return MUST_HAVE_VALUES.issubset(dice)


class ConservativeStrategy(SimpleStrategy):
    """
    Rules:

    For each roll:
        If player does not qualify:
            Keep the required dice if they were rolled, otherwise keep highest.
        Else:
            If one dice left, keep all 4, 5 or 6.
            If two dice left, keep all 5 or 6
            Else, keep all 6
    """

    @classmethod
    def play(
        cls,
        kept_dice: List[int],
        rolled_dice: List[int],
    ) -> List[int]:
        """
        Decides which of the rolled dice have to be kept.
        """
        new_dice_to_keep = []
        if cls.dice_qualify(kept_dice):
            new_dice_to_keep += cls.keep_when_qualifies(rolled_dice)
        else:
            for value in MUST_HAVE_VALUES:
                if value not in kept_dice and value in rolled_dice:
                    new_dice_to_keep.append(value)
                    rolled_dice.remove(value)
            if len(new_dice_to_keep) == 0:
                new_dice_to_keep.append(max(rolled_dice))
            elif cls.dice_qualify(kept_dice + new_dice_to_keep):
                new_dice_to_keep += cls.keep_when_qualifies(rolled_dice)
        return new_dice_to_keep

    @staticmethod
    def keep_when_qualifies(rolled_dice):
        if len(rolled_dice) == 1:
            values_to_keep = [4, 5, 6]
        elif len(rolled_dice) == 2:
            values_to_keep = [5, 6]
        else:
            values_to_keep = [6]
        return [value for value in rolled_dice if value in values_to_keep]


class CompoundStrategy:
    """
    Abstract class for compound strategies. These strategies choose among the
    simple strategies according to external variables, such as the current highest
    score, the pot size relative to the player wager and the number players left.
    """

    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def play(
        kept_dice: List[int],
        rolled_dice: List[int],
        top_score: Optional[Score],
        players_left: Optional[int],
        current_pot: Optional[int],
    ) -> List[int]:
        """
        Decides which of the rolled dice have to be kept.
        """
        pass


class AlwaysConservativeStrategy(CompoundStrategy):
    """
    Use always a conservative strategy, no matter the external variables.
    """

    @staticmethod
    def play(
        kept_dice: List[int],
        rolled_dice: List[int],
        top_score: Optional[Score],
        players_left: Optional[int],
        current_pot: Optional[int],
    ) -> List[int]:
        return ConservativeStrategy().play(kept_dice, rolled_dice)
