# Converter of feature profiles from Excel to CSV

1. Put Excel files (created from the [template](../../xslm_vba/_template.xlsm)) into [`../input_xlsm`](input_xlsm)
2. Run [`convert_from_excel.py`](convert_from_excel.py)
3. Converted CSV files will be put into [`../output_csv`](output_csv)
4. Move these CSV files to [directory with feature profiles](../../../data/feature_profiles).
5. Run [`/langworld_db_data/main.py`](../../main.py) that will check your CSV and update other data files.
6. If it throws errors, you can either fix respective CSV files manually or fix Excel files and run conversion again.
