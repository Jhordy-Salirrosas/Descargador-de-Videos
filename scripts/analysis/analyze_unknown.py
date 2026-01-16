"""
Analiza entradas Unknown y sugiere organizaciones alternativas
"""

import json
from pathlib import Path
import re

BASE_DIR = Path(__file__).parent
HISTORY_FILE = BASE_DIR / "history.json"
REPORT_FILE = BASE_DIR / "temp" / "output" / "unknown_analysis.txt"

REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
if REPORT_FILE.exists():
    REPORT_FILE.unlink()

def log(msg):
    print(msg)
    with open(REPORT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

log("="*70)
log("ANALISIS DE ENTRADAS UNKNOWN")
log("="*70)

with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
    history = json.load(f)

unknowns = [e for e in history if e.get('uploader', '').lower() in ['unknown', 'na']]

log(f"\nTotal Unknown: {len(unknowns)}")

log("\n MUESTRA DE 10 ENTRADAS:")
log("-"*70)

for i, entry in enumerate(unknowns[:10], 1):
    log(f"\n{i}. {entry.get('title', 'Sin titulo')[:60]}")
    log(f"   URL: {entry.get('url', 'Sin URL')[:70]}")
    log(f"   Archivo: {Path(entry.get('file_path', '')).name if entry.get('file_path') else 'Sin archivo'}")
    log(f"   Status: {entry.get('status', 'unknown')}")

# Analizar qué campos tienen
log("\n\nCAMPOS DISPONIBLES (primera entrada):")
log("-"*70)
if unknowns:
    sample = unknowns[0]
    for key, value in sample.items():
        value_str = str(value)[:100] if value else "(vacio)"
        log(f"  {key}: {value_str}")

log(f"\n\nReporte: {REPORT_FILE}")
log("="*70)

print(f"\nREPORTE GUARDADO EN:\n{REPORT_FILE}\n")
