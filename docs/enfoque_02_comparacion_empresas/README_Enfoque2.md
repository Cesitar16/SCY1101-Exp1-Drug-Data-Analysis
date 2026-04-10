# Enfoque 02 - README Tecnico

## 1. Foco de analisis

**Nombre del foco:** `Comparacion por Empresa / Manufacturer`

Este enfoque estudia como cambia la percepcion de calidad de los medicamentos segun el laboratorio que los fabrica. El eje principal es comparar fabricantes por reputacion, consistencia, seguridad, especializacion terapeutica y desempeno sobre una misma composicion.

## 2. Columna principal del dataset

**Columna central:** `Manufacturer`

La columna original `Manufacturer` se normaliza y se trabaja como `manufacturer_clean`. Como columnas de apoyo se usan:

- `Composition` para comparar la misma base farmacologica entre empresas.
- `Uses` para inferir areas terapeuticas.
- `Side_effects` para resumir seguridad.
- `Excellent Review %`, `Average Review %` y `Poor Review %` para medir reputacion.

## 3. Archivos desarrollados

### Codigo fuente

- `src/enfoque_02_comparacion_empresas/cleaning.py`
- `src/enfoque_02_comparacion_empresas/transform.py`
- `src/enfoque_02_comparacion_empresas/validation.py`
- `src/enfoque_02_comparacion_empresas/analysis.py`
- `src/enfoque_02_comparacion_empresas/pipeline.py`
- `src/enfoque_02_comparacion_empresas/__init__.py`

### Notebooks

- `notebooks/enfoque_02_comparacion_empresas/01_eda_comparacion_empresas.ipynb`
- `notebooks/enfoque_02_comparacion_empresas/02_limpieza_transformacion_comparacion_empresas.ipynb`
- `notebooks/enfoque_02_comparacion_empresas/03_analisis_comparacion_empresas.ipynb`

### Documentacion de apoyo

- `docs/enfoque_02_comparacion_empresas/analisis_graficos.md`
- `docs/enfoque_02_comparacion_empresas/README.md`

### Outputs del pipeline

- `data/processed/manufacturer_comparison_clean.csv`
- `data/processed/manufacturer_side_effects_exploded.csv`
- `data/processed/manufacturer_therapeutic_areas_exploded.csv`
- `data/processed/manufacturer_composition_summary.csv`
- `outputs/tables/enfoque_02_comparacion_empresas/*.csv`
- `outputs/figures/enfoque_02_comparacion_empresas/*.png`
- `outputs/reports/enfoque_02_comparacion_empresas_pipeline_report.json`

## 4. Pipeline de limpieza

### Paso a paso

1. Se verifica que el dataset contenga las 8 columnas requeridas:
   `Medicine Name`, `Composition`, `Uses`, `Side_effects`, `Manufacturer`,
   `Excellent Review %`, `Average Review %` y `Poor Review %`.
2. Se genera un reporte de calidad del raw antes de limpiar.
3. Se eliminan duplicados exactos con `drop_duplicates()`.
4. Se normalizan espacios y strings en:
   `Medicine Name`, `Manufacturer`, `Uses`, `Side_effects` y `Composition`.
5. Se normaliza `Composition` para dejar separadores consistentes:
   `"A+B"` -> `"A + B"`, y comas con espacio uniforme.
6. Se convierten las tres columnas de reviews a numericas con `pd.to_numeric(..., errors="coerce")`.
7. Se generan columnas derivadas para analisis posterior.
8. Se exporta el CSV limpio a `data/processed/manufacturer_comparison_clean.csv`.

### Filas/columnas eliminadas

- **Filas eliminadas:** 84 duplicados exactos.
- **Columnas eliminadas:** ninguna. Se conservaron las 9 columnas del dataset raw y se agregaron columnas nuevas.

### Normalizaciones aplicadas

- Colapso de espacios repetidos y trim en extremos.
- Homogeneizacion de `Composition`.
- Normalizacion de `Manufacturer` sin forzar cambio de mayusculas/minusculas.
- Conversion de reviews a tipo numerico.

### Columnas nuevas generadas

- `manufacturer_clean`
- `composition_clean`
- `components_list`
- `composition_key`
- `side_effects_list`
- `therapeutic_areas`
- `n_components`
- `n_side_effects`
- `review_sum`
- `review_balance`

### Resultado de limpieza

- **Shape raw:** `11,825 x 9`
- **Shape limpio:** `11,741 x 19`

## 5. Transformaciones

### Tecnicas usadas

- `groupby`
- `agg`
- `merge`
- `explode`
- `pivot`
- `value_counts`
- `corr`
- ranking y ordenamiento con `sort_values`

### DataFrames transformados principales

| DataFrame | Descripcion | Shape |
|---|---|---:|
| `df_clean` | Dataset limpio con columnas derivadas | `11,741 x 19` |
| `side_effects` | Una fila por medicamento x efecto secundario | `81,231 x 19` |
| `therapeutic_areas` | Una fila por medicamento x area terapeutica | `14,236 x 19` |
| `composition_frame` | Resumen composicion x empresa | `6,746 x 8` |

### Tablas analiticas generadas

| Tabla | Shape |
|---|---:|
| `market_share` | `15 x 3` |
| `ranking` | `150 x 6` |
| `consistency` | `150 x 6` |
| `composition_comparison` | `6,746 x 8` |
| `winners` | `940 x 8` |
| `side_effect_summary` | `150 x 7` |
| `specialization` | `1,224 x 5` |
| `quality_balance` | `150 x 8` |
| `top_medicines` | `450 x 6` |

### Transformaciones clave

- `explode_side_effects(df_clean)`: abre la lista de efectos secundarios.
- `explode_therapeutic_areas(df_clean)`: abre la lista de areas terapeuticas inferidas.
- `build_manufacturer_composition_frame(df_clean)`: agrega reviews por `composition_key` y `manufacturer_clean`.
- `manufacturer_reputation_ranking(df_clean)`: resume reputacion promedio por empresa.
- `manufacturer_consistency(df_clean)`: mide dispersion interna con `std` e IQR.
- `manufacturer_specialization(df_clean)`: construye mezcla terapeutica por fabricante.

## 6. Validacion

### Checksum MD5

- **No.** En el enfoque 2 no se implemento checksum MD5.

### Validacion de esquema

- **Si.** Se valida la presencia de las 8 columnas requeridas con `ensure_required_columns()`.

### Validacion de integridad

- **Si.** Se verifica que `Excellent Review % + Average Review % + Poor Review %` sume aproximadamente 100 con tolerancia `1.0`.

### Resultado del reporte de calidad del raw

- Duplicados: `84`
- `Manufacturer` vacio: `0`
- `Composition` vacio: `0`
- Reviews inconsistentes: `0`
- Fabricantes unicos: `759`
- Nulos en columnas requeridas: `0` en todas

## 7. Graficos generados

### Graficos exportados por el pipeline

- `top_manufacturers.png`
  Muestra las empresas con mayor cantidad de medicamentos en el dataset.
- `reputation_ranking.png`
  Ordena fabricantes por `review_balance_mean` para comparar reputacion promedio.
- `review_balance_boxplot.png`
  Muestra la dispersion de `review_balance` en las empresas mas grandes.
- `quality_vs_quantity.png`
  Compara cantidad de medicamentos vs calidad promedio por empresa.
- `correlation_size_vs_good_reviews.png`
  Evalua la correlacion entre tamano del portafolio y `% Excellent` promedio.
- `specialization_heatmap.png`
  Muestra la concentracion terapeutica de las empresas mas grandes.

### Graficos exploratorios en notebooks

- Histogramas de `Excellent Review %`, `Average Review %` y `Poor Review %`.
- Barplot de top fabricantes por volumen.
- Boxplot de `review_balance` para las empresas mas grandes.
- Scatter de correlacion entre cantidad de medicamentos y buenas valoraciones.

## 8. Resultados principales

### Hallazgo 1: el dataset esta muy concentrado en pocas empresas grandes

- Hay `759` fabricantes unicos.
- La mediana es solo `2` medicamentos por empresa.
- Solo `150` fabricantes tienen `>= 10` medicamentos.
- Las 5 empresas con mayor volumen son:
  `Sun Pharmaceutical Industries Ltd (819)`,
  `Intas Pharmaceuticals Ltd (648)`,
  `Cipla Ltd (569)`,
  `Torrent Pharmaceuticals Ltd (441)` y
  `Lupin Ltd (432)`.

### Hallazgo 2: las empresas mas grandes no son necesariamente las mejor valoradas

- La correlacion entre `n_medicines` y `excellent_mean` es `r = 0.019`.
- La correlacion entre `n_medicines` y `review_balance_mean` es `r = 0.085`.
- Ambas relaciones son practicamente nulas.
- Conclusion: mayor volumen en el dataset no implica mejor reputacion promedio.

### Hallazgo 3: el top de reputacion lo lideran empresas medianas o pequenas

- `AstraZeneca`: `21` medicamentos, `57.52%` Excellent, `11.81%` Poor, `review_balance_mean = 45.71`
- `Jubilant Life Sciences`: `15` medicamentos, `review_balance_mean = 39.47`
- `Eli Lilly and Company India Pvt Ltd`: `18` medicamentos, `review_balance_mean = 34.89`
- `Merck Ltd`: `22` medicamentos, `review_balance_mean = 34.09`
- `Novartis India Ltd`: `41` medicamentos, `review_balance_mean = 33.76`

### Hallazgo 4: existe base real para comparar la misma composicion entre empresas

- Se identificaron `940` composiciones compartidas por al menos `2` fabricantes.
- De ellas, `660` aparecen en al menos `3` fabricantes.
- Esto confirma que el subestudio "misma composicion, distinta empresa" es metodologicamente valido dentro del dataset.

### Hallazgo 5: varias empresas muestran una especializacion muy marcada

- `Eli Lilly and Company India Pvt Ltd`: `100.00%` de sus medicamentos en `Diabetes / Endocrine`
- `Novo Nordisk India Pvt Ltd`: `96.77%` en `Diabetes / Endocrine`
- `Boehringer Ingelheim`: `76.92%` en `Diabetes / Endocrine`
- `Jubilant Life Sciences`: `70.59%` en `Cardiovascular`

## 9. Dificultades encontradas y resolucion

- `Side_effects` venia como texto concatenado sin delimitador explicito.
  Se resolvio con una separacion por regex basada en cambios de mayuscula.
- `Uses` venia como texto libre, no como categoria.
  Se resolvio con reglas heuristicas (`THERAPEUTIC_AREA_PATTERNS`) para inferir areas terapeuticas.
- Comparar empresas por `Medicine Name` no era robusto, porque el nombre comercial cambia entre laboratorios.
  Se resolvio creando `composition_key`, una clave canonica basada en principios activos.
- El entorno tenia incompatibilidad entre `matplotlib 3.7.1` y `numpy 2.x`.
  Se resolvio fijando `numpy < 2` en dependencias.
- En notebooks aparecio un `ImportError` despues de agregar funciones nuevas al modulo.
  La causa fue cache del kernel de Jupyter; se resolvio reiniciando el kernel o recargando el modulo.
- El `main.py` general del proyecto todavia no tenia integrado el enfoque 2.
  Se resolvio creando un pipeline propio ejecutable desde `python -m src.enfoque_02_comparacion_empresas.pipeline`.

## Referencia rapida

Para ejecutar el pipeline completo del enfoque 2:

```powershell
python -m src.enfoque_02_comparacion_empresas.pipeline
```

Para revisar el analisis interpretativo de las visualizaciones:

- `docs/enfoque_02_comparacion_empresas/analisis_graficos.md`
