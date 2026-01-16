# Documentación del Proyecto: V128 Downloader (Enhanced)

**Ubicación:** `V128_Downloader/Documentation/PROJECT_STATUS.md`
**Última Actualización:** 14 de Enero, 2026

## 1. Estructura del Programa (Componentes)

El sistema está dividido en módulos para facilitar el mantenimiento:

| Archivo / Carpeta | Descripción |
| :--- | :--- |
| **`app.py`** | **Núcleo del Servidor**. Gestiona la interfaz web (Flask), rutas API, y coordina las descargas. Contiene la lógica principal de negocio. |
| **`cookie_utils.py`** | **Gestor de Cookies**. Se encarga de robar/copiar las cookies de navegadores (Brave, Chrome) incluso si están bloqueados, usando "Shadow Copy". |
| **`templates/index.html`** | **Interfaz de Usuario**. El frontend que ves en el navegador. |
| **`temp_downloads/`** | Carpeta temporal donde se guardan los videos antes de moverlos a su destino final. |
| **`history.json`** | Base de datos simple (JSON) que guarda el historial de tus descargas. |

---

## 2. Compatibilidad de Sitios (Estado Actual)

### ✅ Sitios Soportados y Verificados
These sites have been tested and work with the current configuration:
*   **JuiceXXX** (Soporte nativo + Fix Referer)
*   **YouPorn** (Requiere Referer específico, ya implementado)
*   **PornHub**
*   **xHamster**
*   **YouTube**
*   **XVideos**
*   **PornOxo** (Soporte mediante **Extractor Personalizado**)
*   **XNXX** (Soporte mediante **Extractor Personalizado**)
*   **eporner**

### ❌ Sitios NO Soportados / Rotos
*   (Ninguno crítico reportado actualmente)

---

## 3. Funcionalidades y Soluciones Recientes

### Soluciones Implementadas
1.  **Anti-Crash de Cookies**: 
    *   *Antes:* El programa se cerraba si Brave estaba abierto.
    *   *Ahora:* Detecta el bloqueo y continúa en "Modo Anónimo" sin fallar (o intenta usar yt-dlp nativo).
2.  **Fix Error 503**:
    *   Se corrigió el envío de cabeceras "Referer" que bloqueaba descargas en JuiceXXX.
3.  **Soporte PornOxo (Extractor Híbrido)**:
    *   Se implementó un extractor personalizado que lee el HTML directamente para evitar el error "Unsupported URL" de `yt-dlp`.
    *   Soporte para enlaces directos y extracción de miniaturas.

### Falta por Solucionar / Mejorar (TODO)
*   [x] **Soporte PornOxo**: Solucionado con extractor propio.
*   [ ] **Descarga con Navegador Abierto**: Actualmente Windows impide leer cookies en uso. Se podría investigar inyección de DLLs (muy avanzado) o extensión de navegador, pero por ahora la solución es cerrar el navegador si se requieren cookies obligatoriamente.
*   [ ] **Organización Automática**: Mejorar la detección de nombres de Actrices/Uploaders para crear carpetas más limpias.

---

## 4. Notas Técnicas
*   **Motor Base**: `yt-dlp` (Versión 2025.12.08 o superior).
*   **Lenguaje**: Python 3.14.
*   **Puerto por defecto**: 5000.
