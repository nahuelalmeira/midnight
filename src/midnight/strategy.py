from abc import abstractmethod
from typing import Iterable, List, Optional

import numpy as np
import pandas as pd

from .utils import N_DICE, QUALIFIERS, Score, dice_qualify, roll_dice, score_dice


class SimpleStrategy:
    """
    Abstract class for simple strategies. These strategies depend only on the
    current player roll.
    """

    def __init__(self):
        pass

    @classmethod
    def play(
        cls,
        kept_dice: List[int],
        rolled_dice: List[int],
    ) -> List[int]:
        new_dice_to_keep = cls._play(list(kept_dice), list(rolled_dice))
        assert len(new_dice_to_keep) > 0
        return new_dice_to_keep

    @classmethod
    @abstractmethod
    def _play(
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
        return dice_qualify(dice)

    @classmethod
    def sample(cls, nsamples: int = 1000, start_dice: List[int] = []) -> List[Score]:
        scores: List[Score] = []
        for _ in range(nsamples):
            kept_dice = list(start_dice)
            while len(kept_dice) < N_DICE:
                rolled_dice = roll_dice(N_DICE - len(kept_dice))
                new_dice_to_keep = cls.play(kept_dice, rolled_dice)
                kept_dice += new_dice_to_keep
            scores.append(score_dice(kept_dice))
        return scores

    def show_example(
        cls, start_dice: List[int] = [], start_roll: Optional[List[int]] = None
    ) -> pd.DataFrame:
        kept_dice = list(start_dice)
        data = []
        if start_roll is None:
            rolled_dice = roll_dice(N_DICE - len(kept_dice))
        else:
            if len(start_dice) + len(start_roll) != N_DICE:
                raise ValueError(f"The number of dice must be equal to {N_DICE}.")
            rolled_dice = list(start_roll)
        while len(kept_dice) < N_DICE:
            new_dice_to_keep = cls.play(kept_dice, rolled_dice)
            data.append([list(kept_dice), rolled_dice, new_dice_to_keep])
            kept_dice += new_dice_to_keep
            rolled_dice = roll_dice(N_DICE - len(kept_dice))
        df = pd.DataFrame(data, columns=["Kept dice", "Roll", "New dice"])
        return df


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
    def _play(
        cls,
        kept_dice: List[int],
        rolled_dice: List[int],
    ) -> List[int]:
        """
        Decides which of the rolled dice have to be kept.
        """
        new_dice_to_keep: List[int] = []

        # TODO: make this a function. Maybe this will require to define instance
        # methods instead of class methods
        for die in rolled_dice:
            all_kept_dice = kept_dice + new_dice_to_keep
            if cls.dice_qualify(all_kept_dice):
                break
            if die in QUALIFIERS and die not in kept_dice:
                new_dice_to_keep.append(die)

        for die in new_dice_to_keep:
            rolled_dice.remove(die)
        if cls.dice_qualify(kept_dice + new_dice_to_keep):
            new_dice_to_keep += cls.keep_when_qualifies(rolled_dice)
        if len(new_dice_to_keep) == 0:
            new_dice_to_keep.append(max(rolled_dice))
        return new_dice_to_keep

    @staticmethod
    def keep_when_qualifies(rolled_dice: List[int]) -> List[int]:
        dice_to_keep: List[int] = []
        finish = 0
        while not finish:
            if 6 in rolled_dice:
                dice_to_keep.append(6)
                rolled_dice.remove(6)
            elif len(rolled_dice) <= 2 and 5 in rolled_dice:
                dice_to_keep.append(5)
                rolled_dice.remove(5)
            elif len(rolled_dice) == 1 and 4 in rolled_dice:
                dice_to_keep.append(4)
                rolled_dice.remove(4)
            else:
                finish = 1
        return dice_to_keep

    @staticmethod
    def _keep_when_qualifies(rolled_dice):
        if len(rolled_dice) == 1:
            values_to_keep = [4, 5, 6]
        elif len(rolled_dice) == 2:
            values_to_keep = [5, 6]
        else:
            values_to_keep = [6]
        return [value for value in rolled_dice if value in values_to_keep]


class MiddleStrategy(SimpleStrategy):
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
    def _play(
        cls,
        kept_dice: List[int],
        rolled_dice: List[int],
    ) -> List[int]:
        """
        Decides which of the rolled dice have to be kept.
        """
        new_dice_to_keep: List[int] = []

        first_roll = len(kept_dice) == 0

        if first_roll:
            number_of_sixes = sum(np.array(rolled_dice) == 6)
            qualifiers_rolled = QUALIFIERS.intersection(rolled_dice)
            if qualifiers_rolled == QUALIFIERS:
                if number_of_sixes > 0:
                    new_dice_to_keep = list(qualifiers_rolled) + [6] * number_of_sixes
                else:
                    for die in rolled_dice:
                        if die in QUALIFIERS:
                            new_dice_to_keep.append(die)
                            break
            elif len(qualifiers_rolled) == 1:
                new_dice_to_keep += list(qualifiers_rolled) + [6] * min(
                    1, number_of_sixes
                )
        else:
            for die in rolled_dice:
                all_kept_dice = kept_dice + new_dice_to_keep
                if cls.dice_qualify(all_kept_dice):
                    break
                if die in QUALIFIERS and die not in kept_dice:
                    new_dice_to_keep.append(die)

        for die in new_dice_to_keep:
            rolled_dice.remove(die)

        if cls.dice_qualify(kept_dice + new_dice_to_keep):
            new_dice_to_keep += cls.keep_when_qualifies(rolled_dice)
        if len(new_dice_to_keep) == 0:
            new_dice_to_keep.append(max(rolled_dice))
        return new_dice_to_keep

    @staticmethod
    def keep_when_qualifies(rolled_dice):
        return ConservativeStrategy.keep_when_qualifies(rolled_dice)


class AgressiveStrategy(SimpleStrategy):
    """
    Rules:

    TODO
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
        pass


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


class AlwaysMiddleStrategy(CompoundStrategy):
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
        return MiddleStrategy().play(kept_dice, rolled_dice)
