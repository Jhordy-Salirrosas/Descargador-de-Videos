"""
Paso 3: Cerrar columna izquierda y abrir columna derecha con tabs
"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Buscar donde están las tabs
tabs_marker = '<!-- Downloads & History TabSection -->'
tabs_pos = html.find(tabs_marker)

if tabs_pos == -1:
    print("✗ No se encontraron las tabs")
    exit(1)

# Insertar cierre de columna izquierda y apertura de derecha ANTES de las tabs
right_column_start = '''
            </div>

            <!-- Right Column (1/3) - Downloads & History -->
            <div>

                '''

html = html[:tabs_pos] + right_column_start + html[tabs_pos:]

# Cerrar grid y container antes del script
script_pos = html.find('<script>')
close_divs = '''
            </div>
        </div>
    </div>

    '''

html = html[:script_pos] + close_divs + html[script_pos:]

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✓ Columna derecha creada")
print("✓ Tabs movidas a la derecha")
print("✓ Estructura HTML cerrada correctamente")
