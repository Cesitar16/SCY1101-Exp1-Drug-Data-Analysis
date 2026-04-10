# Ficha Técnica — Enfoque 3
## Para el informe técnico grupal

---

## 1. FOCO

**Efectos Secundarios por Componentes Activos**

Análisis de la relación entre los principios activos de un medicamento y sus efectos secundarios: qué efectos son más frecuentes, qué componentes concentran mayor diversidad de efectos y si el número de componentes se relaciona con la cantidad de efectos secundarios o con la valoración del usuario.

---

## 2. COLUMNA PRINCIPAL

Dos columnas trabajadas en simultáneo:

| Columna | Rol |
|---|---|
| `Side_effects` | **Principal** — efectos secundarios (texto sin separador explícito) |
| `Composition` | **Secundaria** — componentes activos (con dosis, se parsea para extraer nombres) |

Columnas de revisión usadas para cruzar resultados: `Excellent Review %`, `Poor Review %`, `Average Review %`.

---

## 3. ARCHIVOS DESARROLLADOS

**Código fuente:**
- `src/enfoque_03_efectos_secundarios_componentes/cleaning.py`
- `src/enfoque_03_efectos_secundarios_componentes/transform.py`
- `src/enfoque_03_efectos_secundarios_componentes/analysis.py`
- `src/enfoque_03_efectos_secundarios_componentes/validation.py`

**Notebooks:**
- `notebooks/enfoque_03_efectos_secundarios_componentes/01_eda_efectos_secundarios_componentes.ipynb`
- `notebooks/enfoque_03_efectos_secundarios_componentes/02_limpieza_transformacion_efectos_secundarios_componentes.ipynb`
- `notebooks/enfoque_03_efectos_secundarios_componentes/03_analisis_efectos_secundarios_componentes.ipynb`

**Documentos:**
- `docs/enfoque_03_combinaciones_componentes/decisiones_limpieza.md`
- `docs/enfoque_03_combinaciones_componentes/README.md`

---

## 4. PIPELINE DE LIMPIEZA

**Función orquestadora:** `run_cleaning_pipeline(df)` en `cleaning.py`

### Paso 1 — Eliminación de duplicados completos
- **Qué:** `df.drop_duplicates(keep="first")`
- **Por qué:** 84 filas donde todas las columnas eran idénticas inflaban artificialmente las co-ocurrencias componente–efecto
- **Resultado:** 11.825 → **11.741 filas** (−84, −0,71%)

### Paso 2 — Extracción de componentes activos
- **Qué:** regex `r"\(.*?\)"` sobre `Composition` para eliminar dosis; split por `+`; normalización a minúsculas
- **Por qué:** La dosis no es relevante para agrupar por componente. `Amoxycillin (500mg)` y `Amoxycillin (250mg)` son el mismo componente. Se normaliza a minúsculas para evitar duplicados artificiales por capitalización inconsistente
- **Columna generada:** `componentes` (list[str])
- **Componentes únicos detectados:** 875 (con mínimo 5 observaciones)

### Paso 3 — Parseo de efectos secundarios (desafío técnico principal)
- **Qué:** `re.findall(r"[A-Z][^A-Z]*", texto)` sobre `Side_effects`; normalización a minúsculas
- **Por qué:** La columna `Side_effects` NO tiene separador explícito. Los efectos están concatenados usando la **mayúscula inicial como delimitador implícito**:
  ```
  "Nausea Abdominal pain Diarrhea"        → ['nausea', 'abdominal pain', 'diarrhea']
  "Rectal bleeding Taste change Headache" → ['rectal bleeding', 'taste change', 'headache']
  ```
  El regex captura correctamente efectos multipalabra sin fragmentarlos
- **Limitación conocida y mitigada:** Si un efecto tuviera todas las palabras en minúsculas no sería detectado. El EDA confirmó que **todos los efectos observados comienzan con mayúscula**
- **Columna generada:** `efectos_secundarios` (list[str])
- **Efectos únicos detectados:** 761 (con mínimo 5 observaciones)

### Paso 4 — Columnas derivadas y de conteo
- `manufacturer` (str): fabricante normalizado a minúsculas
- `n_componentes` (int): cantidad de componentes activos por medicamento
- `n_efectos` (int): cantidad de efectos secundarios por medicamento
- `anomalia_componentes` (bool): True si n_componentes == 0
- `anomalia_efectos` (bool): True si n_efectos == 0

### Resultado final de la limpieza
| Métrica | Valor |
|---|---|
| Filas finales | 11.741 |
| Columnas añadidas | 7 |
| Anomalías en componentes | **0** |
| Anomalías en efectos | **0** |
| Distribución de efectos (media) | **6,92 efectos/medicamento** |
| Distribución de efectos (mediana) | **6,00** |

---

## 5. TRANSFORMACIONES

**Función orquestadora:** `run_transform_pipeline(df_clean)` → `(df_long, crosstab, crosstab_norm)`

### T1 — `explotar_efectos()` / `explotar_componentes()`
- Explode individual de cada columna de listas para análisis de frecuencias por separado

### T2 — `explotar_todo()` — Producto cartesiano componente × efecto ⭐
- **Qué:** Doble explode: primero por `componentes`, luego por `efectos_secundarios`
- **Por qué:** Para cada medicamento con N componentes y M efectos, genera N×M filas — una por cada combinación (componente, efecto). Es el DataFrame base de todo el análisis de asociación
- **Ejemplo:** Medicamento con [A, B] y [náusea, mareo] → 4 filas: (A, náusea), (A, mareo), (B, náusea), (B, mareo)
- **Salida:** `df_long` — una fila por (medicamento, componente, efecto)

### T3 — `construir_crosstab()` — Tabla de contingencia
- **Qué:** `pd.crosstab(df_long["componentes"], df_long["efectos_secundarios"])`
- **Filtrado:** Solo componentes con ≥ 5 observaciones para evitar distorsión por rareza
- **Salida:** `crosstab` — matriz componente × efecto con frecuencias absolutas

### T4 — `normalizar_crosstab()` — Normalización por fila ⭐
- **Qué:** Divide cada fila por su suma → proporciones en rango [0, 1]
- **Por qué:** Sin normalizar, Metformin (664 apariciones) siempre tendría frecuencias absolutas mayores que un componente con 10 apariciones, creando un sesgo visual. La normalización por fila permite **comparar componentes con equidad**, independientemente de su frecuencia total
- **Salida:** `crosstab_norm` — misma forma que `crosstab`, valores en [0, 1]

### T5 — `construir_matriz_efectos()` — Matriz binaria con MultiLabelBinarizer
- **Qué:** `MultiLabelBinarizer` de scikit-learn sobre los top-30 efectos más frecuentes
- **Salida:** Matriz binaria medicamento × efecto (1 si el medicamento tiene el efecto, 0 si no)
- **Uso:** Base para clustering y reducción dimensional

### DataFrames exportados a `data/processed/`
| Archivo | Descripción |
|---|---|
| `e03_medicine_long.csv` | Producto cartesiano componente × efecto |
| `e03_crosstab_componente_efecto.csv` | Tabla de contingencia (frecuencias brutas) |
| `e03_crosstab_componente_efecto_norm.csv` | Tabla normalizada por fila |

---

## 6. VALIDACIÓN

**Función:** `run_validation_pipeline(df_raw, df_clean)` — exporta `outputs/reports/reporte_integridad_e03.json`

| Verificación | Resultado |
|---|---|
| Checksum MD5 del CSV raw | `93656e73e4e8fbf7dd8da9ecfab7ce07` ✅ |
| Esquema del DataFrame raw | ⚠️ Mínima discrepancia `str` vs `object` (pandas ≥2.0, **no funcional**) |
| Shapes antes/después de limpieza | 84 filas eliminadas (0,71%) ✅ |
| Columnas derivadas en df_clean | Las 7 columnas presentes ✅ |

> **Nota sobre la discrepancia de esquema:** pandas ≥ 2.0 reporta `str` (en lugar de `object`) para columnas de texto puro. La validación esperaba `object` (tipo legacy). Esto no afecta el pipeline ni los resultados.

---

## 7. GRÁFICOS GENERADOS

**Función:** `run_analysis_pipeline(df_clean, df_long, crosstab, crosstab_norm)` — 6 gráficos en `outputs/figures/`

| # | Archivo | Descripción |
|---|---|---|
| 1 | `e03_top_efectos_globales.png` | Barplot horizontal con los 15 efectos secundarios más frecuentes en todo el dataset. Responde: ¿qué efectos son transversales a todos los medicamentos? |
| 2 | `e03_componentes_por_diversidad_efectos.png` | Barplot con los 20 componentes que presentan mayor número de efectos secundarios **distintos**. Responde: ¿qué componentes tienen el catálogo más amplio de efectos? |
| 3 | `e03_heatmap_componente_efecto_norm.png` | Heatmap de la tabla normalizada (top 20 componentes × top 20 efectos). Cada celda = proporción de registros del componente i que tienen el efecto j. Permite comparar afinidades entre componentes con equidad |
| 4 | `e03_boxplot_efectos_por_n_componentes.png` | Boxplot de n_efectos agrupado por n_componentes (1 a 6). Responde: ¿los medicamentos con más componentes tienen más efectos secundarios? |
| 5 | `e03_top_efectos_por_componente_detalle.png` | Scatterplot comparativo de los top efectos para los 5 componentes más representados del dataset (detalle individual por componente) |
| 6 | `e03_histograma_n_efectos.png` | Histograma de distribución de medicamentos según su número de efectos secundarios. Responde: ¿cuántos efectos tiene típicamente un medicamento? |

**Tablas exportadas a `outputs/tables/`:**
- `e03_top_efectos_globales.csv`
- `e03_componentes_por_diversidad_efectos.csv`
- `e03_top_efectos_por_componente_detalle.csv`

---

## 8. RESULTADOS PRINCIPALES

### Hallazgo 1 — Los efectos más frecuentes son generalistas y transversales
Los 4 efectos más comunes afectan a más de la mitad del dataset:

| Efecto | Medicamentos |
|---|---|
| Nausea | 6.216 (53% del dataset) |
| Headache | 5.374 (46%) |
| Diarrhea | 4.553 (39%) |
| Dizziness | 4.064 (35%) |

No son efectos específicos de ninguna familia terapéutica: son respuestas generales del organismo a la medicación.

### Hallazgo 2 — La carga de efectos por medicamento es moderada con cola larga
- **Media:** 6,92 efectos/medicamento
- **Mediana:** 6,00
- **Rango IQR:** 4–9
- **Máximo:** 36 efectos (casos extremos aislados, posiblemente quimioterápicos)

### Hallazgo 3 — Más componentes NO implica más efectos secundarios (contraintuitivo)

| N° componentes | Media efectos |
|---|---|
| 1 | 6,92 |
| 2 | 6,92 |
| **3 (mayor)** | **7,27** |
| 4 | 6,22 |
| **5+ (menor)** | **4,55** |

Los tríos tienen la carga más alta y los complejos la más baja. Las formulaciones de 5+ componentes son altamente especializadas con perfiles de seguridad controlados.

### Hallazgo 4 — Más efectos listados NO implica peores valoraciones
- Correlación `n_efectos` ↔ `Poor Review %`: **r = −0,040** (prácticamente nula)
- Correlación `n_efectos` ↔ `Excellent Review %`: **r = +0,036** (prácticamente nula)

Listar más efectos en el prospecto no empeora la percepción del usuario. El conteo de efectos refleja **cobertura documental**, no severidad clínica percibida.

### Hallazgo 5 — El perfil de reviews varía entre componentes, pero no por carga de efectos
Con umbral mínimo de 100 observaciones:

| Componente (mejor) | Excellent % | Poor % |
|---|---|---|
| ramipril | 58,12% | 13,69% |
| enalapril | 57,47% | 12,03% |

| Componente (peor) | Poor % | Excellent % |
|---|---|---|
| letrozole | 43,33% | 29,83% |
| deflazacort | 42,85% | 27,02% |

Los peor valorados corresponden a patologías crónicas o difíciles (quimioterapia hormonal, corticosteroides), donde la experiencia negativa es intrínseca a la enfermedad.

---

## 9. DIFICULTADES Y SOLUCIONES

### Dificultad 1 — `Side_effects` no tiene separador explícito ⭐ (principal)
**Problema:** La columna concatena efectos usando la mayúscula inicial como único delimitador (`"Nausea Abdominal pain Diarrhea"`). No se puede hacer un split simple por coma o punto y coma.

**Solución:** regex `re.findall(r"[A-Z][^A-Z]*", texto)` que captura cada segmento que inicia con mayúscula. Captura correctamente efectos multipalabra como `"Abdominal pain"` o `"High blood pressure"`.

**Validación de la solución:** El EDA confirmó que todos los efectos en el dataset comienzan con mayúscula, eliminando el riesgo de falsos negativos por el regex.

### Dificultad 2 — Sesgo por frecuencia en el crosstab
**Problema:** Un componente con 664 medicamentos (Metformin) siempre tendría frecuencias absolutas mayores que uno con 10 medicamentos, haciendo imposible comparar patrones de efectos entre componentes.

**Solución:** Normalización del crosstab por fila (`tabla.div(sumas_fila, axis=0)`), convirtiendo frecuencias absolutas en proporciones. Ahora cada celda representa la proporción de medicamentos con ese componente que tienen ese efecto.

### Dificultad 3 — Explosión exponencial de filas en el doble explode
**Problema:** El producto cartesiano componente × efecto genera N×M filas por medicamento. Un medicamento con 3 componentes y 9 efectos genera 27 filas. El `df_long` resultante es mucho mayor que el dataset original.

**Solución:** Filtrado de componentes con mínimo 5 observaciones antes de construir el crosstab, y uso de `drop_empty=True` en las funciones de explode para eliminar filas vacías.

### Dificultad 4 — Discrepancia de tipos en validación de esquema
**Problema:** La validación esperaba tipo `object` para columnas de texto (comportamiento pandas <2.0), pero pandas ≥2.0 reporta `str`. La validación marcaba el esquema como inválido sin que hubiera un error real.

**Solución:** Documentar la discrepancia en `decisiones_limpieza.md` como comportamiento esperado de la versión de pandas. El pipeline funciona correctamente; solo el chequeo de tipo era el que fallaba por incompatibilidad de versión.

---

## Resumen ejecutivo

| Item | Valor |
|---|---|
| Foco | Efectos Secundarios por Componentes Activos |
| Columna principal | `Side_effects` (+ `Composition`) |
| Registros finales | 11.741 |
| Columnas derivadas | 7 |
| Componentes únicos | 875 (min. 5 obs.) |
| Efectos únicos | 761 (min. 5 obs.) |
| Efecto más frecuente | Nausea — 6.216 medicamentos (53%) |
| Componente con más diversidad efectos | menthol — 67 efectos distintos |
| Gráficos generados | 6 |
| Checksum MD5 | `93656e73e4e8fbf7dd8da9ecfab7ce07` |
