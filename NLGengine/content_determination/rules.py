from collections import Counter


class Rules:
    """This class methods with rules that can be called upon for a rules check.
    """

    @staticmethod
    def x_times_repeat_comp(amount: int, observs: list):
        """Check whether a component is repeated for x times or over.

        Args:
            amount (int): The amount of repetitions to check for
            observs (list): A list of observations to search for

        Returns:
            bool: Returns whether a component has been mentioned x times.
        """
        assert amount > 0, "Amount has to be greater than zero"

        # check whether there are enough observations to check for
        if len(observs) < amount:
            return False

        # build a list to save all the components
        all_comps = [x.meta_data.get("components") if x.meta_data.get("components") is not None else x.serie for x in observs]
        # flatten the list
        all_comps = list(flatten(all_comps))
        print(all_comps)

        # count all the occurences of the elements in the list
        occ_elems = Counter(all_comps)

        # check if the max amount has been reached
        if amount in occ_elems.values():
            return True
        else:
            return False


def flatten(lst):
    """Takes a list with lists and normal strings and flattens it.
    https://stackoverflow.com/questions/5286541/how-can-i-flatten-lists-without-splitting-strings

    Args:
        lst (list): The list to be flattened

    Yields:
        String: Yields the next String it comes across
    """
    for x in lst:
        if hasattr(x, '__iter__') and not isinstance(x, str):
            for y in flatten(x):
                yield y
        else:
            yield x
