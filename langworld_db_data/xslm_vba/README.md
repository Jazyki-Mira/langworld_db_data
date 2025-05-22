This folder contains the **template of a feature profile** in XSLM format, and, separately, **code of VBA macros** included in this template for better version control.

Filename `_template.xlsm` begins with an underscore so that the template doesn't get lost when it's around files with filled feature profiles.

To edit a particular feature profile in Excel, one must **copy** the template into a file named with **ID of a doculect**, then open this new file and run a macro that downloads the data for this doculect from CSV in this GitHub repository.

File `bulk_copy_template_and_load_csv.vba` contains a macro that
can be run a temporarily created Excel file, but not inside `_template.xlsm`.
It copies the template to a new file, then downloads data from CSV files in this repository into it.
Useful for bulk creation of feature profiles.
