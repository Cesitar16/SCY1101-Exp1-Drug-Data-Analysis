Vision General
==============

Contexto
--------

El proyecto analiza el dataset ``Medicine_Details.csv`` con foco en tres lineas
de trabajo complementarias:

- **Enfoque 1:** combinaciones de componentes activos.
- **Enfoque 2:** comparacion por empresa o fabricante.
- **Enfoque 3:** relacion entre componentes y efectos secundarios.

El objetivo no es solo generar graficos, sino construir pipelines reproducibles
de limpieza, transformacion, validacion y analisis que permitan justificar las
decisiones tecnicas del informe final.

Objetivos del proyecto
----------------------

- comprender la estructura del dataset y su calidad inicial;
- preparar una base limpia para analisis posteriores;
- separar el trabajo en enfoques independientes pero consistentes;
- exportar tablas, figuras y reportes reutilizables;
- mantener trazabilidad entre notebooks, codigo fuente y documentacion.

Dataset
-------

- **Fuente:** Kaggle, ``aadyasingh55/drug-dataset``
- **Archivo principal:** ``data/raw/Medicine_Details.csv``
- **Variables centrales:** nombre del medicamento, composicion, usos,
  efectos secundarios, fabricante y tres porcentajes de review.

Flujo de alto nivel
-------------------

1. Carga del dataset desde ``src.load_data``.
2. EDA general en notebooks.
3. Limpieza y transformaciones por enfoque.
4. Validacion de integridad y exportacion de reportes.
5. Analisis y generacion de figuras y tablas.

Documentos relacionados
-----------------------

La carpeta ``docs/`` del repositorio contiene documentos narrativos ya
elaborados que complementan este sitio:

- ``docs/analisis_integrado_enfoques.md``
- ``docs/decisiones_limpieza.md``
- documentacion especifica por enfoque dentro de ``docs/enfoque_*``
