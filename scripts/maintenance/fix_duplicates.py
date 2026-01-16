"""
Script para arreglar los dos problemas:
1. Eliminar header duplicado
2. Asegurar que tabs estén dentro de la columna derecha
"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Problema 1: Eliminar header duplicado (líneas 243-260 aprox)
# Buscar y eliminar desde "<!-- Main Card -->" hasta "</div>" después del header viejo
new_lines = []
skip = False
skip_count = 0

for i, line in enumerate(lines):
    # Detectar inicio del header viejo
    if '<!-- Main Card -->' in line and i > 200:  # El segundo, no el primero
        skip = True
        skip_count = 0
        continue
    
    # Contar divs para saber cuándo termina el header viejo
    if skip:
        if '<div' in line:
            skip_count += 1
        if '</div>' in line:
            skip_count -= 1
            if skip_count < 0:  # Terminó el bloque del header viejo
                skip = False
                # Agregar solo el cierre de div de padding
                if 'p-6 md:p-8' in lines[i-5:i+1].__str__():
                    new_lines.append(line)
                continue
        continue
    
    new_lines.append(line)

# Guardar cambios
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✓ Header duplicado eliminado")

# Problema 2: Verificar que las tabs estén dentro del grid
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Verificar estructura
if 'lg:col-span-2' in content and '<!-- Downloads & History TabSection -->' in content:
    # Buscar si hay un cierre de div antes de las tabs
    tabs_pos = content.find('<!-- Downloads & History TabSection -->')
    before_tabs = content[tabs_pos-500:tabs_pos]
    
    if '</div>\n\n            <!-- Downloads' in before_tabs:
        print("✓ Tabs ya están en columna derecha")
    else:
        print("⚠ Tabs podrían estar fuera del grid")
        # Las tabs deberían estar después de un comentario de columna derecha
        if '<!-- Right Column' not in before_tabs:
            print("✗ Falta apertura de columna derecha antes de tabs")
else:
    print("✗ Estructura de grid no encontrada")

print("\n✓ Verificación completada")
