from core.models import UnitCell
from crystallography.unit_cell import (
    calculate_volume,
    to_gemmi,
    from_gemmi,
    reduce_cell,
)


cell = UnitCell(
    a=20.839999,
    b=20.839999,
    c=14.391,
    alpha=90.0,
    beta=90.0,
    gamma=90.0,
    source="TEST",
)

print("Original:")
print(cell.as_tuple())

print()
print("Volume:")
print(calculate_volume(cell))

print()
print("Gemmi conversion:")

gemmi_cell = to_gemmi(cell)

print(
    gemmi_cell.a,
    gemmi_cell.b,
    gemmi_cell.c,
    gemmi_cell.alpha,
    gemmi_cell.beta,
    gemmi_cell.gamma,
)

print()
print("Back from Gemmi:")

converted = from_gemmi(gemmi_cell)

print(converted.as_tuple())

print()
print("Niggli reduction:")

reduced = reduce_cell(
    cell,
    method="niggli",
)

print(reduced.as_tuple())
print("Reduced volume:", reduced.volume)

buerger = reduce_cell(cell, method="buerger")

print()
print("Buerger reduction:")
print(buerger.as_tuple())
print("Buerger volume:", buerger.volume)


cell2 = UnitCell(
    a=10.123,
    b=11.456,
    c=12.789,
    alpha=89.2,
    beta=102.4,
    gamma=91.7,
    source="TEST",
)

print()
print("Non-orthogonal cell:")
print(cell2.as_tuple())
print("Valid:", cell2.is_valid())
print("Volume:", cell2.volume)

reduced2 = reduce_cell(cell2, method="niggli")

print()
print("Reduced non-orthogonal cell:")
print(reduced2.as_tuple())
print("Reduced volume:", reduced2.volume)