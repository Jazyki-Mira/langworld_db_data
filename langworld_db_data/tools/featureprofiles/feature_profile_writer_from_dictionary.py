from dataclasses import asdict
from pathlib import Path

from langworld_db_data.constants.literals import KEY_FOR_FEATURE_ID
from langworld_db_data.tools.featureprofiles.data_structures import (
    ValueForFeatureProfileDictionary,
)
from langworld_db_data.tools.files.csv_xls import write_csv


class FeatureProfileWriterFromDictionary:
    """Class for writing CSV files with feature profiles.
    The main method, `.write()`, accepts as input a dictionary
    where keys are feature IDs and values are `ValueForFeatureProfileDictionary`
    objects.

    The class is intended for use in combination with
    some other functionality that manipulates feature profile data.

    If you already have rows of data ready to be written to CSV,
    you do not need this class. Just write them to CSV with `filetools`.
    """

    @staticmethod
    def write(
        feature_dict: dict[str, ValueForFeatureProfileDictionary],
        output_path: Path,
    ) -> None:
        rows_to_write = []

        for key in feature_dict:
            row_dict = {KEY_FOR_FEATURE_ID: key}
            row_dict.update(asdict(feature_dict[key]))
            rows_to_write.append(row_dict)

        write_csv(rows_to_write, path_to_file=output_path, overwrite=True, delimiter=",")
