"""
Script final para agregar funciones faltantes al HTML
"""

# Read current file
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the functions to add
functions_to_add = '''
        // ==================== DELETE HISTORY (with modal) ====================
        async function deleteHistory(downloadId) {
            const item = historyData.find(h => h.download_id === downloadId);
            if (!item) return;
            
            const confirmed = await showConfirm(
                `¿Estás seguro que deseas eliminar este video del historial?<br><small class="text-white/60">Esta acción no se puede deshacer</small>`,
                '🗑️ Eliminar del Historial',
                {
                    thumbnail: item.thumbnail,
                    videoTitle: item.title,
                    icon: 'fa-trash-alt',
                    iconBg: 'bg-red-500/20 text-red-300',
                    confirmText: 'Sí, eliminar',
                    cancelText: 'Cancelar'
                }
            );
            
            if (!confirmed) return;
            
            try {
                const res = await fetch(`/delete_history/${downloadId}`, { method: 'DELETE' });
                if (res.ok) {
                    await showAlert('Video eliminado del historial correctamente', '✓ Eliminado', 'fa-check-circle', 'bg-green-500/20 text-green-300');
                    loadHistory();
                } else {
                    await showAlert('Error al eliminar del historial', '✗ Error', 'fa-exclamation-circle', 'bg-red-500/20 text-red-300');
                }
            } catch (e) {
                await showAlert('Error: ' + e.message, '✗ Error', 'fa-exclamation-circle', 'bg-red-500/20 text-red-300');
            }
        }

        // ==================== MOVE HISTORY FILE ====================
        async function moveHistoryFile(downloadId) {
            await showAlert('Función de mover archivo en desarrollo', 'ℹ️ Información', 'fa-info-circle', 'bg-blue-500/20 text-blue-300');
        }

        // ==================== PASTE FROM CLIPBOARD ====================
        async function pasteFromClipboard() {
            try {
                const text = await navigator.clipboard.readText();
                document.getElementById('urlInput').value = text;
            } catch (e) {
                await showAlert('No se pudo acceder al portapapeles', '⚠️ Aviso', 'fa-exclamation-circle', 'bg-yellow-500/20 text-yellow-300');
            }
        }

'''

# Find where to insert (before the FORMAT BYTES comment)
insert_point = content.find('// ==================== FORMAT BYTES ====================')

if insert_point != -1:
    # Insert the functions
    content = content[:insert_point] + functions_to_add + content[insert_point:]
    
    # Write back
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Funciones agregadas exitosamente")
    print("  - deleteHistory (with modal + thumbnail)")
    print("  - moveHistoryFile")
    print("  - pasteFromClipboard")
else:
    print("✗ No se encontró el punto de inserción")
