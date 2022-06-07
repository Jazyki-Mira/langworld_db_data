from pathlib import Path

from langworld_db_data.featureprofiletools.data_structures import ValueForFeatureProfileDictionary
from langworld_db_data.filetools.csv_xls import write_csv


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
    ):
        rows_to_write = []

        for key in feature_dict:
            row_dict = {'feature_id': key}
            row_dict.update(**feature_dict[key]._asdict())
            rows_to_write.append(row_dict)

        write_csv(rows_to_write, path_to_file=output_path, overwrite=True, delimiter=',')


if __name__ == '__main__':
    pass
