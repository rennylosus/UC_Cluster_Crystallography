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
# FIND A REAL EXPERIMENT
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
print("CAP CONNECTION TEST")
print("=" * 70)

print()
print(f"Experiment:")
print(par_file)


# ============================================================
# CONNECT
# ============================================================

connection = CAPConnection(
    par_file=par_file,
    start_now=True,
    raise_on_error=False,
)


print()
print("Connecting to CrysAlisPro...")

connected = connection.connect()

print()
print(f"Connected: {connected}")


if not connected:
    raise RuntimeError(
        "CAP connection failed."
    )


# ============================================================
# BASIC INFORMATION
# ============================================================

print()
print("-" * 70)
print("CAP INFORMATION")
print("-" * 70)

print()
print("CAP version:")
print(connection.cap_version)

print()
print("CAP status:")
print(connection.get_status())

print()
print("Command history:")
print(connection.history)


# ============================================================
# DISCONNECT
# ============================================================

print()
print("Disconnecting...")

connection.disconnect()

print()
print("Finished.")