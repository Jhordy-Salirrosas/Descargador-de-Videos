"""
Script final para arreglar el layout de 2 columnas correctamente
"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Verificar que existe el grid
if 'lg:grid-cols-3' not in html:
    print("✗ Grid no existe, algo salió mal")
    exit(1)

# 2. Encontrar donde están las tabs
tabs_pos = html.find('<!-- Downloads & History TabSection -->')
if tabs_pos == -1:
    print("✗ No se encontraron las tabs")
    exit(1)

# 3. Verificar si hay un cierre de columna izquierda antes de las tabs
# Buscar hacia atrás desde las tabs
before_tabs = html[max(0, tabs_pos-1000):tabs_pos]

# Si NO hay un cierre de div de columna izquierda, agregarlo
if '<!-- Right Column' not in before_tabs:
    print("Agregando cierre de columna izquierda y apertura de columna derecha...")
    
    # Insertar antes de las tabs
    right_column_html = '''
            </div>

            <!-- Right Column (1/3) -->
            <div>

                '''
    
    html = html[:tabs_pos] + right_column_html + html[tabs_pos:]
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✓ Columna derecha agregada correctamente")
else:
    print("✓ Columna derecha ya existe")

print("\n✅ Layout de 2 columnas completado")
print("   - Izquierda (lg:col-span-2): Input y análisis")
print("   - Derecha (1/3): Tabs de Descargas/Historial")
