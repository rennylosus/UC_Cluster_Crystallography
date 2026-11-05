# Changelog

All notable changes to this project are documented in this file.

## [1.1.0] - 2026-11-05

### Improved
- Improved CrysAlisPro `.par` file discovery and selection in `datasets/processor.py`.
- Added a prioritised selection strategy:
  1. Exact dataset-name match.
  2. Dataset-name prefix match.
  3. Fallback to another available `.par` file when .par file has a different name from the root dir.

- Output the selected `.par` file path and its directory in Excel and HTML.
  1. Store and output the selected `.par` file path and its directory in `dataset.cap_par_file` and `dataset.cap_par_directory`.
  2. Ensure the selected `.par` file is passed to CAP and used by `run_indexing()`.

### Fixed
- Excluded `*_cracker.par` files from fallback selection.
- Added debug warnings when a fallback `.par` file is selected.

## [1.0.0] - Initial release

- Initial release.
