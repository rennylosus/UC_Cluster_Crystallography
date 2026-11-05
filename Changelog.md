# Changelog

All notable changes to this project are documented in this file.

## [1.1.0] - 2026-11-05

### Improved

- **CrysAlisPro `.par` file discovery and selection**
  - Improved `.par` file discovery and selection in `datasets/processor.py`.
  - Added a prioritised selection strategy:
    1. Exact dataset-name match.
    2. Dataset-name prefix match.
    3. Fallback to another available `.par` file when its name differs from the dataset root directory.

- **CAP parameter file reporting and integration**
  - Added storage of the selected `.par` file path and directory in `dataset.cap_par_file` and `dataset.cap_par_directory`.
  - Added the selected `.par` file path and directory to Excel and HTML reports.
  - Ensured the selected `.par` file is passed to CAP and used by `run_indexing()`.

- **Flexible unit-cell indexing**
  - Separated peak hunting and twin/multicrystal indexing into independently controlled operations.
  - Added support for retrieving existing unit-cell information using CAP's `um i` command when twin/multicrystal indexing is disabled.
  - Allows unit-cell processing with or without peak hunting and twin/multicrystal indexing, independently controlled through the GUI or `config.py`.

### Fixed

- Excluded `*_cracker.par` files from fallback `.par` file selection.
- Added debug warnings when a fallback `.par` file is selected.

## [1.0.0] - 2026-10-08

- Initial release.
