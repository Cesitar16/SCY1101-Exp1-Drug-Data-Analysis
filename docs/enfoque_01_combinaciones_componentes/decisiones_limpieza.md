# Decisiones de Limpieza — Foco: Combinaciones de Componentes

**Proyecto:** SCY1101 - Programación para la Ciencia de Datos  
**Dataset:** Medicine_Details.csv  
**MD5 del archivo original:** `93656e73e4e8fbf7dd8da9ecfab7ce07`  
**Tamaño del archivo:** 4.360.239 bytes  
**Fecha de procesamiento:** 2026-04-09  

---

## Contexto

El objetivo del foco es analizar las combinaciones de componentes activos
presentes en la columna `Composition` del dataset. Para ello fue necesario
diseñar un flujo de limpieza que preparara los datos sin alterar su valor
informativo original.

Todas las decisiones descritas en este documento están implementadas en
`src/enfoque_01_combinaciones_componentes/cleaning.py` y fueron validadas
mediante `src/enfoque_01_combinaciones_componentes/validation.py`.

---

## Estado inicial del dataset

| Métrica | Valor |
|---|---|
| Filas totales | 11.825 |
| Columnas totales | 9 |
| Valores nulos | 0 |
| Strings vacíos | 0 |
| Duplicados completos | 84 |

---

## Decisión 1 — Eliminación de duplicados completos

**Función:** `eliminar_duplicados()`

### Qué se hizo
Se eliminaron 84 filas donde **todas las columnas** eran idénticas,
conservando la primera ocurrencia de cada grupo duplicado mediante
`drop_duplicates(keep="first")`.

### Por qué
Un duplicado completo es un registro que no aporta información nueva:
tiene el mismo medicamento, misma composición, mismo fabricante y mismas
valoraciones. Conservarlos inflaría artificialmente las frecuencias de
ciertas combinaciones en el análisis posterior.

### Por qué NO se eliminaron duplicados parciales
Registros con el mismo nombre de medicamento pero distinta composición
o fabricante son legítimos: representan versiones, concentraciones o
fabricantes distintos del mismo principio activo. Eliminarlos habría
reducido la diversidad real del dataset.

### Impacto cuantificado
| Métrica | Antes | Después | Diferencia |
|---|---|---|---|
| Filas | 11.825 | 11.741 | -84 (-0,71%) |

---

## Decisión 2 — Normalización de espacios en `Composition`

**Función:** `normalizar_composicion()`

### Qué se hizo
Se aplicaron tres operaciones vectorizadas sobre la columna `Composition`:
1. `str.strip()` — elimina espacios al inicio y al final.
2. `str.replace(r"\s+", " ")` — colapsa múltiples espacios consecutivos a uno.
3. `str.replace(r"\s*\+\s*", " + ")` — estandariza el separador `+` con un espacio a cada lado.

### Por qué
El separador `+` es la clave del parseo posterior. Si una celda tiene
`"Amoxycillin  +Clavulanic Acid"` (doble espacio o sin espacio antes del `+`),
el split por `"+"` genera tokens con espacios sobrantes que producen
nombres de componentes inconsistentes como `"Amoxycillin "` y `" Clavulanic Acid"`.
La normalización garantiza que el parseo sea confiable.

### Por qué se usaron operaciones vectorizadas
Las operaciones `str.strip()` y `str.replace()` de pandas operan sobre
toda la Serie en C, sin iterar fila por fila. Esto es significativamente
más eficiente que un `apply()` con una función Python para esta tarea.

### Impacto cuantificado
No se eliminaron filas. La operación es de estandarización de formato,
no de filtrado. Los 11.741 registros se mantienen intactos.

---

## Decisión 3 — Extracción de componentes sin dosis

**Función:** `extraer_componentes()`

### Qué se hizo
Se creó la columna `components_list` extrayendo únicamente los nombres
de los principios activos desde `Composition`, eliminando las dosis entre
paréntesis mediante la expresión regular `r"\(.*?\)"`.

Ejemplo:
```
Entrada : "Amoxycillin (500mg) + Clavulanic Acid (125mg)"
Salida  : ['Amoxycillin', 'Clavulanic Acid']
```

### Por qué se eliminaron las dosis
Para el análisis de **qué componentes se combinan**, la dosis no es
relevante. `Amoxycillin (500mg)` y `Amoxycillin (250mg)` son el mismo
componente en combinación con otros. Conservar la dosis habría
fragmentado artificialmente los grupos, contando la misma combinación
como dos distintas.

La columna `Composition` original se conserva intacta para trazabilidad,
por lo que la información de dosis no se pierde del dataset.

### Por qué se usó `apply()` en vez de operaciones vectorizadas
La función `extraer_componentes` requiere lógica personalizada: split por
`+`, regex sobre cada token y filtrado de resultados vacíos. No existe
una alternativa vectorizada directa en pandas para esta combinación de
operaciones. El uso de `apply()` está justificado técnicamente.

### Impacto cuantificado
| Columna generada | Descripción |
|---|---|
| `components_list` | Lista de nombres de componentes sin dosis |
| Componentes únicos detectados | 1.058 |
| Registros con lista vacía (anomalías) | 0 |

---

## Decisión 4 — Generación de columnas derivadas

**Función:** `añadir_columnas_componentes()`

### Qué se hizo
A partir de `components_list` se generaron dos columnas adicionales:

- **`n_components`** (int): cantidad de componentes por medicamento,
  calculada como `len(components_list)`.

- **`size_category`** (pd.Categorical): categoría semántica del tamaño
  de la combinación, con orden lógico definido:
  `mono < duo < trio < cuádruple < complejo`.

### Por qué `pd.Categorical` con `ordered=True`
Al definir `size_category` como Categorical ordenado, pandas respeta
el orden farmacológico (no alfabético) en todas las operaciones
posteriores: `sort_values`, `groupby`, visualizaciones y comparaciones
como `df[df.size_category > "duo"]`. Sin `ordered=True`, el orden sería
alfabético (`complejo < cuádruple < duo < mono < trio`), lo que
distorsionaría la lectura de los gráficos.

### Distribución resultante
| Categoría | Medicamentos | Porcentaje |
|---|---|---|
| mono | 7.019 | 59,8% |
| duo | 3.569 | 30,4% |
| trio | 929 | 7,9% |
| cuádruple | 147 | 1,3% |
| complejo | 77 | 0,7% |
| **Total** | **11.741** | **100%** |

---

## Decisión 5 — Marcado de anomalías sin eliminación automática

**Función:** `flag_anomalies()`

### Qué se hizo
Se creó la columna booleana `composition_anomaly` marcando los registros
donde `n_components == 0`, es decir, donde no se pudo extraer ningún
componente válido desde `Composition`.

### Por qué no se eliminaron automáticamente
La eliminación automática de registros anómalos sin inspección previa
es una mala práctica: podría descartar información válida por un problema
de formato que se podría corregir con imputación. Al marcar en vez de
eliminar, se deja la decisión final documentada y explícita.

### Resultado
Se detectaron **0 anomalías** en el dataset. Todos los registros tienen
al menos un componente válido extraído.

---

## Resumen del pipeline de limpieza

| Paso | Función | Filas eliminadas | Columnas añadidas |
|---|---|---|---|
| 1. Eliminar duplicados | `eliminar_duplicados` | 84 | 0 |
| 2. Normalizar Composition | `normalizar_composicion` | 0 | 0 |
| 3. Extraer componentes | `extraer_componentes` | 0 | 1 (`components_list`) |
| 4. Columnas derivadas | `añadir_columnas_componentes` | 0 | 2 (`n_components`, `size_category`) |
| 5. Marcar anomalías | `flag_anomalies` | 0 | 1 (`composition_anomaly`) |
| **Total** | | **84 (-0,71%)** | **4** |

---

## Validación de integridad

La validación completa se ejecutó mediante `run_validation_pipeline()`
y el reporte fue exportado a `outputs/reports/reporte_integridad.json`.

| Verificación | Estado |
|---|---|
| Checksum MD5 del CSV original | `93656e73e4e8fbf7dd8da9ecfab7ce07` |
| Esquema del DataFrame raw | ✅ Válido — 9 columnas con tipos correctos |
| Shapes antes/después | ✅ 84 filas eliminadas (0,71%) |
| Columnas derivadas en df_clean | ✅ Las 4 columnas presentes |

---

## Columnas del dataset final

| Columna | Origen | Tipo | Descripción |
|---|---|---|---|
| Medicine Name | Raw | str | Nombre comercial del medicamento |
| Composition | Raw (normalizado) | str | Composición original con dosis |
| Uses | Raw | str | Usos terapéuticos |
| Side_effects | Raw | str | Efectos secundarios |
| Image URL | Raw | str | URL de imagen referencial |
| Manufacturer | Raw | str | Fabricante |
| Excellent Review % | Raw | int64 | % de valoraciones excelentes |
| Average Review % | Raw | int64 | % de valoraciones promedio |
| Poor Review % | Raw | int64 | % de valoraciones malas |
| components_list | Derivada | list[str] | Componentes sin dosis |
| n_components | Derivada | int | Cantidad de componentes |
| size_category | Derivada | Categorical | Categoría ordinal del tamaño |
| composition_anomaly | Derivada | bool | Marca de anomalía en Composition |