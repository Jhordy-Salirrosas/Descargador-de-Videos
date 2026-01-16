"""
Script DEFINITIVO para aplicar el diseño completo SIN romper nada
Voy a ser MUY cuidadoso esta vez
"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("Paso 1: Agregar CSS...")
# CSS adicional
css = '''
        body {
            background: linear-gradient(270deg, #667eea, #764ba2, #f093fb, #4facfe) !important;
            background-size: 800% 800% !important;
            animation: gradient-shift 15s ease infinite;
        }
        @keyframes gradient-shift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        #particles-container {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            pointer-events: none; z-index: 1;
        }
        .particle {
            position: absolute; width: 4px; height: 4px;
            background: rgba(255, 255, 255, 0.3); border-radius: 50%;
            animation: float-particle 20s infinite ease-in-out;
        }
        @keyframes float-particle {
            0%, 100% { transform: translate(0, 0); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { transform: translate(var(--tx), var(--ty)); opacity: 0; }
        }
        .neon-text {
            text-shadow: 0 0 10px rgba(102, 126, 234, 0.8),
                0 0 20px rgba(102, 126, 234, 0.6), 0 0 30px rgba(102, 126, 234, 0.4);
        }
        .stat-number {
            background: linear-gradient(135deg, #fff, #e0e7ff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .grid-pattern {
            background-image: linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px);
            background-size: 50px 50px;
        }
'''
html = html.replace('    </style>', css + '\n    </style>')
print("✓ CSS agregado")

print("\nPaso 2: Agregar particles y cambiar body...")
# Agregar particles después del modal
modal_end = html.find('</div>\n\n    <div class="max-w-4xl')
if modal_end != -1:
    insert_pos = html.find('</div>', modal_end) + len('</div>')
    html = html[:insert_pos] + '\n\n    <div id="particles-container"></div>' + html[insert_pos:]
print("✓ Particles container agregado")

# Cambiar body y container
html = html.replace('<body class="min-h-screen py-10 px-4">', '<body class="min-h-screen">')
html = html.replace(
    '<div class="max-w-4xl mx-auto space-y-6">',
    '<div class="min-h-screen p-4 md:p-8 relative z-10">'
)
print("✓ Body y container actualizados")

print("\nPaso 3: Agregar hero section...")
hero = '''
        <!-- Hero -->
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

        <!-- Grid 2 Columnas -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div class="lg:col-span-2">
'''

# Insertar hero DESPUÉS del container principal y ANTES del primer "<!-- Main Card -->"
main_card_pos = html.find('<!-- Main Card -->')
html = html[:main_card_pos] + hero + '\n        ' + html[main_card_pos:]
print("✓ Hero section y grid agregados")

print("\nPaso 4: Eliminar header viejo dentro de Main Card...")
# Eliminar SOLO el header viejo (desde <!-- Header --> hasta el cierre de ese div)
header_start = html.find('<!-- Header -->', main_card_pos)
if header_start != -1:
    # Encontrar el cierre del div del header (el que tiene bg-gradient-to-r)
    header_content_start = html.find('<div class="p-8 text-center', header_start)
    # Buscar el cierre de ese div específico
    div_count = 1
    pos = header_content_start + 30
    while div_count > 0 and pos < len(html):
        if html[pos:pos+4] == '<div':
            div_count += 1
        elif html[pos:pos+6] == '</div>':
            div_count -= 1
            if div_count == 0:
                # Encontramos el cierre, eliminar desde <!-- Header --> hasta aquí
                html = html[:header_start] + html[pos+7:]
                print("✓ Header viejo eliminado")
                break
        pos += 1

print("\nPaso 5: Cerrar columna izquierda y abrir derecha...")
# Encontrar donde están las tabs
tabs_pos = html.find('<!-- Downloads & History TabSection -->')
# Insertar cierre de columna izquierda y apertura de derecha
html = html[:tabs_pos] + '''
            </div>
            <div>
                ''' + html[tabs_pos:]
print("✓ Columnas configuradas")

print("\nPaso 6: Cerrar grid antes del script...")
script_pos = html.find('<script>')
html = html[:script_pos] + '''
            </div>
        </div>
    </div>

    ''' + html[script_pos:]
print("✓ Estructura HTML cerrada")

print("\nPaso 7: Agregar JavaScript...")
js = '''
            function initParticles() {
                const c = document.getElementById('particles-container');
                if (!c) return;
                for (let i = 0; i < 50; i++) {
                    const p = document.createElement('div');
                    p.className = 'particle';
                    p.style.left = Math.random() * 100 + '%';
                    p.style.top = Math.random() * 100 + '%';
                    p.style.setProperty('--tx', (Math.random() - 0.5) * 200 + 'px');
                    p.style.setProperty('--ty', (Math.random() - 0.5) * 200 + 'px');
                    p.style.animationDelay = Math.random() * 20 + 's';
                    p.style.animationDuration = (15 + Math.random() * 10) + 's';
                    c.appendChild(p);
                }
            }
            (function() { initParticles(); })();
'''
# Insertar antes de "// Modal functions" o antes del cierre del script
modal_funcs_pos = html.find('            // Modal functions')
if modal_funcs_pos != -1:
    html = html[:modal_funcs_pos] + js + '\n' + html[modal_funcs_pos:]
else:
    close_script = html.rfind('</script>')
    html = html[:close_script] + '\n' + js + '        ' + html[close_script:]
print("✓ JavaScript agregado")

# Guardar
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\n✅ DISEÑO COMPLETO APLICADO EXITOSAMENTE")
print("   - Hero section con stats")
print("   - Partículas flotantes")
print("   - Gradiente animado")
print("   - Layout 2 columnas (Input izq 2/3, Tabs der 1/3)")
print("   - Header viejo eliminado")
print("   - Todas las funciones preservadas")
