"""
Script para agregar el sistema de modales personalizados bonitos
"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Agregar HTML del modal después de <body>
modal_html = '''
    <!-- Custom Modal System -->
    <div id="customModal" class="fixed inset-0 z-50 hidden items-center justify-center p-4" style="background: rgba(0,0,0,0.85); backdrop-filter: blur(15px);">
        <div class="rounded-3xl p-8 max-w-md w-full relative overflow-hidden" style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)); backdrop-filter: blur(25px); border: 2px solid rgba(255, 255, 255, 0.3); box-shadow: 0 25px 70px rgba(0,0,0,0.6); animation: modalSlideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);">
            <div class="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none"></div>
            
            <div class="relative z-10">
                <div class="flex items-center gap-4 mb-6">
                    <div id="modalIcon" class="w-16 h-16 rounded-2xl flex items-center justify-center text-4xl shadow-2xl" style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(147, 51, 234, 0.3)); backdrop-filter: blur(10px);">
                        <i class="fas fa-info-circle"></i>
                    </div>
                    <h3 id="modalTitle" class="text-3xl font-black text-white drop-shadow-lg">Aviso</h3>
                </div>
                
                <div id="modalContent" class="text-white/95 mb-6 text-lg leading-relaxed font-medium"></div>
                
                <div id="modalImage" class="hidden mb-6">
                    <div class="rounded-2xl p-4 flex gap-4 items-center" style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.2);">
                        <img id="modalThumbnail" src="" class="w-32 h-24 object-cover rounded-xl shadow-xl" />
                        <h4 id="modalVideoTitle" class="text-white text-base font-bold flex-1"></h4>
                    </div>
                </div>
                
                <div class="flex gap-3 justify-end mt-8">
                    <button id="modalCancel" onclick="closeModal()" class="hidden px-8 py-4 rounded-xl font-bold transition-all text-white text-lg" style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border: 2px solid rgba(255, 255, 255, 0.3);" onmouseover="this.style.background='rgba(255, 255, 255, 0.2)'" onmouseout="this.style.background='rgba(255, 255, 255, 0.1)'">
                        Cancelar
                    </button>
                    <button id="modalConfirm" onclick="confirmModal()" class="px-8 py-4 rounded-xl font-bold transition-all text-white text-lg shadow-2xl" style="background: linear-gradient(135deg, #667eea, #764ba2); border: 2px solid rgba(255, 255, 255, 0.4);" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                        Aceptar
                    </button>
                </div>
            </div>
        </div>
    </div>

    <style>
        @keyframes modalSlideIn {
            from { opacity: 0; transform: translateY(-30px) scale(0.9); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }
    </style>

'''

# Insertar después de <body>
body_pos = html.find('<body class="min-h-screen">')
if body_pos != -1:
    insert_pos = html.find('>', body_pos) + 1
    html = html[:insert_pos] + '\n' + modal_html + html[insert_pos:]
    print("✓ Modal HTML agregado")
else:
    print("✗ No se encontró <body>")

# 2. Agregar funciones JavaScript del modal
js_functions = '''
            // ==================== CUSTOM MODAL SYSTEM ====================
            let modalResolve = null;

            function showAlert(message, title = '⚠️ Aviso', icon = 'fa-exclamation-circle', iconBg = 'linear-gradient(135deg, rgba(251, 191, 36, 0.3), rgba(245, 158, 11, 0.3))') {
                const modal = document.getElementById('customModal');
                if (!modal) return Promise.resolve();
                const modalTitle = document.getElementById('modalTitle');
                const modalContent = document.getElementById('modalContent');
                const modalIcon = document.getElementById('modalIcon');
                const modalImage = document.getElementById('modalImage');
                const modalCancel = document.getElementById('modalCancel');
                
                modalImage.classList.add('hidden');
                modalCancel.classList.add('hidden');
                
                modalTitle.textContent = title;
                modalContent.innerHTML = message;
                modalIcon.style.background = iconBg;
                modalIcon.innerHTML = `<i class="fas ${icon}"></i>`;
                
                modal.classList.remove('hidden');
                modal.classList.add('flex');
                
                return new Promise(resolve => { modalResolve = resolve; });
            }

            function showConfirm(message, title = '❓ Confirmación', options = {}) {
                const modal = document.getElementById('customModal');
                if (!modal) return Promise.resolve(false);
                const modalTitle = document.getElementById('modalTitle');
                const modalContent = document.getElementById('modalContent');
                const modalIcon = document.getElementById('modalIcon');
                const modalImage = document.getElementById('modalImage');
                const modalCancel = document.getElementById('modalCancel');
                const modalThumbnail = document.getElementById('modalThumbnail');
                const modalVideoTitle = document.getElementById('modalVideoTitle');
                
                modalCancel.classList.remove('hidden');
                
                modalTitle.textContent = title;
                modalContent.innerHTML = message;
                modalIcon.style.background = options.iconBg || 'linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(147, 51, 234, 0.3))';
                modalIcon.innerHTML = `<i class="fas ${options.icon || 'fa-question-circle'}"></i>`;
                
                if (options.thumbnail && options.videoTitle) {
                    modalImage.classList.remove('hidden');
                    modalThumbnail.src = options.thumbnail;
                    modalVideoTitle.textContent = options.videoTitle;
                } else {
                    modalImage.classList.add('hidden');
                }
                
                document.getElementById('modalConfirm').textContent = options.confirmText || 'Aceptar';
                modalCancel.textContent = options.cancelText || 'Cancelar';
                
                modal.classList.remove('hidden');
                modal.classList.add('flex');
                
                return new Promise(resolve => { modalResolve = resolve; });
            }

            function closeModal() {
                const modal = document.getElementById('customModal');
                if (!modal) return;
                modal.classList.add('hidden');
                modal.classList.remove('flex');
                if (modalResolve) {
                    modalResolve(false);
                    modalResolve = null;
                }
            }

            function confirmModal() {
                const modal = document.getElementById('customModal');
                if (!modal) return;
                modal.classList.add('hidden');
                modal.classList.remove('flex');
                if (modalResolve) {
                    modalResolve(true);
                    modalResolve = null;
                }
            }

            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') closeModal();
            });

            const modalEl = document.getElementById('customModal');
            if (modalEl) {
                modalEl.addEventListener('click', (e) => {
                    if (e.target.id === 'customModal') closeModal();
                });
            }

'''

# Insertar antes del cierre del script
script_close = html.rfind('</script>')
if script_close != -1:
    html = html[:script_close] + '\n' + js_functions + '        </script>' + html[script_close+9:]
    print("✓ Funciones JavaScript agregadas")
else:
    print("✗ No se encontró </script>")

# Guardar
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\n✅ Sistema de modales personalizados agregado exitosamente")
print("   - Modal con glassmorphism avanzado")
print("   - Animaciones suaves")
print("   - Funciones showAlert() y showConfirm()")
print("   - Soporte para miniaturas en confirmaciones")
