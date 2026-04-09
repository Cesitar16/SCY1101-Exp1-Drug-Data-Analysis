# Organizacion de notebooks

La carpeta `notebooks/` se organiza en una linea general y tres enfoques de trabajo.

## Estructura

- `general/`: contiene el EDA inicial transversal del dataset completo.
- `enfoque_01_combinaciones_componentes/`: flujo completo para el enfoque de combinaciones de componentes.
- `enfoque_02_comparacion_empresas/`: flujo completo para el enfoque de comparacion entre empresas o fabricantes.
- `enfoque_03_efectos_secundarios_componentes/`: flujo completo para el enfoque de efectos secundarios por componente.

## Convencion

Cada enfoque tiene tres notebooks:

- `01_eda_...`: exploracion especifica del enfoque.
- `02_limpieza_transformacion_...`: preparacion, normalizacion y transformaciones necesarias.
- `03_analisis_...`: analisis final del enfoque.

## Orden sugerido

1. Ejecutar `general/01_eda_inicial.ipynb`.
2. Elegir un enfoque.
3. Avanzar dentro del enfoque en el orden `01 -> 02 -> 03`.
