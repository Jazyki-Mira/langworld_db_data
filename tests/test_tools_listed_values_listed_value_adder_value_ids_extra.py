# These tests were created using AI assistant to improve coverage.
# They use a different approach, so keeping them in a separate file.
import csv

from langworld_db_data.tools.listed_values.listed_value_adder import ListedValueAdder


# 1. Covers combined value id with "&" (atomic increment inside combined value)
def test_increment_value_ids_combined(monkeypatch, tmp_path):
    csv_path = tmp_path / "combo.csv"
    input_rows = [
        {"feature_id": "A-1", "value_type": "listed", "value_id": "A-1-1&A-1-2"},
        {"feature_id": "A-1", "value_type": "listed", "value_id": "A-1-3"},
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=input_rows[0].keys())
        writer.writeheader()
        writer.writerows(input_rows)

    def fake_read_dicts_from_csv(p):
        with open(csv_path) as f:
            return list(csv.DictReader(f))

    def fake_write_csv(rows_arg, path_to_file, **kwargs):
        with open(path_to_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows_arg[0].keys())
            writer.writeheader()
            for r in rows_arg:
                writer.writerow(r)

    monkeypatch.setattr(
        "langworld_db_data.tools.listed_values.listed_value_adder.read_dicts_from_csv",
        fake_read_dicts_from_csv,
    )
    monkeypatch.setattr(
        "langworld_db_data.tools.listed_values.listed_value_adder.write_csv", fake_write_csv
    )
    ListedValueAdder._increment_value_ids_in_feature_profiles(
        new_value_id="A-1-1",
        input_files=[csv_path],
        output_dir=tmp_path,
    )
    with open(tmp_path / "combo.csv") as f:
        out = list(csv.DictReader(f))
    assert out[0]["value_id"] == "A-1-2&A-1-3"
    assert out[1]["value_id"] == "A-1-4"


# 2. Covers else-branch (atomic, not-combined, requires actual increment)
def test_increment_value_ids_atomic(monkeypatch, tmp_path):
    csv_path = tmp_path / "atomic.csv"
    input_rows = [
        {"feature_id": "A-1", "value_type": "listed", "value_id": "A-1-3"},
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=input_rows[0].keys())
        writer.writeheader()
        writer.writerows(input_rows)

    def fake_read_dicts_from_csv(p):
        with open(csv_path) as f:
            return list(csv.DictReader(f))

    def fake_write_csv(rows_arg, path_to_file, **kwargs):
        with open(path_to_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows_arg[0].keys())
            writer.writeheader()
            for r in rows_arg:
                writer.writerow(r)

    monkeypatch.setattr(
        "langworld_db_data.tools.listed_values.listed_value_adder.read_dicts_from_csv",
        fake_read_dicts_from_csv,
    )
    monkeypatch.setattr(
        "langworld_db_data.tools.listed_values.listed_value_adder.write_csv", fake_write_csv
    )
    ListedValueAdder._increment_value_ids_in_feature_profiles(
        new_value_id="A-1-2",
        input_files=[csv_path],
        output_dir=tmp_path,
    )
    with open(tmp_path / "atomic.csv") as f:
        out = list(csv.DictReader(f))
    assert out[0]["value_id"] == "A-1-4"


# 3. Covers the no-op case (is_changed always False, so file is never written)
def test_increment_value_ids_noop(monkeypatch, tmp_path):
    csv_path = tmp_path / "noop.csv"
    input_rows = [
        {"feature_id": "A-1", "value_type": "listed", "value_id": "A-1-1"},
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=input_rows[0].keys())
        writer.writeheader()
        writer.writerows(input_rows)

    def fake_read_dicts_from_csv(p):
        with open(csv_path) as f:
            return list(csv.DictReader(f))

    written = []

    def fake_write_csv(rows_arg, path_to_file, **kwargs):
        written.append(True)

    monkeypatch.setattr(
        "langworld_db_data.tools.listed_values.listed_value_adder.read_dicts_from_csv",
        fake_read_dicts_from_csv,
    )
    monkeypatch.setattr(
        "langworld_db_data.tools.listed_values.listed_value_adder.write_csv", fake_write_csv
    )
    ListedValueAdder._increment_value_ids_in_feature_profiles(
        new_value_id="A-1-5",
        input_files=[csv_path],
        output_dir=tmp_path,
    )
    assert not written  # write_csv never called
