"""
Paso 2: Agregar particles container y hero section
"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Agregar particles después del modal
modal_close = html.find('</div>\n\n    <div class="max-w-4xl')
if modal_close != -1:
    insert_pos = html.find('</div>', modal_close) + len('</div>')
    html = html[:insert_pos] + '\n\n    <!-- Particles -->\n    <div id="particles-container"></div>' + html[insert_pos:]

# 2. Cambiar container a responsive
html = html.replace(
    '<div class="max-w-4xl mx-auto space-y-6">',
    '<div class="min-h-screen p-4 md:p-8 relative z-10">'
)

# 3. Insertar hero section
hero = '''
        <!-- Hero Section -->
        <div class="glass rounded-3xl p-8 md:p-12 mb-6 relative overflow-hidden">
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
            <div class="lg:col-span-2">
'''

container_start = html.find('<div class="min-h-screen p-4 md:p-8 relative z-10">') + len('<div class="min-h-screen p-4 md:p-8 relative z-10">')
html = html[:container_start] + '\n' + hero + html[container_start:]

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✓ Particles y hero agregados")
print("✓ Grid de 2 columnas iniciado")
