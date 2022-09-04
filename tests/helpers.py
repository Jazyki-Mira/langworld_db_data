from pathlib import Path

from langworld_db_data.filetools.csv_xls import read_csv


def check_existence_of_output_csv_file_and_compare_with_gold_standard(output_file: Path,
                                                                      gold_standard_file: Path,
                                                                      unlink_if_successful: bool = True):
    """Checks if output file exists first, then
    compares CSV output with a gold standard file
    on a line by line basis.

    If no exception is thrown, deletes test output file
    (override by setting `unlink_if_successful` to `False`).
    """
    print(f'TEST: checking existence of output file {output_file}')
    assert output_file.exists()

    print(f'TEST: comparing test output file {output_file.name} '
          f'with gold standard file {gold_standard_file.name}')
    output_lines = read_csv(output_file, read_as='plain_rows')
    gold_standard_lines = read_csv(gold_standard_file, read_as='plain_rows')

    for output_line, gold_standard_line in zip(output_lines, gold_standard_lines):
        assert output_line == gold_standard_line, \
            f'Output line {output_line} does not match expected line {gold_standard_line}'

    if unlink_if_successful:
        print(f'Deleting test output file {output_file.name}')
        output_file.unlink()
