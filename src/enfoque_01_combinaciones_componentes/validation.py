"""
Módulo de verificación de integridad y procedencia de datos.
Foco: Combinaciones de Componentes.

Responsabilidades:
    - Calcular y verificar el checksum MD5 del CSV original.
    - Validar que el esquema del DataFrame coincide con el esperado.
    - Comparar shape antes y después de la limpieza.
    - Exportar reporte de integridad a outputs/reports/.

Uso desde notebook:
    from src.enfoque_01_combinaciones_componentes.validation import run_validation_pipeline
    run_validation_pipeline(df_raw, df_clean)
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path

import pandas as pd

RUTA_PROYECTO = Path(__file__).resolve().parents[2]
RAW_CSV_PATH = RUTA_PROYECTO / "data" / "raw" / "Medicine_Details.csv"
RUTA_REPORTES = RUTA_PROYECTO / "outputs" / "reports"

ESQUEMA_ESPERADO: dict[str, str] = {
    "Medicine Name": "str",
    "Composition": "str",
    "Uses": "str",
    "Side_effects": "str",
    "Image URL": "str",
    "Manufacturer": "str",
    "Excellent Review %": "int64",
    "Average Review %": "int64",
    "Poor Review %": "int64",
}

COLUMNAS_CLEAN_ESPERADAS: list[str] = [
    "components_list",
    "n_components",
    "size_category",
    "composition_anomaly",
]


# Verificación 1: Checksum MD5

def calcular_md5(ruta: str | Path) -> str:
    """
    Calcula el hash MD5 de un archivo en disco.

    El MD5 es una huella digital del archivo: si cualquier byte cambia,
    el hash cambia. Esto permite detectar si el CSV fue modificado,
    corrompido o reemplazado entre sesiones de trabajo, garantizando
    la trazabilidad y reproducibilidad del análisis.

    Se lee en bloques de 8KB para no cargar archivos grandes en memoria.

    Args:
        ruta: Ruta al archivo a verificar.

    Returns:
        String hexadecimal con el hash MD5 del archivo.

    Raises:
        FileNotFoundError: Si el archivo no existe en la ruta indicada.
    """
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {ruta}")

    hasher = hashlib.md5()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(8192), b""):
            hasher.update(bloque)

    return hasher.hexdigest()


def verificar_checksum(
    ruta: str | Path = RAW_CSV_PATH,
    checksum_esperado: str | None = None,
) -> dict:
    """
    Calcula el MD5 del CSV raw y opcionalmente lo compara con un valor esperado.

    En la primera ejecución no hay checksum esperado, así que solo se
    registra el valor actual. En ejecuciones posteriores se puede pasar
    el checksum previo para detectar cambios en el archivo fuente.

    Args:
        ruta: Ruta al CSV raw.
        checksum_esperado: Hash MD5 previo para comparación. Si es None,
            solo se calcula y reporta el hash actual.

    Returns:
        Diccionario con el resultado de la verificación:

        .. code-block:: python

           {
               "archivo": str,
               "md5": str,
               "tamanio_bytes": int,
               "coincide": bool | None,
               "estado": str,
           }
    """
    ruta = Path(ruta)
    md5_actual = calcular_md5(ruta)
    tamanio = ruta.stat().st_size

    if checksum_esperado is None:
        coincide = None
        estado = "SIN_REFERENCIA"
    elif md5_actual == checksum_esperado:
        coincide = True
        estado = "OK"
    else:
        coincide = False
        estado = "MODIFICADO"

    resultado = {
        "archivo": str(ruta.name),
        "md5": md5_actual,
        "tamanio_bytes": tamanio,
        "coincide": coincide,
        "estado": estado,
    }

    print(f"[verificar_checksum] {ruta.name}")
    print(f"    MD5     : {md5_actual}")
    print(f"    Tamaño  : {tamanio:,} bytes")
    print(f"    Estado  : {estado}")

    return resultado


# Verificación 2: Esquema del DataFrame

def validar_esquema(df: pd.DataFrame, esperado: dict[str, str] = ESQUEMA_ESPERADO) -> dict:
    """
    Verifica que el DataFrame tenga las columnas y tipos de datos esperados.

    Compara el esquema real del DataFrame contra el esquema definido en
    ESQUEMA_ESPERADO. Detecta columnas faltantes, columnas extra inesperadas
    y tipos de datos incorrectos.

    Esta validación es crítica para garantizar que el CSV descargado desde
    Kaggle no cambió su estructura entre versiones del dataset.

    Args:
        df: DataFrame a validar.
        esperado: Diccionario {nombre_columna: tipo_esperado}.

    Returns:
        Diccionario con resultados:

        .. code-block:: python

           {
               "columnas_ok": list[str],
               "columnas_faltantes": list[str],
               "columnas_extra": list[str],
               "tipos_incorrectos": dict,
               "esquema_valido": bool,
           }
    """
    columnas_reales = set(df.columns)
    columnas_esperadas = set(esperado.keys())

    faltantes = list(columnas_esperadas - columnas_reales)
    extras = list(columnas_reales - columnas_esperadas)
    tipos_incorrectos = {}
    columnas_ok = []

    for col, tipo_esp in esperado.items():
        if col in df.columns:
            tipo_real = str(df[col].dtype)
            if tipo_real != tipo_esp:
                tipos_incorrectos[col] = {
                    "esperado": tipo_esp,
                    "real": tipo_real,
                }
            else:
                columnas_ok.append(col)

    esquema_valido = not faltantes and not tipos_incorrectos

    resultado = {
        "columnas_ok": columnas_ok,
        "columnas_faltantes": faltantes,
        "columnas_extra": extras,
        "tipos_incorrectos": tipos_incorrectos,
        "esquema_valido": esquema_valido,
    }

    estado = "VÁLIDO" if esquema_valido else "❌ INVÁLIDO"
    print(f"[validar_esquema] Estado: {estado}")
    if faltantes:
        print(f"    Columnas faltantes  : {faltantes}")
    if tipos_incorrectos:
        print(f"    Tipos incorrectos   : {tipos_incorrectos}")
    if extras:
        print(f"    Columnas extra      : {extras}")

    return resultado



# Verificación 3: Comparación de shape antes/después


def comparar_shapes(df_raw: pd.DataFrame, df_clean: pd.DataFrame) -> dict:
    """
    Compara las dimensiones del DataFrame antes y después de la limpieza.

    Cuantifica el impacto de cada decisión de limpieza: cuántas filas se
    eliminaron y cuántas columnas se añadieron. Esta trazabilidad es
    fundamental para justificar las decisiones ante el docente.

    Args:
        df_raw: DataFrame original cargado desde el CSV raw.
        df_clean: DataFrame después de ejecutar run_cleaning_pipeline.

    Returns:
        Diccionario con métricas de transformación:

        .. code-block:: python

           {
               "filas_raw": int,
               "filas_clean": int,
               "filas_eliminadas": int,
               "porcentaje_eliminado": float,
               "columnas_raw": int,
               "columnas_clean": int,
               "columnas_añadidas": int,
               "columnas_nuevas": list[str],
           }
    """
    filas_raw = len(df_raw)
    filas_clean = len(df_clean)
    filas_eliminadas = filas_raw - filas_clean
    pct_eliminado = round((filas_eliminadas / filas_raw) * 100, 2)

    cols_raw = set(df_raw.columns)
    cols_clean = set(df_clean.columns)
    cols_nuevas = sorted(cols_clean - cols_raw)

    resultado = {
        "filas_raw": filas_raw,
        "filas_clean": filas_clean,
        "filas_eliminadas": filas_eliminadas,
        "porcentaje_eliminado": pct_eliminado,
        "columnas_raw": len(df_raw.columns),
        "columnas_clean": len(df_clean.columns),
        "columnas_añadidas": len(cols_nuevas),
        "columnas_nuevas": cols_nuevas,
    }

    print(f"[comparar_shapes]")
    print(f"    Filas raw           : {filas_raw:,}")
    print(f"    Filas limpias       : {filas_clean:,}")
    print(f"    Filas eliminadas    : {filas_eliminadas} ({pct_eliminado}%)")
    print(f"    Columnas raw        : {len(df_raw.columns)}")
    print(f"    Columnas clean      : {len(df_clean.columns)}")
    print(f"    Columnas nuevas     : {cols_nuevas}")

    return resultado



# Verificación 4: Validar columnas del DataFrame limpio

def validar_columnas_clean(df_clean: pd.DataFrame) -> dict:
    """
    Verifica que el DataFrame limpio contiene las columnas derivadas esperadas.

    Comprueba que el pipeline de limpieza generó correctamente las columnas
    `components_list`, `n_components`, `size_category` y `composition_anomaly`.

    Args:
        df_clean: DataFrame limpio a validar.

    Returns:
        Diccionario con columnas presentes y faltantes.
    """
    presentes = [c for c in COLUMNAS_CLEAN_ESPERADAS if c in df_clean.columns]
    faltantes = [c for c in COLUMNAS_CLEAN_ESPERADAS if c not in df_clean.columns]

    resultado = {
        "columnas_presentes": presentes,
        "columnas_faltantes": faltantes,
        "valido": len(faltantes) == 0,
    }

    estado = "VÁLIDO" if resultado["valido"] else "FALTANTES"
    print(f"[validar_columnas_clean] Estado: {estado}")
    if faltantes:
        print(f"    Faltantes: {faltantes}")

    return resultado


# Exportar reporte

def exportar_reporte(resultados: dict, nombre: str = "reporte_integridad") -> Path:
    """
    Exporta el reporte de validación como archivo JSON en outputs/reports/.

    El formato JSON permite que el reporte sea legible por humanos y
    también procesable automáticamente en futuras auditorías del pipeline.

    Args:
        resultados: Diccionario con todos los resultados de validación.
        nombre: Nombre del archivo sin extensión.

    Returns:
        Ruta del archivo exportado.

    Raises:
        IOError: Si no se puede escribir el archivo.
    """
    try:
        RUTA_REPORTES.mkdir(parents=True, exist_ok=True)
        ruta = RUTA_REPORTES / f"{nombre}.json"
        with ruta.open("w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        print(f"[exportar_reporte] Reporte guardado en: {ruta}")
        return ruta
    except OSError as exc:
        raise IOError(f"No se pudo guardar el reporte: {exc}") from exc


# Pipeline orquestador

def run_validation_pipeline(
    df_raw: pd.DataFrame,
    df_clean: pd.DataFrame,
    ruta_csv: str | Path = RAW_CSV_PATH,
    checksum_esperado: str | None = None,
) -> dict:
    """
    Ejecuta el pipeline completo de validación de integridad.

    Pasos en orden:
        1. Calcular y verificar checksum MD5 del CSV original.
        2. Validar esquema del DataFrame raw (columnas y tipos).
        3. Comparar shapes antes y después de la limpieza.
        4. Validar que el DataFrame limpio tiene las columnas derivadas.
        5. Exportar reporte JSON a outputs/reports/.

    Args:
        df_raw: DataFrame original sin limpiar.
        df_clean: DataFrame después de run_cleaning_pipeline.
        ruta_csv: Ruta al CSV raw para calcular el checksum.
        checksum_esperado: Hash MD5 de referencia para comparar.
            Pasar None en la primera ejecución.

    Returns:
        Diccionario con todos los resultados de validación.

    Raises:
        ValueError: Si alguno de los DataFrames está vacío.
    """
    if df_raw.empty or df_clean.empty:
        raise ValueError("df_raw y df_clean no pueden estar vacíos.")

    print("=" * 55)
    print("INICIO DEL PIPELINE DE VALIDACIÓN")
    print("=" * 55)

    reporte = {
        "timestamp": datetime.now().isoformat(),
        "checksum": {},
        "esquema": {},
        "shapes": {},
        "columnas_clean": {},
    }

    print("\n[1/4] Verificando checksum MD5...")
    reporte["checksum"] = verificar_checksum(ruta_csv, checksum_esperado)

    print("\n[2/4] Validando esquema del DataFrame raw...")
    reporte["esquema"] = validar_esquema(df_raw)

    print("\n[3/4] Comparando shapes antes/después de limpieza...")
    reporte["shapes"] = comparar_shapes(df_raw, df_clean)

    print("\n[4/4] Validando columnas del DataFrame limpio...")
    reporte["columnas_clean"] = validar_columnas_clean(df_clean)

    print("\n" + "-" * 55)
    exportar_reporte(reporte)

    print("=" * 55)
    print("VALIDACIÓN COMPLETA")
    print("=" * 55)

    return reporte
