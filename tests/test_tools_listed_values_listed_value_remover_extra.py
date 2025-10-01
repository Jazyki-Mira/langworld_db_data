# These tests were created using AI assistant to improve coverage.
# They use a different approach, so keeping them in a separate file.
import csv

from langworld_db_data.tools.listed_values.listed_value_remover import ListedValueRemover

# Helper for patching
_DEF_KEYS = ["feature_id", "value_type", "value_id", "id"]


def make_csv(tmp_path, rows, fname="in.csv"):
    path = tmp_path / fname
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=_DEF_KEYS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_remover_changes_to_custom(monkeypatch, tmp_path, capsys):
    """Covers: changing listed to custom and print path (hits break)."""
    input_path = make_csv(
        tmp_path,
        [{"feature_id": "F-1", "value_type": "listed", "value_id": "F-1-3", "id": "irrelevant"}],
    )

    def fake_read_csv(path):
        with open(input_path) as f:
            return list(csv.DictReader(f))

    def fake_write_csv(rows_arg, path_to_file, **kwargs):
        with open(path_to_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows_arg[0].keys())
            writer.writeheader()
            writer.writerows(rows_arg)

    monkeypatch.setattr(
        "langworld_db_data.tools.listed_values.listed_value_remover.read_dicts_from_csv",
        fake_read_csv,
    )
    monkeypatch.setattr(
        "langworld_db_data.tools.listed_values.listed_value_remover.write_csv", fake_write_csv
    )
    remover = ListedValueRemover(
        input_file_with_listed_values=tmp_path / "never_used.csv",
        output_file_with_listed_values=tmp_path / "never_used2.csv",
        input_dir_with_feature_profiles=tmp_path,
        output_dir_with_feature_profiles=tmp_path,
    )
    remover._remove_from_feature_profiles_and_update_ids_whose_indices_are_greater_than_one_of_removed_value(
        "F-1-3"
    )
    out = capsys.readouterr().out
    assert "Changing value type to custom" in out


def test_remover_combined_value(monkeypatch, tmp_path, capsys):
    """Covers: combined value_id '&' and atomic update print path."""
    input_path = make_csv(
        tmp_path,
        [
            {
                "feature_id": "F-2",
                "value_type": "listed",
                "value_id": "F-2-4&F-2-8",
                "id": "irrelevant",
            }
        ],
        "combo.csv",
    )

    def fake_read_csv(path):
        with open(input_path) as f:
            return list(csv.DictReader(f))

    def fake_write_csv(rows_arg, path_to_file, **kwargs):
        with open(path_to_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows_arg[0].keys())
            writer.writeheader()
            writer.writerows(rows_arg)

    monkeypatch.setattr(
        "langworld_db_data.tools.listed_values.listed_value_remover.read_dicts_from_csv",
        fake_read_csv,
    )
    monkeypatch.setattr(
        "langworld_db_data.tools.listed_values.listed_value_remover.write_csv", fake_write_csv
    )
    remover = ListedValueRemover(
        input_file_with_listed_values=tmp_path / "n.csv",
        output_file_with_listed_values=tmp_path / "o.csv",
        input_dir_with_feature_profiles=tmp_path,
        output_dir_with_feature_profiles=tmp_path,
    )
    remover._remove_from_feature_profiles_and_update_ids_whose_indices_are_greater_than_one_of_removed_value(
        "F-2-8"
    )
    out = capsys.readouterr().out
    assert "Updating atomic valie ids" in out


def test_remover_regular_id_update(monkeypatch, tmp_path, capsys):
    """Covers: regular else branch (not listed/custom/&, but index decrement and print)"""
    input_path = make_csv(
        tmp_path,
        [{"feature_id": "F-3", "value_type": "listed", "value_id": "F-3-5", "id": "irrelevant"}],
        "atomic.csv",
    )

    def fake_read_csv(path):
        with open(input_path) as f:
            return list(csv.DictReader(f))

    def fake_write_csv(rows_arg, path_to_file, **kwargs):
        with open(path_to_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows_arg[0].keys())
            writer.writeheader()
            writer.writerows(rows_arg)

    monkeypatch.setattr(
        "langworld_db_data.tools.listed_values.listed_value_remover.read_dicts_from_csv",
        fake_read_csv,
    )
    monkeypatch.setattr(
        "langworld_db_data.tools.listed_values.listed_value_remover.write_csv", fake_write_csv
    )
    remover = ListedValueRemover(
        input_file_with_listed_values=tmp_path / "x.csv",
        output_file_with_listed_values=tmp_path / "y.csv",
        input_dir_with_feature_profiles=tmp_path,
        output_dir_with_feature_profiles=tmp_path,
    )
    remover._remove_from_feature_profiles_and_update_ids_whose_indices_are_greater_than_one_of_removed_value(
        "F-3-3"
    )
    out = capsys.readouterr().out
    assert "Updating value id in" in out


def test_remover_file_not_changed(monkeypatch, tmp_path, capsys):
    """Covers: else branch, file.stem is not changed"""
    input_path = make_csv(
        tmp_path,
        [{"feature_id": "F-4", "value_type": "custom", "value_id": "", "id": "irrelevant"}],
        "unchanged.csv",
    )

    def fake_read_csv(path):
        with open(input_path) as f:
            return list(csv.DictReader(f))

    def fake_write_csv(rows_arg, path_to_file, **kwargs):
        pass  # must not be called

    monkeypatch.setattr(
        "langworld_db_data.tools.listed_values.listed_value_remover.read_dicts_from_csv",
        fake_read_csv,
    )
    monkeypatch.setattr(
        "langworld_db_data.tools.listed_values.listed_value_remover.write_csv", fake_write_csv
    )
    remover = ListedValueRemover(
        input_file_with_listed_values=tmp_path / "m.csv",
        output_file_with_listed_values=tmp_path / "n.csv",
        input_dir_with_feature_profiles=tmp_path,
        output_dir_with_feature_profiles=tmp_path,
    )
    remover._remove_from_feature_profiles_and_update_ids_whose_indices_are_greater_than_one_of_removed_value(
        "F-4-6"
    )
    out = capsys.readouterr().out
    assert "unchanged is not changed" in out
