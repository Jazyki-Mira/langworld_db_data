import pytest

from langworld_db_data.removers.listed_value_remover import (
    ListedValueRemover,
    ListedValueRemoverError,
)
from tests.helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard

# To my mind, this will probably be a structure isomorphic to adders
# It should be, first of all, able to remove a value from the inventory
# and subsequently update the IDs of reminiscent values
# Moreover, as was discussed earlier, it should not simply remove values but pop them
# so that the popped value will be available to insert somewhere else with ListedValueAdder


@pytest.fixture(scope="function")
def test_remover():
    return ListedValueRemover()


# Tests
def test_remove_listed_value_from_end_of_feature(test_remover):
    # Check if the target value is removed from the inventory (the very end of the feature) and saved into a variable
    # A-5-8 should be removed
    pass


def test_remove_listed_value_from_middle_of_feature(test_remover):
    # Check if the target value is removed from the inventory (not the end of the feature) and saved into a variable
    # A-5-5 should be removed
    pass


def test_remove_listed_value_throws_exception_with_invalid_value_id(test_remover):
    pass


def test_remove_listed_value_throws_exception_with_value_that_does_not_exist(test_remover):
    pass

# What should the module do if it is asked to pop a value which does not exist?


# How should the removed values be changed in profiles? Should they become custom or not_stated?
# To me, it would be more logical to make them custom, again for the sake of possible movement
# However, perhaps both options may be necessary to provide

# Should we also be able to remove custom values?
