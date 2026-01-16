"""
Script para verificar y arreglar las funciones loadDownloads y loadHistory
"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Verificar si las funciones existen
if 'loadDownloads' not in content:
    print("✗ ERROR: loadDownloads no existe en el archivo")
else:
    print("✓ loadDownloads encontrada")
    
if 'loadHistory' not in content:
    print("✗ ERROR: loadHistory no existe en el archivo")
else:
    print("✓ loadHistory encontrada")

# Buscar errores de sintaxis comunes
import re

# Buscar funciones async que no deberían serlo
async_funcs = re.findall(r'async function (\w+)', content)
print(f"\nFunciones async encontradas: {async_funcs}")

# Verificar que showTab existe
if 'function showTab' in content:
    print("✓ showTab encontrada")
else:
    print("✗ ERROR: showTab no encontrada")

# Buscar si hay errores de await sin async
lines = content.split('\n')
for i, line in enumerate(lines, 1):
    if 'await show' in line and 'async function' not in lines[max(0, i-10):i]:
        # Verificar si está dentro de una función async
        func_start = -1
        for j in range(max(0, i-50), i):
            if 'async function' in lines[j]:
                func_start = j
                break
        if func_start == -1:
            print(f"⚠ Línea {i}: await fuera de función async: {line.strip()[:80]}")
