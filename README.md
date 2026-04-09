# Medicine Analysis

Proyecto de analisis exploratorio y preparacion de datos sobre un dataset de medicamentos. El trabajo esta organizado para separar la carga de datos, el analisis exploratorio inicial, la futura limpieza y la etapa posterior de analisis.

## Objetivo

El objetivo del proyecto es estudiar un dataset de medicamentos para:

- comprender su estructura y calidad;
- identificar problemas de datos antes de limpiar;
- preparar una base organizada para limpieza, transformacion y analisis posterior.

## Dataset

El dataset utilizado corresponde a Kaggle y se descarga desde:

- `aadyasingh55/drug-dataset`

Archivo principal esperado dentro del proyecto:

- `data/raw/Medicine_Details.csv`

El proyecto esta configurado para no versionar datasets ni archivos generados. Por eso, `data/` y `outputs/` se mantienen fuera de Git mediante el archivo `.gitignore`.

## Estructura del proyecto

```text
medicine-analysis/
|
|-- data/
|   |-- raw/
|   |   `-- Medicine_Details.csv
|   `-- processed/
|       |-- medicine_cleaned.csv
|       `-- medicine_exploded.csv
|
|-- notebooks/
|   |-- general/
|   |   `-- 01_eda_inicial.ipynb
|   |-- enfoque_01_combinaciones_componentes/
|   |   |-- 01_eda_combinaciones_componentes.ipynb
|   |   |-- 02_limpieza_transformacion_combinaciones_componentes.ipynb
|   |   `-- 03_analisis_combinaciones_componentes.ipynb
|   |-- enfoque_02_comparacion_empresas/
|   |   |-- 01_eda_comparacion_empresas.ipynb
|   |   |-- 02_limpieza_transformacion_comparacion_empresas.ipynb
|   |   `-- 03_analisis_comparacion_empresas.ipynb
|   `-- enfoque_03_efectos_secundarios_componentes/
|       |-- 01_eda_efectos_secundarios_componentes.ipynb
|       |-- 02_limpieza_transformacion_efectos_secundarios_componentes.ipynb
|       `-- 03_analisis_efectos_secundarios_componentes.ipynb
|
|-- src/
|   |-- __init__.py
|   |-- load_data.py
|   |-- cleaning.py
|   |-- transform.py
|   |-- validation.py
|   `-- analysis.py
|
|-- outputs/
|   |-- figures/
|   |-- tables/
|   `-- reports/
|
|-- docs/
|   |-- informe_tecnico.pdf
|   `-- decisiones_limpieza.md
|
|-- README.md
|-- pyproject.toml
|-- requirements.txt
`-- main.py
```

## Estado actual

Actualmente el proyecto tiene operativo el flujo de carga de datos y una organizacion de notebooks separada por enfoque:

- `src/load_data.py` descarga el dataset si hace falta y carga `Medicine_Details.csv`;
- `notebooks/general/01_eda_inicial.ipynb` contiene el EDA transversal del dataset completo;
- cada enfoque dentro de `notebooks/` tiene su propia secuencia `EDA -> limpieza/transformacion -> analisis`;
- `cleaning.py`, `transform.py`, `validation.py`, `analysis.py` y `main.py` siguen reservados para las siguientes etapas.

## Requisitos

Se recomienda trabajar con Python 3.11 o superior.

Dependencias principales del proyecto:

- `pandas`
- `kagglehub`
- `numpy`
- `matplotlib`
- `ipykernel`

## Instalacion

### 1. Crear un entorno virtual

En Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 3. Instalar el proyecto en modo editable

Este paso permite usar imports directos como `from src.load_data import load_medicine_data` incluso desde notebooks ubicados dentro de subcarpetas.

```powershell
pip install -e .
```

### 4. Seleccionar el kernel correcto en Jupyter o VS Code

Si trabajas con notebooks, asegurate de usar el interprete de `.venv` como kernel. Eso evita errores de importacion y garantiza que las dependencias instaladas en el proyecto esten disponibles dentro del notebook.

## Descarga y carga de datos

El archivo [src/load_data.py](src/load_data.py) permite:

- usar el CSV si ya existe en `data/raw/Medicine_Details.csv`;
- descargar el dataset desde Kaggle con `kagglehub` si el archivo no existe o esta vacio;
- copiar el archivo descargado dentro de `data/raw/`;
- cargar los datos como `DataFrame` de `pandas`.

### Ejecutar la carga desde terminal

```powershell
python src\load_data.py
```

### Usar la funcion desde Python

```python
from src.load_data import load_medicine_data

df = load_medicine_data(download_if_missing=True)
print(df.head())
```

### Uso desde notebooks

Despues de ejecutar `pip install -e .`, los notebooks pueden importar directamente:

```python
from src.load_data import load_medicine_data
```

### Nota sobre Kaggle

Si es la primera vez que usas `kagglehub`, puede que necesites autenticar tu acceso a Kaggle en tu entorno local. Si ya tienes el archivo `Medicine_Details.csv` dentro de `data/raw/`, puedes trabajar directamente sin volver a descargarlo.

## Flujo de trabajo sugerido

### 1. Cargar los datos

Verificar que el archivo quede disponible en `data/raw/Medicine_Details.csv`.

### 2. Ejecutar el EDA general

Abrir:

- `notebooks/general/01_eda_inicial.ipynb`

Este notebook esta pensado para:

- revisar estructura, tipos de datos y cardinalidad;
- detectar nulos, duplicados y problemas de consistencia;
- inspeccionar columnas clave como `Composition`, `Uses`, `Side_effects` y `Manufacturer`;
- dejar registradas decisiones preliminares de limpieza.

### 3. Elegir un enfoque de trabajo

El proyecto ahora separa el trabajo en tres enfoques:

- `notebooks/enfoque_01_combinaciones_componentes/`
- `notebooks/enfoque_02_comparacion_empresas/`
- `notebooks/enfoque_03_efectos_secundarios_componentes/`

Dentro de cada carpeta se sigue el orden:

- `01_eda_...`
- `02_limpieza_transformacion_...`
- `03_analisis_...`

## Archivos importantes

- `src/load_data.py`: descarga y carga del dataset principal.
- `pyproject.toml`: configuracion para instalar el proyecto en modo editable.
- `notebooks/general/01_eda_inicial.ipynb`: analisis exploratorio general.
- `notebooks/enfoque_01_combinaciones_componentes/`: flujo del enfoque de composiciones.
- `notebooks/enfoque_02_comparacion_empresas/`: flujo del enfoque por fabricante.
- `notebooks/enfoque_03_efectos_secundarios_componentes/`: flujo del enfoque de efectos secundarios.
- `data/raw/`: datos originales.
- `data/processed/`: datos procesados generados durante el proyecto.
- `outputs/`: figuras, tablas y reportes exportados.
- `docs/`: documentacion del proyecto.

## Git y versionado

El proyecto ya incluye un `.gitignore` preparado para no subir:

- datasets en `data/raw/` y `data/processed/`;
- archivos generados en `outputs/`;
- entornos virtuales, caches y checkpoints de Jupyter.

Se mantienen archivos `.gitkeep` para conservar la estructura de carpetas.
