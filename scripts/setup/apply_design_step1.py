"""
Script para aplicar el diseño completo FluxDownloader sin romper funcionalidad
Estrategia: Modificar solo HTML/CSS, NO tocar JavaScript
"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Agregar CSS adicional antes de </style>
additional_css = '''
        /* Animated Background Gradient */
        body {
            background: linear-gradient(270deg, #667eea, #764ba2, #f093fb, #4facfe);
            background-size: 800% 800%;
            animation: gradient-shift 15s ease infinite;
        }
        
        @keyframes gradient-shift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }

        /* Particles */
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
            font-family: 'JetBrains Mono', monospace;
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

        .card-3d {
            transform-style: preserve-3d;
            transition: transform 0.3s ease;
        }

        .card-3d:hover {
            transform: translateY(-4px);
        }
'''

# Insertar CSS antes de </style>
content = content.replace('    </style>', additional_css + '\n    </style>')

# 2. Cambiar body class
content = content.replace(
    '<body class="min-h-screen py-10 px-4">',
    '<body class="min-h-screen">'
)

# 3. Agregar particles container después del modal
modal_end = content.find('</div>\n\n    <div class="max-w-4xl')
if modal_end != -1:
    insert_pos = content.find('</div>', modal_end) + len('</div>')
    content = content[:insert_pos] + '\n\n    <!-- Particles -->\n    <div id="particles-container"></div>' + content[insert_pos:]

# 4. Cambiar max-w-4xl a layout responsive
content = content.replace(
    '<div class="max-w-4xl mx-auto space-y-6">',
    '<div class="min-h-screen p-4 md:p-8">'
)

print("✓ CSS adicional agregado")
print("✓ Body class actualizado")  
print("✓ Particles container agregado")
print("✓ Layout base actualizado")

# Guardar
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✓ Cambios aplicados exitosamente")
print("Siguiente: Agregar hero section y reorganizar layout")
