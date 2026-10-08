from config import (
    ROOT_DIRS,
    MAX_FOLDERS_TO_PROCESS,
)

from datasets.finder import (
    find_target_folders_multiple_roots,
)

from cap.connection import (
    find_par_file,
    CAPConnection,
)


# ============================================================
# FIND EXPERIMENT
# ============================================================

folders = find_target_folders_multiple_roots(
    ROOT_DIRS
)

par_file = None

for folder in folders[:MAX_FOLDERS_TO_PROCESS]:

    candidate = find_par_file(folder)

    if candidate is not None:
        par_file = candidate
        break


if par_file is None:
    raise RuntimeError(
        "No CrysAlisPro .par file was found."
    )


print()
print("=" * 70)
print("CAP EXPERIMENT LOAD TEST")
print("=" * 70)

print()
print("Experiment:")
print(par_file)


# ============================================================
# START CAP WITHOUT PAR FILE
# ============================================================

connection = CAPConnection(
    par_file=None,
    start_now=True,
    raise_on_error=False,
)


print()
print("Starting CrysAlisPro in listen mode...")

connected = connection.connect()

print()
print(f"Connected: {connected}")

if not connected:
    raise RuntimeError(
        "CAP connection failed."
    )


# ============================================================
# LOAD EXPERIMENT
# ============================================================

print()
print("-" * 70)
print("LOADING EXPERIMENT")
print("-" * 70)

print()
print("Loading:")
print(par_file)

result = connection.session.load_experiment(
    str(par_file)
)

print()
print("Load result:")
print(result)


# ============================================================
# STATUS
# ============================================================

print()
print("CAP status:")
print(connection.get_status())


# ============================================================
# DISCONNECT
# ============================================================

print()
print("Disconnecting...")

connection.disconnect()

print()
print("Finished.")