from config import (
    ROOT_DIRS,
    MAX_FOLDERS_TO_PROCESS,
)

from datasets.finder import (
    find_target_folders_multiple_roots,
)

from cap.connection import (
    CAPConnection,
    find_par_file,
)


# ============================================================
# FIND A REAL EXPERIMENT
# ============================================================

print()
print("=" * 70)
print("CAP CONNECTION TEST")
print("=" * 70)

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
print("Experiment:")
print(par_file)


# ============================================================
# CREATE CAP CONNECTION
# ============================================================

connection = CAPConnection(
    par_file=par_file,
    start_now=True,
    raise_on_error=False,
)


# ============================================================
# CONNECT TO CRYSALISPRO
# ============================================================

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
# CAP INFORMATION
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
# BASIC CAP COMMUNICATION TEST
# ============================================================

print()
print("-" * 70)
print("CAP COMMUNICATION TEST")
print("-" * 70)

print()
print("CAP version:")
print(connection.cap_version)

print()
print("CAP status:")
print(connection.get_status())

print()
print("Sending harmless CAP command...")

result = connection.execute(
    "xx sleep 1",
    timeout=5,
)

print()
print("Command result:")
print(result)

print()
print("Success:")
print(result.success)

print()
print("Warnings:")
print(result.warnings)

print()
print("Errors:")
print(result.errors)

print()
print("Execution time:")
print(result.execution_time)

print()
print("Command history:")
for item in connection.history:
    print(item)


# ============================================================
# DISCONNECT
# ============================================================

print()
print("Disconnecting...")

connection.disconnect()

print()
print("Finished.")

