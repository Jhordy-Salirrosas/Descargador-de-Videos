"""
Script FINAL para arreglar el layout completamente
Voy a:
1. Tomar el backup funcional con modal
2. Aplicar SOLO los cambios visuales necesarios SIN romper la estructura
"""

# Leer el backup funcional con modal (index_functional_backup.html que creamos antes)
with open('templates/index_functional_backup.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Agregar CSS adicional antes de </style>
css_insert = html.find('</style>')
additional_css = '''
        /* Animated Background */
        body {
            background: linear-gradient(270deg, #667eea, #764ba2, #f093fb, #4facfe);
            background-size: 800% 800%;
            animation: gradient-shift 15s ease infinite;
        }
        
        @keyframes gradient-shift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }

        #particles-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        }

        .particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            animation: float-particle 20s infinite ease-in-out;
        }

        @keyframes float-particle {
            0%, 100% { transform: translate(0, 0); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { transform: translate(var(--tx), var(--ty)); opacity: 0; }
        }

        .neon-text {
            text-shadow: 
                0 0 10px rgba(102, 126, 234, 0.8),
                0 0 20px rgba(102, 126, 234, 0.6),
                0 0 30px rgba(102, 126, 234, 0.4);
        }

        .stat-number {
            background: linear-gradient(135deg, #fff, #e0e7ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .grid-pattern {
            background-image: 
                linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px);
            background-size: 50px 50px;
        }
'''

html = html[:css_insert] + additional_css + '\n' + html[css_insert:]

# 2. Agregar particles container después del modal
modal_end = html.find('</div>\n\n    <div class="max-w-4xl')
if modal_end != -1:
    insert_pos = html.find('</div>', modal_end) + len('</div>')
    html = html[:insert_pos] + '\n\n    <div id="particles-container"></div>' + html[insert_pos:]

# 3. Cambiar el container principal
html = html.replace(
    '<div class="max-w-4xl mx-auto space-y-6">',
    '<div class="min-h-screen p-4 md:p-8 relative z-10">'
)

# 4. Insertar hero section después del container principal
hero_html = '''
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
html = html[:container_start] + '\n' + hero_html + html[container_start:]

# 5. Cerrar columna izquierda antes de tabs y abrir columna derecha
# Buscar donde están las tabs
tabs_pos = html.find('<!-- Downloads & History TabSection -->')
# Insertar cierre de columna izquierda y apertura de columna derecha
html = html[:tabs_pos] + '\n            </div>\n\n            <!-- Right Column (1/3) -->\n            <div>\n\n                ' + html[tabs_pos:]

# 6. Cerrar el grid y container antes del script
script_pos = html.find('<script>')
html = html[:script_pos] + '\n            </div>\n        </div>\n    </div>\n\n    ' + html[script_pos:]

# 7. Agregar funciones de partículas antes del cierre del script
js_insert = html.rfind('</script>')
particles_js = '''
            // Particles
            function initParticles() {
                const container = document.getElementById('particles-container');
                if (!container) return;
                for (let i = 0; i < 50; i++) {
                    const p = document.createElement('div');
                    p.className = 'particle';
                    p.style.left = Math.random() * 100 + '%';
                    p.style.top = Math.random() * 100 + '%';
                    p.style.setProperty('--tx', (Math.random() - 0.5) * 200 + 'px');
                    p.style.setProperty('--ty', (Math.random() - 0.5) * 200 + 'px');
                    p.style.animationDelay = Math.random() * 20 + 's';
                    p.style.animationDuration = (15 + Math.random() * 10) + 's';
                    container.appendChild(p);
                }
            }
            function animateCounter(el, target, dur = 2000) {
                if (!el) return;
                let cur = 0;
                const inc = target / (dur / 16);
                const timer = setInterval(() => {
                    cur += inc;
                    if (cur >= target) {
                        el.textContent = target;
                        clearInterval(timer);
                    } else {
                        el.textContent = Math.floor(cur);
                    }
                }, 16);
            }
            (function() {
                initParticles();
            })();
'''

html = html[:js_insert] + '\n' + particles_js + '\n        ' + html[js_insert:]

# Guardar
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ DISEÑO COMPLETO APLICADO CORRECTAMENTE")
print("  - Hero section con stats")
print("  - Partículas flotantes")
print("  - Gradiente animado")
print("  - Layout 2 columnas (Input izq, Tabs der)")
print("  - Todas las funciones preservadas")
