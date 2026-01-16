# 🛠️ Guía de Mantenimiento - V128 Downloader

Esta guía explica cómo usar la utilidad de mantenimiento para solucionar problemas comunes con archivos descargados.

## 🎯 ¿Para Qué Sirve?

La utilidad `maintenance.py` soluciona dos problemas principales:

1. **📂 Archivos sin historial**: Videos descargados que no aparecen en la interfaz web
2. **💔 Videos corruptos**: Archivos que no se pueden reproducir

## 🚀 Uso Rápido

### Paso 1: Ejecutar la Utilidad

```bash
python maintenance.py
```

### Paso 2: Seleccionar Opción 5 (Mantenimiento Completo)

```
👉 Selecciona una opción: 5
```

Esto ejecutará automáticamente:
- ✅ Sincronización de historial
- ✅ Verificación de integridad
- ✅ Limpieza de entradas huérfanas

### Paso 3: Revisar Resultados

La utilidad mostrará:
- Cantidad de archivos sincronizados
- Videos corruptos detectados
- Entradas de historial sin archivo

### Paso 4: Eliminar Videos Corruptos (Opcional)

Si se detectaron videos corruptos:

```
👉 Selecciona una opción: 4
```

Confirma escribiendo `SI` cuando se solicite.

## 📋 Opciones Detalladas

### 1️⃣ Sincronizar Historial con Archivos

**¿Qué hace?**
- Escanea todos los videos en `temp_downloads/`
- Los compara con las entradas en `history.json`
- Identifica archivos que no están registrados

**Ejemplo de salida:**
```
📊 RESULTADOS DE SINCRONIZACIÓN:
============================================================
✅ Archivos sincronizados: 225
⚠️  Archivos sin historial: 6
❌ Entradas sin archivo: 3
```

**¿Cuándo usar?**
- Cuando notes que videos descargados no aparecen en el historial
- Si moviste archivos manualmente
- Después de recuperar archivos de backup

### 2️⃣ Verificar Integridad de Videos

**¿Qué hace?**
- Usa FFprobe para verificar cada video
- Detecta archivos corruptos o incompl etos
- Reporta videos con problemas

**Ejemplo de salida:**
```
[1/231] Verificando: Sia_Siberia_video.mp4...  ✅ OK (320.5s)
[2/231] Verificando: broken_video.mp4...  ❌ CORRUPTO: Duration is 0
[3/231] Verificando: another_video.mp4...  ✅ OK (180.2s)

============================================================
✅ Videos válidos: 225
❌ Videos corruptos: 6
```

**¿Cuándo usar?**
- Si tienes videos que no se reproducen
- Después de interrupciones de descarga
- Para verificar la calidad de tus archivos

**⚠️ Advertencia**: Este proceso puede tardar varios minutos dependiendo de la cantidad de archivos.

### 3️⃣ Limpiar Historial

**¿Qué hace?**
- Elimina entradas del historial que ya no tienen archivo
- Limpia registros de descargas fallidas o eliminadas

**Ejemplo de salida:**
```
🧹 Limpiando 3 entradas huérfanas del historial...
✅ Historial limpio. Entradas restantes: 228
```

**¿Cuándo usar?**
- Si eliminaste videos manualmente
- Para mantener el historial limpio
- Cuando hay muchas entradas "fantasma"

### 4️⃣ Eliminar Videos Corruptos

**¿Qué hace?**
- Elimina archivos detectados como corruptos
- Libera espacio en disco
- Requiere confirmación explícita

**Ejemplo de uso:**
```
⚠️  ADVERTENCIA: Se eliminarán 6 archivos corruptos
Esta acción NO se puede deshacer.

¿Continuar? (escribe 'SI' para confirmar): SI

🗑️  Eliminado: broken_video1.mp4
🗑️  Eliminado: broken_video2.mp4
...
✅ 6 archivos eliminados
```

**¿Cuándo usar?**
- Después de ejecutar la opción 2 (verificación)
- Para liberar espacio de archivos inutilizables
- Solo cuando estés seguro de eliminar

**⚠️ IMPORTANTE**: Esta acción es IRREVERSIBLE. Los archivos se eliminarán permanentemente.

### 5️⃣ Mantenimiento Completo

**¿Qué hace?**
- Ejecuta opciones 1, 2 y 3 automáticamente
- Proceso completo en un solo paso

**¿Cuándo usar?**
- **Recomendado para primera ejecución**
- Mantenimiento periódico (mensual)
- Cuando sospeches múltiples problemas

## 📊 Interpretando los Resultados

### Archivos Sincronizados ✅
```
✅ Archivos sincronizados: 225
```
Videos que están correctamente registrados en el historial. Todo OK.

### Archivos Sin Historial ⚠️
```
⚠️  Archivos sin historial: 6

   📁 Unknown/
      📄 mystery_video.mp4 (123.45 MB)
```

**¿Qué significa?**
- Estos archivos existen en `temp_downloads` pero no aparecen en la interfaz web
- Posibles causas:
  - Descarga interrumpida antes de guardar en historial
  - Archivos copiados manualmente
  - Error al guardar el historial

**¿Qué hacer?**
- Opción 1: Agregar manualmente a `history.json` (avanzado)
- Opción 2: Dejarlos así si no son importantes
- Opción 3: Eliminarlos manualmente si no los necesitas

### Entradas Sin Archivo ❌
```
❌ Entradas sin archivo: 3

   🎬 Video Title Example
      📂 C:\...\temp_downloads\Unknown\deleted_video.mp4
```

**¿Qué significa?**
- El historial tiene registro de un video que ya no existe
- Posibles causas:
  - Archivo eliminado manualmente
  - Archivo movido a otra ubicación
  - Descarga fallida

**¿Qué hacer?**
- Usar opción 3 para limpiar estas entradas automáticamente

### Videos Corruptos ❌
```
❌ Videos corruptos: 6

   📁 Sia Siberia/
      📄 broken_video.mp4
      💾 45.23 MB
      ⚠️  Duration is 0 (possibly corrupted)
```

**¿Qué significa?**
- El archivo existe pero está dañado y no se puede reproducir
- Posibles causas:
  - Descarga interrumpida
  - Error durante conversión FFmpeg
  - Archivo corruptodesde el origen

**¿Qué hacer?**
- Usar opción 4 para eliminarlos y liberar espacio
- Intentar re-descargar desde la URL original

## 🔧 Solución de Problemas

### Error: "FFprobe not found"

**Causa**: FFmpeg no está instalado o no está en PATH

**Solución**:
```bash
# Verificar instalación
ffprobe -version

# Si no está instalado (Windows con Winget):
winget install Gyan.FFmpeg
```

### La verificación es muy lenta

**Causa**: Muchos archivos grandes

**Soluciones**:
- Es normal, espera pacientemente
- Puedes interrumpir con `Ctrl+C` si es necesario
- Considera ejecutar durante la noche

### Archivos eliminados por error

**Prevención**:
- Siempre revisa la lista antes de confirmar
- La utilidad siempre pide confirmación con 'SI'
- Considera hacer backup antes

**Recuperación**:
- Usa herramientas de recuperación de archivos
- Restaura desde backup si tienes
- Re-descarga desde la fuente original

## 📅 Mantenimiento Recomendado

### Frecuencia Sugerida

- **Mensual**: Ejecutar opción 5 (Mantenimiento completo)
- **Después de problemas**: Si hay descargas interrumpidas
- **Antes de limpiar disco**: Verificar qué archivos eliminar

### Rutina Recomendada

1. Ejecutar mantenimiento completo (opción 5)
2. Revisar videos corruptos detectados
3. Eliminar corruptos si procede (opción 4)
4. Verificar espacio liberado

```bash
# Comando rápido para todo:
python maintenance.py
# Luego seleccionar: 5 → ENTER → 4 → SI → 0
```

## 💡 Tips y Trucos

### Ver Solo Estadísticas (Sin Eliminar)

Ejecuta opciones 1 y 2 para diagnosticar sin hacer cambios.

### Backup Antes de Limpiar

```bash
# Copiar historial antes de limpiar
copy history.json history_backup.json
```

### Automatizar con Script

Crea un archivo `auto_maintenance.bat`:
```batch
@echo off
cd "c:\PROGRAMAS HECHOS POR MI\MiDownloader\V128_Downloader"
python maintenance.py
pause
```

### Espacio Recuperado

Después de eliminar corruptos, verifica espacio:
```bash
# Windows PowerShell
Get-ChildItem temp_downloads -Recurse | Measure-Object -Property Length -Sum
```

## ❓ Preguntas Frecuentes

**P: ¿Puedo ejecutar esto mientras la aplicación está corriendo?**  
R: Sí, pero es mejor pausar descargas activas primero.

**P: ¿Se perderá el historial?**  
R: No. La opción 3 solo limpia entradas sin archivo. El resto se mantiene.

**P: ¿Qué pasa si interrumpo la verificación?**  
R: Nada grave. Simplemente ejecuta de nuevo cuando quieras.

**P: ¿Puedo deshacer la eliminación de corruptos?**  
R: No. Por eso siempre pide confirmación explícita ('SI').

**P: ¿Los archivos "sin historial" son malos?**  
R: No necesariamente. Solo significa que no aparecen en la interfaz web.

## 📞 Soporte

Si encuentras problemas:

1. Verifica que FFmpeg esté instalado: `ffprobe -version`
2. Revisa los logs en la consola
3. Consulta `README.md` principal del proyecto
