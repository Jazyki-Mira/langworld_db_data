# These tests were created using AI assistant to improve coverage.
# They use a different approach, so keeping them in a separate file.
import csv

from langworld_db_data.tools.features.feature_adder import FeatureAdder


def make_feature_profile_csv(tmp_path, rows, fname="profile.csv"):
    keys = [
        "feature_id",
        "ru_name_of_feature",
        "value_type",
        "value_id",
        "ru_name_of_value",
        "ru_comment",
        "en_comment",
    ]
    path = tmp_path / fname
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_add_feature_to_feature_profiles_print_and_updates(monkeypatch, tmp_path, capsys):
    # One row, triggers main feature ID update code path, value_type = 'listed', single value
    path = make_feature_profile_csv(
        tmp_path,
        [
            {
                "feature_id": "A-1",
                "ru_name_of_feature": "Фича1",
                "value_type": "listed",
                "value_id": "A-1-5",
                "ru_name_of_value": "вал",
                "ru_comment": "",
                "en_comment": "",
            }
        ],
    )

    # Patch all IO to operate on above file
    def fake_read_csv(file):
        with open(path) as f:
            return list(csv.DictReader(f))

    def fake_write_csv(rows, path_to_file, **kwargs):
        with open(path_to_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    monkeypatch.setattr(
        "langworld_db_data.tools.features.feature_adder.read_dicts_from_csv", fake_read_csv
    )
    monkeypatch.setattr("langworld_db_data.tools.features.feature_adder.write_csv", fake_write_csv)

    # The actual test
    adder = FeatureAdder(
        input_file_with_features=tmp_path / "dummy.csv",
        output_file_with_features=tmp_path / "dummy_out.csv",
        input_file_with_listed_values=tmp_path / "dummy2.csv",
        output_file_with_listed_values=tmp_path / "dummy2_out.csv",
        input_dir_with_feature_profiles=tmp_path,
        output_dir_with_feature_profiles=tmp_path,
    )
    adder._add_feature_to_feature_profiles(feature_id="A-1", feature_ru="ФичаX")
    captured = capsys.readouterr().out
    assert "Adding feature A-1 to feature profiles with value type 'not_stated'" in captured


def test_add_feature_to_feature_profiles_combined_value_ids(monkeypatch, tmp_path, capsys):
    # One row with combined value_id triggers '&' path
    path = make_feature_profile_csv(
        tmp_path,
        [
            {
                "feature_id": "B-2",
                "ru_name_of_feature": "Фича2",
                "value_type": "listed",
                "value_id": "B-2-3&B-2-4",
                "ru_name_of_value": "вал2",
                "ru_comment": "",
                "en_comment": "",
            }
        ],
        fname="profile2.csv",
    )

    def fake_read_csv(file):
        with open(path) as f:
            return list(csv.DictReader(f))

    def fake_write_csv(rows, path_to_file, **kwargs):
        with open(path_to_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    monkeypatch.setattr(
        "langworld_db_data.tools.features.feature_adder.read_dicts_from_csv", fake_read_csv
    )
    monkeypatch.setattr("langworld_db_data.tools.features.feature_adder.write_csv", fake_write_csv)

    adder = FeatureAdder(
        input_file_with_features=tmp_path / "dummy.csv",
        output_file_with_features=tmp_path / "dummy_out.csv",
        input_file_with_listed_values=tmp_path / "dummy2.csv",
        output_file_with_listed_values=tmp_path / "dummy2_out.csv",
        input_dir_with_feature_profiles=tmp_path,
        output_dir_with_feature_profiles=tmp_path,
    )
    adder._add_feature_to_feature_profiles(feature_id="B-2", feature_ru="ФичаY")
    captured = capsys.readouterr().out
    assert "Adding feature B-2 to feature profiles with value type 'not_stated'" in captured
