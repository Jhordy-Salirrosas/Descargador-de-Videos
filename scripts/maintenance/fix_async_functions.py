"""
Script para arreglar el problema de async en loadHistory y loadDownloads
"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Revertir loadHistory y loadDownloads a funciones síncronas
# Estas NO necesitan ser async porque no usan modales

html = html.replace('async function loadHistory(', 'function loadHistory(')
html = html.replace('async function loadDownloads(', 'function loadDownloads(')

print("✓ loadHistory revertida a función síncrona")
print("✓ loadDownloads revertida a función síncrona")

# Guardar
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\n✅ Funciones arregladas")
print("   - loadHistory: síncrona ✓")
print("   - loadDownloads: síncrona ✓")
print("   - cancelDownload: async ✓ (usa modal)")
print("   - deleteHistory: async ✓ (usa modal)")
