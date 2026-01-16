"""
Script para reconstruir TODO desde cero correctamente
Voy a tomar el backup funcional y aplicar SOLO los cambios visuales necesarios
"""

# Leer el backup funcional
with open('templates/index_backup.html', 'r', encoding='utf-8') as f:
    original = f.read()

# Extraer la sección de tabs completa del backup
tabs_start = original.find('<!-- Downloads & History TabSection -->')
tabs_end = original.find('</div>\n\n    <script>', tabs_start)
tabs_html = original[tabs_start:tabs_end + 6]  # Include the closing </div>

print(f"✓ Tabs extraídas del backup ({len(tabs_html)} caracteres)")
print(f"  Desde línea con: {original[tabs_start:tabs_start+50]}")

# Leer el archivo actual
with open('templates/index.html', 'r', encoding='utf-8') as f:
    current = f.read()

# Encontrar donde insertar las tabs (después de Queue Area)
queue_end = current.find('<!-- Queue Area -->')
if queue_end == -1:
    print("✗ No se encontró Queue Area")
    exit(1)

# Buscar el cierre del div de Queue Area
queue_close = current.find('</div>', queue_end + 200)  # Saltar algunos divs
queue_close = current.find('</div>', queue_close + 10)  # El segundo cierre

# Insertar cierre de columna izquierda + columna derecha con tabs
right_column = f'''

            </div>

            <!-- Right Column (1/3) - Downloads & History -->
            <div class="space-y-6">
                
                {tabs_html}

            </div>
        </div>
    </div>
'''

# Encontrar donde está el cierre actual (antes de <script>)
script_pos = current.find('<script>')
# Eliminar todo entre queue y script
current = current[:queue_close + 6] + right_column + '\n\n    ' + current[script_pos:]

print("✓ Layout de 2 columnas completado")
print("✓ Tabs insertadas en columna derecha")

# Guardar
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(current)

print("\n✓ Archivo reconstruido exitosamente")
print("✓ Layout: Hero arriba, Input izquierda (2/3), Tabs derecha (1/3)")
