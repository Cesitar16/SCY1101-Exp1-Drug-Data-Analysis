"""
Punto de entrada principal del proyecto SCY1101 - Análisis de Medicamentos.

Orquesta los pipelines de los tres enfoques del equipo:
    - Enfoque 01: Combinaciones de Componentes (activo)
    - Enfoque 02: Por implementar
    - Enfoque 03: Por implementar

Uso desde terminal:
    python main.py                    # ejecuta todos los enfoques activos
    python main.py --enfoque 1        # ejecuta solo el enfoque 1
    python main.py --enfoque 1 2      # ejecuta los enfoques 1 y 2

Ejemplo:
    cd SCY1101-Exp1-Drug-Data-Analysis
    python main.py --enfoque 1
"""

import argparse
import sys
import time
from pathlib import Path

RUTA_PROYECTO = Path(__file__).resolve().parent
if str(RUTA_PROYECTO) not in sys.path:
    sys.path.insert(0, str(RUTA_PROYECTO))



def _titulo(texto: str) -> None:
    """Imprime un título formateado en consola."""
    linea = "=" * 60
    print(f"\n{linea}")
    print(f"  {texto}")
    print(linea)


def _seccion(texto: str) -> None:
    """Imprime una sección formateada en consola."""
    print(f"\n{'─' * 60}")
    print(f"  {texto}")
    print(f"{'─' * 60}")


def _ok(texto: str) -> None:
    print(f"  {texto}")


def _error(texto: str) -> None:
    print(f"  {texto}")



def cargar_datos():
    """
    Carga el dataset raw usando el módulo compartido load_data.

    Returns:
        DataFrame con los datos crudos de Medicine_Details.csv.

    Raises:
        FileNotFoundError: Si el CSV no existe en data/raw/.
        ImportError: Si las dependencias no están instaladas.
    """
    try:
        from src.load_data import load_medicine_data
        df = load_medicine_data(download_if_missing=False)
        _ok(f"Dataset cargado: {df.shape[0]:,} filas × {df.shape[1]} columnas")
        return df
    except FileNotFoundError as exc:
        _error(f"CSV no encontrado: {exc}")
        _error("Asegúrate de que data/raw/Medicine_Details.csv existe.")
        raise
    except ImportError as exc:
        _error(f"Dependencia faltante: {exc}")
        _error("Ejecuta: pip install -r requirements.txt")
        raise



# Enfoque 01 — Combinaciones de Componentes


def ejecutar_enfoque_01(df_raw) -> bool:
    """
    Ejecuta el pipeline completo del Enfoque 01: Combinaciones de Componentes.

    Pasos:
        1. Limpieza y generación de columnas derivadas.
        2. Transformaciones avanzadas (explode, pares, co-ocurrencia).
        3. Validación de integridad del pipeline.
        4. Análisis y generación de visualizaciones.

    Args:
        df_raw: DataFrame raw cargado por cargar_datos().

    Returns:
        True si el pipeline completó sin errores, False si falló.
    """
    _seccion("ENFOQUE 01 — Combinaciones de Componentes")

    try:
        # --- Limpieza ---
        print("\n  [1/4] Ejecutando pipeline de limpieza...")
        from src.enfoque_01_combinaciones_componentes.cleaning import (
            run_cleaning_pipeline,
        )
        df_clean = run_cleaning_pipeline(df_raw, save=True)
        _ok(f"Limpieza completada: {df_clean.shape[0]:,} filas")

        # --- Transformaciones ---
        print("\n  [2/4] Ejecutando pipeline de transformaciones...")
        from src.enfoque_01_combinaciones_componentes.transform import (
            run_transform_pipeline,
        )
        df_exploded, df_pairs, cooc_matrix = run_transform_pipeline(
            df_clean, top_n=20, save=True
        )
        _ok(f"Transformaciones completadas: {df_exploded.shape[0]:,} filas expandidas")

        # --- Validación ---
        print("\n  [3/4] Ejecutando pipeline de validación...")
        from src.enfoque_01_combinaciones_componentes.validation import (
            run_validation_pipeline,
        )
        reporte = run_validation_pipeline(df_raw, df_clean)
        estado_esquema = "válido" if reporte["esquema"]["esquema_valido"] else "inválido"
        _ok(f"Validación completada: esquema {estado_esquema}")

        # --- Análisis ---
        print("\n  [4/4] Ejecutando pipeline de análisis...")
        from src.enfoque_01_combinaciones_componentes.analysis import (
            run_analysis_pipeline,
        )

        import pandas as pd
        from src.enfoque_01_combinaciones_componentes.cleaning import (
            CATEGORIAS_TAMAÑO_ORDER,
        )

        # Reconstruir Categorical después de leer el CSV procesado
        df_clean["size_category"] = pd.Categorical(
            df_clean["size_category"],
            categories=CATEGORIAS_TAMAÑO_ORDER,
            ordered=True,
        )

        run_analysis_pipeline(df_clean, df_exploded, df_pairs, cooc_matrix)
        _ok("Análisis completado: 7 gráficos generados en outputs/figures/")

        return True

    except Exception as exc:
        _error(f"Enfoque 01 falló: {exc}")
        return False


# ---------------------------------------------------------------------------
# Enfoque 02 — Por implementar (placeholder para compañero)
# ---------------------------------------------------------------------------


def ejecutar_enfoque_02(df_raw) -> bool:
    """
    Ejecuta el pipeline del Enfoque 02.

    PENDIENTE: Implementar cuando el compañero tenga listo su módulo en
    src/enfoque_02_<nombre>/.

    Para activar este enfoque:
        1. Crear src/enfoque_02_<nombre>/ con su __init__.py
        2. Implementar run_cleaning_pipeline, run_transform_pipeline,
           run_validation_pipeline y run_analysis_pipeline.
        3. Reemplazar el contenido de esta función con las llamadas
           correspondientes, siguiendo el mismo patrón del Enfoque 01.

    Args:
        df_raw: DataFrame raw cargado por cargar_datos().

    Returns:
        False mientras no esté implementado.
    """
    _seccion("ENFOQUE 02 — (Pendiente de implementación)")
    print("  ⏳ Este enfoque aún no está disponible.")
    print("  ⏳ Implementar en src/enfoque_02_<nombre>/")
    return False


# ---------------------------------------------------------------------------
# Enfoque 03 — Por implementar (placeholder para compañero)
# ---------------------------------------------------------------------------


def ejecutar_enfoque_03(df_raw) -> bool:
    """
    Ejecuta el pipeline del Enfoque 03.

    PENDIENTE: Implementar cuando el compañero tenga listo su módulo en
    src/enfoque_03_<nombre>/.

    Para activar este enfoque:
        1. Crear src/enfoque_03_<nombre>/ con su __init__.py
        2. Implementar run_cleaning_pipeline, run_transform_pipeline,
           run_validation_pipeline y run_analysis_pipeline.
        3. Reemplazar el contenido de esta función con las llamadas
           correspondientes, siguiendo el mismo patrón del Enfoque 01.

    Args:
        df_raw: DataFrame raw cargado por cargar_datos().

    Returns:
        False mientras no esté implementado.
    """
    _seccion("ENFOQUE 03 — (Pendiente de implementación)")
    print("  ⏳ Este enfoque aún no está disponible.")
    print("  ⏳ Implementar en src/enfoque_03_<nombre>/")
    return False


# ---------------------------------------------------------------------------
# Registro de enfoques disponibles
# Agregar aquí cada nuevo enfoque cuando esté listo.
# ---------------------------------------------------------------------------
ENFOQUES: dict[int, dict] = {
    1: {
        "nombre": "Combinaciones de Componentes",
        "funcion": ejecutar_enfoque_01,
        "activo": True,
    },
    2: {
        "nombre": "Enfoque 02 (pendiente)",
        "funcion": ejecutar_enfoque_02,
        "activo": False,
    },
    3: {
        "nombre": "Enfoque 03 (pendiente)",
        "funcion": ejecutar_enfoque_03,
        "activo": False,
    },
}


# ---------------------------------------------------------------------------
# CLI y orquestador principal
# ---------------------------------------------------------------------------


def parsear_argumentos() -> argparse.Namespace:
    """
    Define y parsea los argumentos de línea de comandos.

    Returns:
        Namespace con los argumentos parseados.
    """
    parser = argparse.ArgumentParser(
        description="Pipeline principal — SCY1101 Análisis de Medicamentos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py                  Ejecuta todos los enfoques activos
  python main.py --enfoque 1      Ejecuta solo el Enfoque 01
  python main.py --enfoque 1 2    Ejecuta los Enfoques 01 y 02
  python main.py --listar         Lista los enfoques disponibles
        """,
    )
    parser.add_argument(
        "--enfoque",
        nargs="+",
        type=int,
        choices=list(ENFOQUES.keys()),
        help="Número(s) de enfoque a ejecutar. Sin este argumento ejecuta todos los activos.",
    )
    parser.add_argument(
        "--listar",
        action="store_true",
        help="Lista los enfoques disponibles y su estado.",
    )
    return parser.parse_args()


def listar_enfoques() -> None:
    """Imprime en consola los enfoques registrados y su estado."""
    _titulo("ENFOQUES DISPONIBLES")
    for num, info in ENFOQUES.items():
        estado = "✅ Activo" if info["activo"] else "⏳ Pendiente"
        print(f"  Enfoque {num}: {info['nombre']} — {estado}")


def main() -> None:
    """
    Función principal del proyecto.

    Parsea argumentos, carga los datos y ejecuta los pipelines
    de los enfoques seleccionados. Al finalizar imprime un resumen
    de resultados.
    """
    args = parsear_argumentos()

    if args.listar:
        listar_enfoques()
        return

    _titulo("SCY1101 — Pipeline Principal de Análisis de Medicamentos")
    inicio = time.time()

    # Determinar qué enfoques ejecutar
    if args.enfoque:
        enfoques_a_ejecutar = args.enfoque
    else:
        # Por defecto: solo los marcados como activos
        enfoques_a_ejecutar = [n for n, info in ENFOQUES.items() if info["activo"]]

    print(f"\n  Enfoques a ejecutar: {enfoques_a_ejecutar}")

    # Carga única del dataset compartido por todos los enfoques
    _seccion("CARGA DE DATOS")
    try:
        df_raw = cargar_datos()
    except Exception:
        print("\n  Pipeline abortado: no se pudo cargar el dataset.")
        sys.exit(1)

    # Ejecutar cada enfoque y registrar resultado
    resultados: dict[int, bool] = {}
    for num in enfoques_a_ejecutar:
        if num not in ENFOQUES:
            _error(f"Enfoque {num} no existe.")
            resultados[num] = False
            continue

        t0 = time.time()
        exito = ENFOQUES[num]["funcion"](df_raw)
        duracion = round(time.time() - t0, 1)
        resultados[num] = exito

        estado = "completado" if exito else "falló"
        print(f"\n  Enfoque {num} {estado} en {duracion}s")

    # Resumen final
    _titulo("RESUMEN DE EJECUCIÓN")
    for num, exito in resultados.items():
        nombre = ENFOQUES[num]["nombre"]
        icono = "✅" if exito else "❌"
        print(f"  {icono} Enfoque {num} — {nombre}")

    duracion_total = round(time.time() - inicio, 1)
    exitosos = sum(resultados.values())
    print(f"\n  {exitosos}/{len(resultados)} enfoques completados en {duracion_total}s")

    if not all(resultados.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()