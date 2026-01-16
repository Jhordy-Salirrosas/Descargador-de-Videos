"""
Paso 4: Agregar JavaScript de partículas y contadores
"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Agregar funciones antes de las funciones del modal
js_functions = '''
            // ==================== PARTICLES ====================
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

            // Init on load
            (function() {
                initParticles();
            })();

'''

# Insertar antes de "// Modal functions"
insert_pos = html.find('            // Modal functions')
if insert_pos != -1:
    html = html[:insert_pos] + js_functions + '\n' + html[insert_pos:]
else:
    # Si no hay modal functions, insertar antes del cierre del script
    insert_pos = html.rfind('</script>')
    html = html[:insert_pos] + '\n' + js_functions + '        ' + html[insert_pos:]

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✓ Funciones de partículas agregadas")
print("✓ Función animateCounter agregada")
print("✓ Inicialización automática configurada")
print("\n✅ DISEÑO COMPLETO APLICADO")
