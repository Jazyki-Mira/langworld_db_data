from langworld_db_data.adders.listed_value_adder import ListedValueAdder
from langworld_db_data.constants.literals import ID_SEPARATOR
from langworld_db_data.filetools.csv_xls import read_dicts_from_csv, write_csv
from langworld_db_data.movers.mover import Mover, MoverError
from langworld_db_data.removers.listed_value_remover import ListedValueRemover


class ListedValueMoverError(MoverError):
    pass


class ListedValueMover(Mover):
    def __init__(  # type: ignore
        self,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.listed_value_adder = ListedValueAdder(
            input_file_with_listed_values=self.output_file_with_listed_values,  # Otherwise in tests
            # listed_value_adder opens the input inventory where the removed value is
            # present and throws an error
            input_dir_with_feature_profiles=self.input_dir_with_feature_profiles,
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
        if int(initial_value_id.split("-")[2]) == index_to_assign:
            raise ListedValueMoverError("Initial and final indices must not coincide.")
        value_to_move = self.listed_value_remover.remove_listed_value(initial_value_id)
        print(value_to_move)
        self.listed_value_adder.add_listed_value(
            feature_id=value_to_move["feature_id"],
            new_value_en=value_to_move["en"],
            new_value_ru=value_to_move["ru"],
            description_formatted_en=value_to_move["description_formatted_en"],
            description_formatted_ru=value_to_move["description_formatted_ru"],
            index_to_assign=index_to_assign,
        )
