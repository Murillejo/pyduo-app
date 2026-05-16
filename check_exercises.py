# check_exercises.py
import json
from pathlib import Path
import sys

"""
Script de Validación Quirúrgica de Datos para PyDuo.
Verifica que el archivo data/exercises.json sea un JSON válido y 
que contenga las claves obligatorias para que app.py no falle en silencio.
"""

# Rutas del proyecto
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "exercises.json"

print(f"--- Iniciando validación de datos en: {DATA_FILE} ---")

if not DATA_FILE.exists():
    print(f"❌ Error Crítico: No se encuentra el archivo {DATA_FILE}")
    sys.exit(1)

try:
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        exercises = json.load(f)
    print("✅ Formato JSON: Estructura sintáctica válida (parseado correctamente).")
except json.JSONDecodeError as e:
    print(f"❌ Error Sintáctico en JSON: No se pudo parsear el archivo.\n")
    print(f"   Línea problemática: {e.lineno}")
    print(f"   Detalle del error: {e.msg}")
    print(f"   Causa probable: Comillas dobles sin escapar dentro de un string o una coma extra.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error inesperado leyendo el archivo: {e}")
    sys.exit(1)

# Validación de estructura del proyecto
if not isinstance(exercises, list) or len(exercises) == 0:
    print("❌ Error de Datos: exercises.json debe ser una LISTA que contenga al menos un objeto.")
    sys.exit(1)

# Validación de cada ejercicio (Content Gating & Context validation)
print(f"Verificando {len(exercises)} ejercicios...")
REQUIRED_KEYS = ["id", "titulo", "contexto", "solucion", "test"]

for i, ex in enumerate(exercises):
    print(f"  Validando Ejercicio {i+1}...")
    
    # 1. Verificar claves obligatorias
    missing_keys = [key for key in REQUIRED_KEYS if key not in ex]
    if missing_keys:
        print(f"    ❌ Error de Estructura: Faltan claves en el Ejercicio {i+1}: {missing_keys}")
        continue
        
    # 2. Validación quirúrgica de strings multilínea
    contexto = ex.get("contexto", "")
    codigo_inicial = ex.get("codigo_inicial", "")
    solucion = ex.get("solucion", "")
    test = ex.get("test", "")
    
    # Verificación de cadenas de texto vacías
    if not contexto.strip():
        print(f"    ⚠️ Advertencia de Datos: El 'contexto' del Ejercicio {i+1} está vacío.")
    
    # Verificación crítica: el editor no puede recibir un None o una cadena mal formada
    if codigo_inicial is None or not isinstance(codigo_inicial, str):
        print(f"    ❌ Error Crítico de Renderizado: El 'codigo_inicial' del Ejercicio {i+1} no es un string válido. El editor de app.py fallará.")
    
    # Verificación de validación automatizada
    if not solucion.strip() or not test.strip():
        print(f"    ❌ Error de Gamificación: El Ejercicio {i+1} no tiene 'solucion' o 'test' definidos.")

print("\n--- Validación de datos completada ---")
print("Si no hay errores '❌ Error de Renderizado', la estructura de datos es resiliente.")