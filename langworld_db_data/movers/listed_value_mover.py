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
            **kwargs,
        )
        self.listed_value_remover = ListedValueRemover(
            **kwargs,
        )

    def move_listed_value(
        self,
        initial_value_id: str,
        final_value_id: str,
    ):
        self._move_value_in_inventory_of_listed_values(
            initial_value_id=initial_value_id,
            final_value_id=final_value_id,
        )
        self._update_value_indices_in_inventory()

    def _move_value_in_inventory_of_listed_values(
        self,
        initial_value_id: str,
        final_value_id: str,
    ):
        pass

    @staticmethod
    def _update_value_indices_in_inventory():
        pass
