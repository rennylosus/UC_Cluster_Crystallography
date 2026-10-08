import gemmi

print("Gemmi version:", gemmi.__version__)

cell = gemmi.UnitCell(
    20.839999,
    20.839999,
    14.391,
    90,
    90,
    90,
)

print("\nUnitCell methods containing 'reduce':")

for name in dir(cell):
    if "reduce" in name.lower():
        print(name)

print("\nGemmi attributes containing 'reduce':")

for name in dir(gemmi):
    if "reduce" in name.lower():
        print(name)