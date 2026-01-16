"""
Script para encontrar y mostrar todas las líneas con alert() o confirm()
"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

alerts_found = []
confirms_found = []

for i, line in enumerate(lines, 1):
    if 'alert(' in line.lower():
        alerts_found.append((i, line.strip()))
    if 'confirm(' in line.lower():
        confirms_found.append((i, line.strip()))

print(f"ALERTS ENCONTRADOS: {len(alerts_found)}")
for line_num, content in alerts_found[:10]:
    print(f"  Line {line_num}: {content[:120]}")

print(f"\nCONFIRMS ENCONTRADOS: {len(confirms_found)}")
for line_num, content in confirms_found[:10]:
    print(f"  Line {line_num}: {content[:120]}")

# Save line numbers to file for reference
with open('alerts_to_replace.txt', 'w') as f:
    f.write("ALERTS:\n")
    for line_num, content in alerts_found:
        f.write(f"{line_num}: {content}\n")
    f.write("\nCONFIRMS:\n")
    for line_num, content in confirms_found:
        f.write(f"{line_num}: {content}\n")

print("\nSaved details to alerts_to_replace.txt")
