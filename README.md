# V128 Downloader (Enhanced)

Un descargador de videos avanzado con interfaz web, compatible con múltiples sitios de videos y gestión inteligente de cookies.

## 🚀 Características

- ✅ **Interfaz Web moderna** con Flask
- ✅ **Soporte multi-sitio**: XNXX, XGroovy, PornoXO, YouPorn, y más
- ✅ **Extractores personalizados** para sitios que requieren procesamiento especial
- ✅ **Gestión de cookies** desde navegadores (Brave, Chrome, Edge) o manual
- ✅ **Selección de calidad** de video
- ✅ **Historial de descargas** persistente
- ✅ **Detección automática de uploader/actriz** para organización de carpetas
- ✅ **Barra de progreso en tiempo real**

## 📋 Requisitos

- Python 3.8+
- FFmpeg (instalado y en PATH)
- Dependencias Python:
  - Flask
  - yt-dlp
  - requests

## 🔧 Instalación

1. **Clonar o descargar el proyecto**

2. **Instalar dependencias**:
   ```bash
   pip install flask yt-dlp requests
   ```

3. **Instalar FFmpeg**:
   - **Windows (Winget)**:
     ```bash
     winget install Gyan.FFmpeg
     ```
   - **Verificar instalación**:
     ```bash
     ffmpeg -version
     ```

## 🎯 Uso

1. **Iniciar la aplicación**:
   ```bash
   python app.py
   ```

2. **Abrir navegador**:
   - Ir a: `http://localhost:5000`

3. **Descargar videos**:
   - Pegar URL del video
   - (Opcional) Seleccionar fuente de cookies si el sitio requiere autenticación
   - Clic en "Analizar"
   - Seleccionar calidad deseada
   - Clic en "Descargar"

4. **Ver historial**:
   - Clic en el botón "Historial" en la interfaz

## 📁 Estructura del Proyecto

```
V128_Downloader/
├── app.py                  # Aplicación principal Flask
├── cookie_utils.py         # Utilidades para manejo de cookies
├── history.json            # Historial de descargas
├── .gitignore             # Archivos ignorados por Git
├── README.md              # Este archivo
│
├── Documentation/         # Documentación del proyecto
├── templates/            # Templates HTML de Flask
├── tests/               # Scripts de prueba y análisis
│   ├── xnxx/           # Pruebas específicas para XNXX
│   ├── xgroovy/        # Pruebas específicas para XGroovy
│   └── general/        # Pruebas generales
│
├── temp/               # Archivos temporales (ignorado por Git)
│   ├── cookies/       # Cookies de sesión
│   └── output/        # Outputs de debug/análisis
│
└── temp_downloads/    # Videos descargados temporalmente
```

## 🛠️ Características Técnicas

### Extractores Personalizados

El proyecto incluye extractores personalizados para sitios que no funcionan bien con yt-dlp estándar:

- **XNXX**: Extracción de calidades HLS + detección de uploader
- **XGroovy**: Parsing HTML personalizado + detección de actriz
- **PornoXO**: Extracción de fuentes de video directas

### Gestión de Cookies

Soporta múltiples métodos de obtención de cookies:
- Extracción automática desde navegadores (Brave, Chrome, Edge)
- Carga manual en formato Netscape
- Sanitización automática de formato

### Organización Inteligente

Los videos se guardan en carpetas organizadas por:
- Nombre del uploader/actriz (detectado automáticamente)
- Fallback a carpetas genéricas si no se detecta

## 🧪 Testing

El directorio `tests/` contiene scripts útiles para:
- Depurar extractores específicos
- Analizar formatos de video
- Probar detección de uploaders
- Verificar parsing de playlists HLS

## 📝 Notas Importantes

- **FFmpeg requerido**: La aplicación necesita FFmpeg para procesar algunos formatos de video
- **Cookies**: Algunos sitios requieren cookies de sesión válidas para acceder a contenido
- **Paths**: Los archivos temporales se limpian automáticamente cuando es posible

## 🐛 Troubleshooting

### Error: "FFmpeg not found"
- Verificar que FFmpeg esté instalado: `ffmpeg -version`
- Asegurarse de que esté en PATH

### Error: "Cookie extraction failed"
- Cerrar el navegador completamente
- Usar el modo "Manual" y pegar cookies manualmente

### Los videos no se descargan
- Verificar la URL
- Intentar con cookies si el sitio requiere autenticación
- Revisar los logs en la consola

## 📄 Licencia

Proyecto personal de uso educativo.

## 👤 Autor

Desarrollado para gestión personal de contenido multimedia.
