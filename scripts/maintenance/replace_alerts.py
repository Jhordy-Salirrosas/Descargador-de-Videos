"""
Script completo para reemplazar todos los alert() y confirm() con modales personalizados
"""

import re

# Read file
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# REPLACE PATTERNS - Convert sync alerts/confirms to async showAlert/showConfirm

# 1. Simple alerts - replace with await showAlert
replacements = [
    # alert("message") -> await showAlert("message")
    (r'return alert\("([^"]+)"\);', r'showAlert("\1", "⚠️ Aviso"); return;'),
    (r'alert\("([^"]+)"\);', r'await showAlert("\1", "⚠️ Aviso");'),
    
    # alert('message') -> await showAlert('message')  
    (r"return alert\('([^']+)'\);", r'showAlert("\1", "⚠️ Aviso"); return;'),
    (r"alert\('([^']+)'\);", r'await showAlert("\1", "⚠️ Aviso");'),
    
    # Handle template literals
    (r'alert\(`([^`]+)`\);', r'await showAlert(`\1`, "⚠️ Aviso");'),
]

# Apply simple replacements
for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# 2. Special case: checkAndStartDownload confirm with date
# Find and replace the complex confirm with showConfirm
old_confirm = r'''if \(confirm\(`⚠️ AVISO: Ya descargaste este video el \${date}\.\\n\\n¿Quieres descargarlo de nuevo\? \(Esto borrará el archivo anterior si existe\)`\)\)'''
new_confirm = r'''if (await showConfirm(
                        `Ya descargaste este video el ${date}.<br><br>¿Quieres descargarlo de nuevo?<br><small class="text-white/60">(Esto borrará el archivo anterior si existe)</small>`,
                        '⚠️ Video Duplicado',
                        {
                            icon: 'fa-exclamation-triangle',
                            iconBg: 'bg-yellow-500/20 text-yellow-300',
                            confirmText: 'Sí, re-descargar',
                            cancelText: 'Cancelar'
                        }
                    ))'''

content = re.sub(old_confirm, new_confirm, content, flags=re.DOTALL)

# 3. Convert async functions that now use await
# Make sure analyzeVideo and checkAndStartDownload are async
content = re.sub(r'function analyzeVideo\(\)', 'async function analyzeVideo()', content)
content = re.sub(r'function checkAndStartDownload\(', 'async function checkAndStartDownload(', content)

# Write back
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Completado!")
print("  - Reemplazados alert() con showAlert()")
print("  - Reemplazados confirm() con showConfirm()")
print("  - Funciones convertidas a async")
