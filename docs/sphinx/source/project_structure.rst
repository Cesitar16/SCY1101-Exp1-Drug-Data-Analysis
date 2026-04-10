Estructura del Repositorio
==========================

Resumen
-------

El repositorio combina codigo fuente, notebooks, datos procesados, salidas del
analisis y documentacion narrativa.

Arbol principal
---------------

.. code-block:: text

   SCY1101-Exp1-Drug-Data-Analysis/
   ├── data/
   │   ├── raw/
   │   └── processed/
   ├── docs/
   │   ├── enfoque_01_combinaciones_componentes/
   │   ├── enfoque_02_comparacion_empresas/
   │   ├── enfoque_03_combinaciones_componentes/
   │   └── sphinx/
   ├── notebooks/
   │   ├── general/
   │   ├── enfoque_01_combinaciones_componentes/
   │   ├── enfoque_02_comparacion_empresas/
   │   └── enfoque_03_efectos_secundarios_componentes/
   ├── outputs/
   │   ├── figures/
   │   ├── reports/
   │   └── tables/
   ├── src/
   │   ├── enfoque_01_combinaciones_componentes/
   │   ├── enfoque_02_comparacion_empresas/
   │   ├── enfoque_03_efectos_secundarios_componentes/
   │   ├── load_data.py
   │   ├── cleaning.py
   │   ├── transform.py
   │   ├── validation.py
   │   └── analysis.py
   ├── main.py
   ├── README.md
   ├── requirements.txt
   └── pyproject.toml

Responsabilidades por carpeta
-----------------------------

``src/``
   Codigo Python reusable del proyecto.

``notebooks/``
   EDA, demostraciones y presentacion del proceso analitico.

``data/``
   Datos raw y archivos procesados generados por pipelines.

``outputs/``
   Figuras, tablas y reportes exportados.

``docs/``
   Documentacion narrativa del proyecto y sitio Sphinx.

``main.py``
   Orquestador principal del proyecto para ejecutar enfoques activos.
