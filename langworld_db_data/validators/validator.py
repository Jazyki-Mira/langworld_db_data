from abc import ABC, abstractmethod
from pathlib import Path

from langworld_db_data.tools.files.csv_xls import read_column_from_csv


class ValidatorError(ValueError):
    pass


class Validator(ABC):
    @abstractmethod
    def validate(self) -> None:
        pass

    @staticmethod
    def _read_ids(path_to_file: Path) -> list[str]:
        """A helper method for a common operation:
        reads CSV file and returns values of 'id' column.
        """
        return read_column_from_csv(path_to_file=path_to_file, column_name="id")
