"""
Script para reemplazar TODOS los alert() y confirm() con modales personalizados
"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

replacements = 0

# 1. Reemplazar confirm("¿Cancelar descarga?")
if 'if (confirm("¿Cancelar descarga?"))' in html:
    html = html.replace(
        'if (confirm("¿Cancelar descarga?")) {',
        'if (await showConfirm("¿Estás seguro de cancelar esta descarga?", "⚠️ Cancelar Descarga", {icon: "fa-times-circle", iconBg: "linear-gradient(135deg, rgba(239, 68, 68, 0.3), rgba(220, 38, 38, 0.3))"})) {'
    )
    replacements += 1
    print("✓ Reemplazado: confirm cancelar descarga")

# 2. Reemplazar confirm("¿Borrar del historial?")
if 'if (confirm("¿Borrar del historial?"))' in html:
    html = html.replace(
        'if (confirm("¿Borrar del historial?")) {',
        'if (await showConfirm("¿Estás seguro de eliminar este video del historial?", "🗑️ Eliminar del Historial", {icon: "fa-trash-alt", iconBg: "linear-gradient(135deg, rgba(239, 68, 68, 0.3), rgba(220, 38, 38, 0.3))"})) {'
    )
    replacements += 1
    print("✓ Reemplazado: confirm borrar historial")

# 3. Buscar y reemplazar alert() genéricos
import re

# Encontrar todos los alert()
alerts = re.findall(r'alert\("([^"]+)"\)', html)
for alert_msg in alerts:
    old = f'alert("{alert_msg}")'
    new = f'await showAlert("{alert_msg}")'
    html = html.replace(old, new)
    replacements += 1
    print(f"✓ Reemplazado: alert('{alert_msg[:50]}...')")

# 4. Hacer las funciones async donde se usan los modales
# Buscar funciones que usan confirm/alert y hacerlas async

# cancelDownload
if 'function cancelDownload(id)' in html:
    html = html.replace(
        'function cancelDownload(id) {',
        'async function cancelDownload(id) {'
    )
    print("✓ Función cancelDownload ahora es async")

# deleteHistory (si existe)
if 'function deleteHistory(' in html:
    html = html.replace(
        'function deleteHistory(',
        'async function deleteHistory('
    )
    print("✓ Función deleteHistory ahora es async")

# Guardar
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✅ Reemplazados {replacements} alert/confirm nativos")
print("   Ahora todos usan los modales personalizados bonitos")
