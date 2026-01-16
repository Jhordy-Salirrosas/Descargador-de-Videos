"""
Script para arreglar DEFINITIVAMENTE los errores de async/await
"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Volver a hacer async las funciones que usan await internamente
# Si usan 'await fetch', TIENEN que ser async

html = html.replace('function loadHistory(', 'async function loadHistory(')
html = html.replace('function loadDownloads(', 'async function loadDownloads(')
html = html.replace('function pollProgress(', 'async function pollProgress(')

print("✓ loadHistory ahora es async (necesario por await fetch)")
print("✓ loadDownloads ahora es async (necesario por await fetch)")
print("✓ pollProgress ahora es async (necesario por await fetch)")

# 2. Verificar llamada a copyLink que tenía un await suelto en el reporte anterior
# Line 1243: await showAlert("Link copiado!");
# Esta línea debe estar dentro de una función async. Vamos a buscar la función copyLink

if 'function copyLink(' in html:
    html = html.replace('function copyLink(', 'async function copyLink(')
    print("✓ copyLink ahora es async (necesario por await showAlert)")

# 3. Verificar playlist functions
if 'function downloadSelectedPlaylist(' in html:
    html = html.replace('function downloadSelectedPlaylist(', 'async function downloadSelectedPlaylist(')
    print("✓ downloadSelectedPlaylist ahora es async")

# Guardar
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\n✅ Funciones corregidas.")
print("   El error era que quité 'async' de funciones que usaban 'await' internamente.")
print("   Esto causaba un SyntaxError que detenía todo el script.")
