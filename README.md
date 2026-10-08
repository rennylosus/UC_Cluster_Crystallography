# UC Crystallography Automation

This program provides an automated crystallographic data processing pipeline. It recursively discovers target datasets within configured directories, parses metadata, does multi-crystal indexing via CrysAlisPro (CAP), performs unit-cell finding, and clusters the results into groups.

## Key Features

* **Dataset Discovery**: Recursively searches root directories for target dataset folders (e.g., matching "RA3").
* **Metadata Parsing**: Reads metadata from `.rodhypix` and SHELX `.ins` files (extracting `CELL` parameters).
* **CrysAlisPro (CAP) Integration**: Runs automated multi-crystal indexing, peak finding, and cell refinement through a persistent CAP session.
* **Unit Cell Reduction**: Utilizes Gemmi (Niggli reduction) for standardizing unit cells.
* **Global Clustering**: Groups extracted unit cells across all datasets based on length and angle tolerances, identifying potential matching crystallographic phases.
* **Live Reporting**: Generates a live-updating HTML report and a final Excel summary sheet with the clustering results.

## Setup and Run

1. **Install Dependencies**: Install the required Python packages using:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. **Configuration**: Edit `config.py` to specify your data search paths (`ROOT_DIRS`), output directories, dataset naming conventions, and to toggle CAP or Gemmi integrations.
3. **Execution**: Run the main script from this directory:
   ```bash
   python main.py
   ```
   *Note: The configured output directory must be writable.*

## Technical Notes

* Groups are unit-cell groupings based on parameter tolerances and do not strictly establish final phase identity.
* CAP and CCDC integrations are designed with clear boundaries. CCDC and Gemmi functionalities are configurable and can be expanded in the future.

## AI
* Written with the help of OpenAI