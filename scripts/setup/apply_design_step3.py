"""
Paso 3: Agregar funciones JavaScript para partículas y contadores
"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Funciones JavaScript a agregar
js_functions = '''
            // ==================== PARTICLES SYSTEM ====================
            function initParticles() {
                const container = document.getElementById('particles-container');
                if (!container) return;
                const particleCount = 50;
                
                for (let i = 0; i < particleCount; i++) {
                    const particle = document.createElement('div');
                    particle.className = 'particle';
                    
                    particle.style.left = Math.random() * 100 + '%';
                    particle.style.top = Math.random() * 100 + '%';
                    
                    const tx = (Math.random() - 0.5) * 200 + 'px';
                    const ty = (Math.random() - 0.5) * 200 + 'px';
                    particle.style.setProperty('--tx', tx);
                    particle.style.setProperty('--ty', ty);
                    
                    particle.style.animationDelay = Math.random() * 20 + 's';
                    particle.style.animationDuration = (15 + Math.random() * 10) + 's';
                    
                    container.appendChild(particle);
                }
            }

            // ==================== COUNTER ANIMATION ====================
            function animateCounter(element, target, duration = 2000) {
                if (!element) return;
                const start = 0;
                const increment = target / (duration / 16);
                let current = start;
                
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        element.textContent = target;
                        clearInterval(timer);
                    } else {
                        element.textContent = Math.floor(current);
                    }
                }, 16);
            }

            // Initialize on load
            (function() {
                initParticles();
            })();

'''

# Insertar antes de las funciones del modal (antes de "// Modal functions")
insert_point = content.find('            // Modal functions')
if insert_point == -1:
    # Si no encuentra, insertar antes del cierre del script
    insert_point = content.rfind('        </script>')
    
content = content[:insert_point] + js_functions + '\n' + content[insert_point:]

print("✓ Función initParticles() agregada")
print("✓ Función animateCounter() agregada")
print("✓ Inicialización automática configurada")

# Guardar
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✓ Paso 3 completado")
print("✓ Diseño completo implementado!")
print("\nReiniciando servidor...")
