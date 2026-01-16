# Guía de Uso - V128 Downloader

Esta guía proporciona instrucciones detalladas sobre cómo usar V128 Downloader para descargar videos de diferentes sitios.

## 🎬 Inicio Rápido

### 1. Iniciar la Aplicación

```bash
cd "c:\PROGRAMAS HECHOS POR MI\MiDownloader\V128_Downloader"
python app.py
```

Deberías ver:
```
Iniciando V128 Downloader (Enhanced) en http://localhost:5000
* Running on http://127.0.0.1:5000
```

### 2. Abrir la Interfaz Web

Abre tu navegador y ve a: `http://localhost:5000`

## 📥 Descargar Videos

### Método Básico (Sin Cookies)

Para sitios que no requieren autenticación:

1. **Pegar URL** del video en el campo de texto
2. **Clic en "Analizar"**
3. Esperar a que se carguen las opciones de calidad
4. **Seleccionar la calidad** deseada del dropdown
5. **Clic en "Descargar"**
6. El video se descargará en `temp_downloads/[Uploader]/[Título].mp4`

### Método con Cookies (Sitios Protegidos)

Si el sitio requiere cookies (sesión/login):

#### Opción A: Extracción Automática desde Navegador

1. **Asegúrate de tener sesión activa** en el navegador (haber iniciado sesión en el sitio)
2. **Cierra el navegador completamente** (importante para evitar bloqueos)
3. En V128 Downloader:
   - Pegar URL
   - **Seleccionar navegador** (Brave, Chrome, Edge) en el dropdown de cookies
   - Clic en "Analizar"

#### Opción B: Cookies Manuales

1. **Exportar cookies** usando una extensión del navegador:
   - Chrome/Brave: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - Firefox: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

2. En el sitio del video:
   - Iniciar sesión si es necesario
   - Usar la extensión para exportar cookies en formato Netscape

3. En V128 Downloader:
   - Pegar URL
   - Seleccionar "Manual" en el dropdown de cookies
   - **Pegar el contenido de las cookies** en el área de texto que aparece
   - Clic en "Analizar"

## 🎯 Sitios Soportados

### Sitios con Extractor Personalizado

Estos sitios tienen extractores optimizados:

#### XNXX
- ✅ Extracción de todas las calidades HLS (1080p, 720p, 480p, etc.)
- ✅ Detección automática de uploader/pornstar
- ✅ No requiere cookies

**Ejemplo de URL**:
```
https://www.xnxx.com/video-xxxxx/video_title
```

#### XGroovy
- ✅ Parsing HTML personalizado
- ✅ Detección automática de actriz desde título o URL
- ✅ Puede requerir cookies dependiendo del contenido

**Ejemplo de URL**:
```
https://xgroovy.com/videos/xxxxx/video-title/
```

#### PornoXO
- ✅ Extracción directa de fuentes de video
- ✅ Múltiples calidades disponibles
- ✅ No requiere cookies

**Ejemplo de URL**:
```
https://www.pornoxo.com/videos/xxxxx/video-title/
```

### Sitios Soportados por yt-dlp

V128 Downloader también funciona con **cientos de sitios** soportados por yt-dlp:

- YouPorn
- Pornhub (con cookies)
- YouTube
- Vimeo
- Y muchos más...

Consulta la lista completa: [yt-dlp supported sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

## 📊 Entender las Calidades

### Resoluciones Comunes

- **1080p** (1920x1080): Full HD, mejor calidad
- **720p** (1280x720): HD, buena calidad, menor tamaño
- **480p** (854x480): SD, calidad media
- **360p** (640x360): Calidad baja, archivos pequeños

### Notas sobre Formatos

- **HLS (m3u8)**: Streaming adaptativo, requiere FFmpeg para convertir a MP4
- **MP4 Directo**: Descarga directa, más rápido
- **Audio Only** 🎵: Solo audio (útil para música/podcasts)

## 📂 Organización de Archivos

Los videos se guardan automáticamente en:

```
temp_downloads/
  └── [Uploader o Actriz]/
       └── [Título del Video].mp4
```

### Ejemplos:

```
temp_downloads/
  ├── Sia Siberia/
  │   └── Sia Siberia Hot Scene.mp4
  ├── Angela White/
  │   └── Angela White Solo Video.mp4
  └── Unknown/
      └── Generic Video Title.mp4
```

### Detección de Uploader

La aplicación intenta detectar el nombre del uploader/actriz desde:

1. Metadata del video (campo `uploader`, `creator`, `channel`)
2. Análisis del título del video (nombres capitalizados)
3. Análisis de la URL (slug)
4. Patrones conocidos de nombres

Si no puede detectar ninguno, usa "Unknown" como carpeta predeterminada.

## 📜 Historial de Descargas

### Ver Historial

- Clic en el botón **"Historial"** en la interfaz
- Se mostrará una lista de todos los videos descargados

### Información Mostrada

- Thumbnail del video
- Título
- Uploader/Actriz
- Estado (Completado, Error, etc.)
- Ruta del archivo descargado
- Fecha/hora de descarga

### Eliminar Entradas

- Clic en el botón **"Eliminar"** junto a cada entrada
- Nota: Esto solo elimina la entrada del historial, no el archivo descargado

## 🔧 Solución de Problemas

### "No formats found"

**Causa**: El sitio no devuelve formatos de video válidos

**Soluciones**:
1. Intentar con cookies (el sitio puede requerir login)
2. Verificar que la URL sea válida
3. Algunos sitios pueden tener protección anti-bot

### "Cookie extraction failed"

**Causa**: El navegador está abierto y bloqueando acceso a cookies

**Soluciones**:
1. **Cerrar completamente el navegador** (incluyendo procesos en segundo plano)
2. Usar el método de cookies manuales
3. Verificar que hayas iniciado sesión en el sitio

### "FFmpeg not found"

**Causa**: FFmpeg no está instalado o no está en PATH

**Soluciones**:
```bash
# Windows (con Winget)
winget install Gyan.FFmpeg

# Verificar instalación
ffmpeg -version
```

### Descarga muy lenta

**Posibles causas**:
- El servidor del sitio es lento
- Tu conexión a internet
- Formato HLS requiere procesamiento adicional

**Soluciones**:
- Seleccionar una calidad más baja
- Esperar pacientemente (algunas descargas pueden tardar)

### El video descargado está corrupto

**Soluciones**:
1. Intentar descargar nuevamente
2. Seleccionar un formato diferente
3. Verificar espacio en disco
4. Revisar logs de FFmpeg en la consola

## 💡 Tips y Trucos

### 1. Descargar Múltiples Videos

Puedes dejar múltiples descargas en cola:
- Analizar URL 1 → Descargar
- Mientras se descarga, analizar URL 2 → Descargar
- Y así sucesivamente

### 2. Cookies Permanentes

Si usas frecuentemente un sitio que requiere cookies:
1. Exporta las cookies manualmente una vez
2. Guárdalas en un archivo de texto
3. Cópialas y pégalas cada vez que las necesites

### 3. Verificar Estado de Descarga

- La barra de progreso muestra el porcentaje en tiempo real
- La velocidad de descarga se actualiza automáticamente
- "Processing..." aparece cuando FFmpeg está convirtiendo el video

### 4. Encontrar el Archivo Descargado

Si no recuerdas dónde se guardó:
1. Ir al **Historial**
2. Buscar el video
3. Ver la ruta completa del archivo

### 5. Cambiar Carpeta de Descargas

Editar en `app.py` la línea 36:
```python
TEMP_DOWNLOADS_DIR = r"C:\Tu\Carpeta\Preferida"
```

## 🧹 Mantenimiento

### Limpiar Archivos Temporales

Periódicamente, puedes limpiar:

```bash
# Eliminar cookies antiguas
del temp\cookies\temp_cookies_*.txt

# Eliminar outputs de debug
del temp\output\*.*
```

### Resetear Historial

Si quieres empezar de cero:

```bash
# Eliminar archivo de historial
del history.json
```

## ❓ Preguntas Frecuentes

**P: ¿Es legal usar este programa?**  
R: Solo para contenido del que tengas derechos o permiso. Uso educativo/personal.

**P: ¿Puedo descargar playlists completas?**  
R: Sí, yt-dlp soporta playlists para sitios como YouTube.

**P: ¿Funciona en Linux/Mac?**  
R: Sí, con Python y FFmpeg instalados.

**P: ¿Dónde se guardan las cookies?**  
R: En `temp/cookies/temp_cookies_[session_id].txt`

**P: ¿Puedo pausar/reanudar descargas?**  
R: No directamente. Puedes abortar y reintentar, yt-dlp puede reanudar en algunos casos.

## 📞 Soporte

Para problemas o dudas:
1. Revisa los logs en la consola donde ejecutaste `python app.py`
2. Verifica la documentación de yt-dlp
3. Consulta `PROJECT_STATUS.md` para estado actual del proyecto
