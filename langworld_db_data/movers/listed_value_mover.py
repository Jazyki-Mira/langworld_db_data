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
