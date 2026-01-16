"""
Paso 2: Agregar Hero Section y reorganizar a 2 columnas
"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Hero section HTML
hero_html = '''
        <!-- Hero Section -->
        <div class="glass rounded-3xl p-8 md:p-12 mb-6 card-3d relative overflow-hidden" style="animation: fadeIn 0.6s;">
            <div class="absolute inset-0 grid-pattern opacity-30"></div>
            
            <div class="relative z-10 text-center">
                <div class="mb-6">
                    <div class="inline-flex items-center gap-3 mb-4">
                        <i class="fas fa-bolt text-6xl text-yellow-300 floating"></i>
                        <h1 class="text-5xl md:text-7xl font-black text-white neon-text">
                            Flux<span class="text-blue-200">Downloader</span>
                        </h1>
                    </div>
                    <p class="text-white/80 text-lg md:text-xl font-light">
                        ⚡ Next Generation Media Manager • Lightning Fast Downloads
                    </p>
                </div>

                <!-- Stats Dashboard -->
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
                    <div class="glass rounded-2xl p-4 hover:scale-105 transition-transform">
                        <i class="fas fa-download text-3xl text-green-300 mb-2"></i>
                        <div class="stat-number text-3xl font-black" id="stat-downloads">0</div>
                        <div class="text-white/60 text-sm">Descargas</div>
                    </div>
                    <div class="glass rounded-2xl p-4 hover:scale-105 transition-transform">
                        <i class="fas fa-history text-3xl text-blue-300 mb-2"></i>
                        <div class="stat-number text-3xl font-black" id="stat-total">0</div>
                        <div class="text-white/60 text-sm">Total</div>
                    </div>
                    <div class="glass rounded-2xl p-4 hover:scale-105 transition-transform">
                        <i class="fas fa-bolt text-3xl text-yellow-300 mb-2"></i>
                        <div class="stat-number text-3xl font-black">∞</div>
                        <div class="text-white/60 text-sm">Velocidad</div>
                    </div>
                    <div class="glass rounded-2xl p-4 hover:scale-105 transition-transform">
                        <i class="fas fa-check-circle text-3xl text-purple-300 mb-2"></i>
                        <div class="stat-number text-3xl font-black">100%</div>
                        <div class="text-white/60 text-sm">Éxito</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Main Content Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            <!-- Left Column (2/3) -->
            <div class="lg:col-span-2 space-y-6">
'''

# Encontrar donde insertar el hero (después del div principal)
insert_point = content.find('<div class="min-h-screen p-4 md:p-8">') + len('<div class="min-h-screen p-4 md:p-8">')
content = content[:insert_point] + '\n' + hero_html + content[insert_point:]

# Ahora necesito encontrar donde termina la sección de input/analysis y agregar cierre + columna derecha
# Buscar el final de "Queue Area"
queue_end = content.find('<!-- Queue Area -->')
queue_div_end = content.find('</div>', queue_end + 100)  # El div que cierra queue area

# Agregar cierre de columna izquierda y apertura de columna derecha
right_column_html = '''

            </div>

            <!-- Right Column (1/3) -->
            <div class="space-y-6">
'''

content = content[:queue_div_end + 6] + right_column_html + content[queue_div_end + 6:]

print("✓ Hero section agregado")
print("✓ Layout reorganizado a 2 columnas")
print("✓ Stats dashboard incluido")

# Guardar
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✓ Paso 2 completado")
print("Siguiente: Agregar funciones JavaScript de partículas y contadores")
