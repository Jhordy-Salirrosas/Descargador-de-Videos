"""
Aplicar diseño completo desde el backup funcional
Paso 1: Solo CSS
"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Agregar CSS adicional
css_to_add = '''
        /* Animated Background Gradient */
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

# Insertar antes de </style>
html = html.replace('    </style>', css_to_add + '\n    </style>')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✓ CSS agregado")
