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

[![License](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)
