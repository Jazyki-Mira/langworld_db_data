![GitHub Actions](https://github.com/Jazyki-Mira/langworld_db_data/actions/workflows/pytest.yml/badge.svg)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Jazyki-Mira/langworld_db_data/master.svg)](https://results.pre-commit.ci/latest/github/Jazyki-Mira/langworld_db_data/master)
[![codecov](https://codecov.io/gh/Jazyki-Mira/langworld_db_data/graph/badge.svg?token=MAG06T2QAF)](https://codecov.io/gh/Jazyki-Mira/langworld_db_data)

# "Languages of the World": data files
Data files for Jazyki Mira (Languages of the World) database.

This repository can be pulled into other repositories 
with actual apps (e.g. using `git subtree`). 

The [*langworld_db_data*](langworld_db_data) package
contains the code used for preparing and validating 
the data files
(the tests for it are [in a separate directory](tests)).

The actual data is in [the directory of the same name](data).
Most of these files are meant to be edited by hand
(they are then validated programmatically), but the 
[CLDF](https://cldf.clld.org/) 
`StructureDataset` [here](data/cldf) is generated programmatically using 
[*pycldf*](https://github.com/cldf/pycldf).

## For editors of feature profiles

Converter from Excel to CSV can be found in [`langworld_db_data/tools/convert_from_excel/`](langworld_db_data/tools/convert_from_excel).

[![License](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)
