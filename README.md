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
|   |-- 01_eda_inicial.ipynb
|   |-- 02_limpieza_transformacion.ipynb
|   `-- 03_analisis_segmentacion.ipynb
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
|-- requirements.txt
`-- main.py
```

## Estado actual

Actualmente el proyecto tiene operativo el flujo de carga de datos y el notebook de EDA inicial:

- `src/load_data.py` descarga el dataset si hace falta y carga `Medicine_Details.csv`;
- `notebooks/01_eda_inicial.ipynb` contiene la estructura base del analisis exploratorio inicial;
- `cleaning.py`, `transform.py`, `validation.py`, `analysis.py`, `main.py` y los notebooks 02 y 03 estan reservados para las siguientes etapas.

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

### Nota sobre Kaggle

Si es la primera vez que usas `kagglehub`, puede que necesites autenticar tu acceso a Kaggle en tu entorno local. Si ya tienes el archivo `Medicine_Details.csv` dentro de `data/raw/`, puedes trabajar directamente sin volver a descargarlo.

## Flujo de trabajo sugerido

### 1. Cargar los datos

Verificar que el archivo quede disponible en `data/raw/Medicine_Details.csv`.

### 2. Ejecutar el EDA inicial

Abrir:

- `notebooks/01_eda_inicial.ipynb`

Este notebook esta pensado para:

- revisar estructura, tipos de datos y cardinalidad;
- detectar nulos, duplicados y problemas de consistencia;
- inspeccionar columnas clave como `Composition`, `Uses`, `Side_effects` y `Manufacturer`;
- dejar registradas decisiones preliminares de limpieza.

### 3. Continuar con limpieza y transformacion

Siguientes notebooks previstos:

- `notebooks/02_limpieza_transformacion.ipynb`
- `notebooks/03_analisis_segmentacion.ipynb`

## Archivos importantes

- `src/load_data.py`: descarga y carga del dataset principal.
- `notebooks/01_eda_inicial.ipynb`: analisis exploratorio inicial.
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
