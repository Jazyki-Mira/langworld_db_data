from pathlib import Path

from langworld_db_data.adders.listed_value_adder import ListedValueAdder
from langworld_db_data.constants.literals import ID_SEPARATOR
from langworld_db_data.constants.paths import FEATURE_PROFILES_DIR, FILE_WITH_LISTED_VALUES
from langworld_db_data.filetools.csv_xls import read_dicts_from_csv, write_csv
from langworld_db_data.movers.mover import Mover, MoverError
from langworld_db_data.removers.listed_value_remover import ListedValueRemover


class ListedValueMoverError(MoverError):
    pass


class ListedValueMover(Mover):
    def __init__(  # type: ignore
        self,
        listed_value_adder_input_file_with_inventories=FILE_WITH_LISTED_VALUES,
        listed_value_adder_input_dir_with_feature_profiles=FEATURE_PROFILES_DIR,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.listed_value_adder = ListedValueAdder(
            input_file_with_listed_values=listed_value_adder_input_file_with_inventories,
            input_dir_with_feature_profiles=listed_value_adder_input_dir_with_feature_profiles,
            output_file_with_listed_values=self.output_file_with_listed_values,
            output_dir_with_feature_profiles=self.output_dir_with_feature_profiles,
        )
        self.listed_value_remover = ListedValueRemover(
            **kwargs,
        )

    def move_listed_value(
        self,
        initial_value_id: str,
        index_to_assign: int,
    ):
        """
        Moves value with the passed ID to the position of the passed index
        within the same feature. Refreshes other IDs of the feature in both
        the inventory and the feature profiles.
        """
        if int(initial_value_id.split("-")[2]) == index_to_assign:
            raise ListedValueMoverError("Initial and final indices cannot be equal.")
        value_to_move = self.listed_value_remover.remove_listed_value(initial_value_id)
        self.listed_value_adder.add_listed_value(
            feature_id=value_to_move["feature_id"],
            new_value_en=value_to_move["en"],
            new_value_ru=value_to_move["ru"],
            index_to_assign=index_to_assign,
            description_formatted_en=value_to_move["description_formatted_en"],
            description_formatted_ru=value_to_move["description_formatted_ru"],
        )
