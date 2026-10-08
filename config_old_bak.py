from pathlib import Path


# ============================================================
# PROJECT
# ============================================================

PROJECT_NAME = "RA3 Crystallography"


# ============================================================
# ROOT DIRECTORIES
# ============================================================

# Add as many root directories as needed.
#
# The program searches each root independently and then
# combines the matching datasets.

ROOT_DIRS = [
    Path(r"path/to/data"),
    # Path(r"path/to/another_dataset"),
    # Path(r"path/to/more_data"),
]


# ============================================================
# DATASET SEARCH
# ============================================================

# Folder names containing this string are treated as datasets.
SEARCH_STRING = "RA3"

# True  = case-sensitive
# False = case-insensitive
CASE_SENSITIVE = False

# Maximum search depth:
#
# 0      = do not inspect subdirectories
# 1      = immediate subdirectories of root
# 2      = two levels down
# 3      = three levels down
# None   = unlimited recursion
#
SEARCH_RECURSION_DEPTH = 1


# ============================================================
# PROCESSING LIMIT
# ============================================================

# Useful for testing.
#
# Example:
#     15     -> process only first 15 datasets
#     None   -> process all datasets
#
MAX_FOLDERS_TO_PROCESS = None


# ============================================================
# OUTPUT
# ============================================================

OUTPUT_DIR = Path(r"U:")

OUTPUT_PREFIX = SEARCH_STRING + "_summary"

ADD_TIMESTAMP_TO_FILENAME = True

TIMESTAMP_FORMAT = "%d%m%y%H%M"


# ============================================================
# RODHYPIX
# ============================================================

RODHYPIX_FOLDER_NAME = "frames"

RODHYPIX_EXTENSION = ".rodhypix"

# False = inspect only frames/
# True  = recursively search inside frames/
RODHYPIX_RECURSIVE = False

# Only the first matching .rodhypix is required.
FIRST_RODHYPIX_ONLY = True


# ============================================================
# INS FILE
# ============================================================

INS_STRUCT_FOLDER = "struct"

# Expected directory:
#
# struct/
#     olex2_RA3_xxx_auto/
#
INS_OLEX_PREFIX = "olex2_"

INS_AUTO_SUFFIX = "_auto"

INS_EXTENSION = ".ins"

# False = inspect files directly inside *_auto/
# True  = recursively search inside *_auto/
INS_RECURSIVE = False

FIRST_INS_ONLY = True


# ============================================================
# UNIT CELL
# ============================================================

# SHELX CELL syntax:
#
# CELL wavelength a b c alpha beta gamma
#
# The wavelength is not stored as part of UnitCell.
IGNORE_CELL_WAVELENGTH = True


# ============================================================
# UNIT-CELL CLUSTERING
# ============================================================

# Current simple clustering method.
#
# Length tolerance is in Å.
LENGTH_TOLERANCE = 0.2

# Angle tolerance is in degrees.
ANGLE_TOLERANCE = 0.5


# ============================================================
# UNIT-CELL SOURCE
# ============================================================

# Current source:
#
# "ins" = obtain unit cell from .ins
# "cap" = future CAP/CrysAlisPro indexing
#
# Later this can become a selectable workflow.
UNIT_CELL_SOURCE = "ins"


# ============================================================
# CAP SETTINGS
# ============================================================

# CAP is currently not active.
CAP_ENABLED = True

# These will be populated after we integrate cap-auto.
CAP_PEAK_FINDING = True
CAP_MULTICRYSTAL_INDEXING = True
CAP_UNIT_CELL_REFINEMENT = True

# For single domain "um ttt" for twin "um twinttt"
TWIN_MULTICRYSTAL_INDEXING_COMMAND = "um ttt"

# Peak hunting options
SMART_PEAK_HUNTING_COMMAND = (
    "ph snogui_pars "
    "1000 20 1 0 2 2 10 10 0 0 1 0 0.0 1000.0"
)

# ------------------------------------------------------------
# CAP .PAR FILE SELECTION
# ------------------------------------------------------------

# Preferred filename prefixes, in descending priority.
#
# For a dataset such as RA3-13do:
#
#   RA3-13do.par       -> priority 1
#   wit_RA3-13do.par   -> priority 2
#   pre_RA3-13do.par   -> priority 3
#    "", "wit_", "pre_",
#
# Empty prefix means the original dataset filename.
CAP_PAR_PREFIX_PREFERENCE = [
    "pre_", "wit_", "",
    
]

# ============================================================
# CCDC SETTINGS
# ============================================================

CCDC_ENABLED = False

# Future options:
#
# "csd"
# "local"
# "reduced_cell"
#
CCDC_SEARCH_MODE = "reduced_cell"


# ============================================================
# GEMMI SETTINGS
# ============================================================

# Gemmi will initially be optional.
GEMMI_ENABLED = False

# Possible future reduction methods:
#
# "niggli"
# "buerger"
# "selling"
#
GEMMI_REDUCTION_METHOD = "niggli"


# ============================================================
# CLUSTERING METHOD
# ============================================================

# Current method:
#
# "simple" = direct unit-cell tolerance comparison
#
# Future:
#
# "reduced_cell"
# "hierarchical"
# "dbscan"
# "intensity"
#
CLUSTERING_METHOD = "simple"


# ============================================================
# FOLDER SIZE
# ============================================================

# Supported:
#
# "B"
# "KB"
# "MB"
# "GB"
#
SIZE_UNIT = "MB"


# ============================================================
# DEBUG
# ============================================================

DEBUG = True

DEBUG_SEARCH = True

DEBUG_RODHYPIX = True

DEBUG_INS = True

DEBUG_CELL = True

DEBUG_SIZE = True

DEBUG_CAP = True

DEBUG_CCDC = True

DEBUG_GEMMI = True

DEBUG_PHASE = True


# ============================================================
# EXCEL
# ============================================================

EXCEL_SHEET_NAME = "Summary"

EXCEL_DATE_FORMAT = "yyyy-mm-dd hh:mm:ss"

EXCEL_SIZE_FORMAT = "0.00"

EXCEL_CELL_FORMAT = "0.000000"

EXCEL_FREEZE_PANES = "A2"


# ============================================================
# PHASE COLOURS
# ============================================================

PHASE_COLOURS = [
    "FFFF00",  # Yellow
    "00FF00",  # Green
    "00FFFF",  # Cyan
    "FF00FF",  # Magenta
    "FFA500",  # Orange
    "ADD8E6",  # Light blue
    "90EE90",  # Light green
    "DDA0DD",  # Plum
    "F4A460",  # Sandy brown
    "FFB6C1",  # Light pink
    "D3D3D3",  # Light gray
    "FFD700",  # Gold
    "98FB98",  # Pale green
    "87CEEB",  # Sky blue
    "EE82EE",  # Violet
]