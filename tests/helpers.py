import logging

logging.basicConfig(level=logging.DEBUG)

from pathlib import Path

from tinybear.csv_xls import read_plain_rows_from_csv
from tinybear.txt import read_non_empty_lines_from_txt_file


logger = logging.getLogger(__name__)


def check_existence_of_output_csv_file_and_compare_with_gold_standard(
    output_file: Path, gold_standard_file: Path, unlink_if_successful: bool = True
) -> None:
    """Checks if output file exists first, then
    compares CSV output with a gold standard file
    on a line by line basis.

    If no exception is thrown, deletes test output file
    (override by setting `unlink_if_successful` to `False`).
    """
    print(f"TEST: checking existence of output file {output_file}")
    assert output_file.exists()

    print(
        f"TEST: comparing test output file {output_file.name} "
        f"with gold standard file {gold_standard_file.name}"
    )
    output_lines = read_plain_rows_from_csv(output_file)
    gold_standard_lines = read_plain_rows_from_csv(gold_standard_file)

    for output_line, gold_standard_line in zip(output_lines, gold_standard_lines):
        assert output_line == gold_standard_line, (
            f"Output line {output_line} does not match expected line" f" {gold_standard_line}"
        )

    if unlink_if_successful:
        print(f"Deleting test output file {output_file.name}")
        output_file.unlink()


def check_existence_of_output_csv_files_in_dir_and_compare_them_with_gold_standards(
    output_dir: Path,
    gold_standard_dir: Path,
    unlink_files_if_successful: bool = True,
    remove_output_dir_if_successful: bool = False,
) -> None:
    """Check if all files in gold standard dir have their
    counterparts in output dir, then compare each CSV
    output with its gold standard counterpart on a line
    by line basis.

    Note that, for check to run successfully, output files
    and their gold standard counterparts must share name.

    If check is successful, delete test output files
    (override by setting `unlink_if_successful` to `False`).
    If specified so, also delete output dir.
    """
    logger.info(gold_standard_dir)
    files_that_must_be_present_in_output = list(gold_standard_dir.glob("*.csv"))
    for entry in gold_standard_dir.iterdir():
        logger.info(entry)
    logger.info(files_that_must_be_present_in_output)
    for file in files_that_must_be_present_in_output:
        logger.info(f"TEST: checking existence of output file {file.name} in output dir")
        assert Path(output_dir / file.name).exists()
    # Should there be a check on files present in output dir
    # with no counterparts in gold standard dir?

    filenames_present_in_output_dir = [file.name for file in files_that_must_be_present_in_output]
    logger.info(filenames_present_in_output_dir)

    for filename in filenames_present_in_output_dir:
        output_filepath = Path(output_dir / filename)
        logger.info(
            f"TEST: comparing test output file {filename} "
            f"with gold standard file {filename}"
        )
        output_lines = read_plain_rows_from_csv(output_filepath)
        gold_standard_lines = read_plain_rows_from_csv(gold_standard_dir / filename)

        for output_line, gold_standard_line in zip(output_lines, gold_standard_lines):
            assert output_line == gold_standard_line, (
                f"Output line {output_line} does not match expected line {gold_standard_line}"
            )
    logger.info(filenames_present_in_output_dir)

    if unlink_files_if_successful:
        for filename in filenames_present_in_output_dir:
            output_filepath = Path(output_dir / filename)
            logger.info(f"Deleting test output file {output_filepath}")
            output_filepath.unlink()

    if remove_output_dir_if_successful:
        logger.info(f"Deleting test output dir {output_dir.name}")
        output_dir.rmdir()


def check_existence_of_output_txt_file_and_compare_with_benchmark(
    output_file: Path, benchmark_file: Path, unlink_if_successful: bool = True
) -> None:
    """Checks if output file exists first, then
    compares TXT output with a benchmark file on a line-by-line basis.

    If no exception is thrown, deletes test output file
    (override by setting `unlink_if_successful` to `False`).
    """
    print(f"TEST: checking existence of output file {output_file}")
    assert output_file.exists()

    print(
        f"TEST: comparing test output file {output_file.name} "
        f"with benchmark file {benchmark_file.name}"
    )
    output_lines = read_non_empty_lines_from_txt_file(output_file)
    benchmark_lines = read_non_empty_lines_from_txt_file(benchmark_file)

    for output_line, benchmark_line in zip(output_lines, benchmark_lines):
        assert output_line == benchmark_line, (
            f"Output line {output_line} does not match expected line" f" {benchmark_line}"
        )

    if unlink_if_successful:
        print(f"Deleting test output file {output_file.name}")
        output_file.unlink()
