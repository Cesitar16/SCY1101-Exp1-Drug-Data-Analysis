# INFORME TÉCNICO
## Enfoque 1 — Combinaciones de Componentes Activos

**Asignatura:** SCY1101 - Programación para la Ciencia de Datos  
**Dataset:** `Medicine_Details.csv`  
**Institución:** DuocUC | **Año:** 2026  

> **Versión Word disponible:** [`informe_tecnico_enfoque_01.docx`](./informe_tecnico_enfoque_01.docx)

---

## 1. Descripción del Foco de Análisis

El **Enfoque 1** estudia la estructura interna de las formulaciones farmacéuticas: qué principios activos componen cada medicamento, qué combinaciones son más frecuentes y cómo se relacionan entre sí en el mercado representado por el dataset.

La columna principal analizada es `Composition`, que contiene cadenas del tipo `"Amoxycillin (500mg) + Clavulanic Acid (125mg)"`. El enfoque extrae los nombres de los componentes descartando las dosis, y construye una red de co-ocurrencias para revelar los patrones de combinación.

### Preguntas de investigación

| Pregunta | Respuesta |
|---|---|
| ¿Qué componentes individuales dominan el mercado? | Metformin (664), Telmisartan (379), Glimepiride (379), Paracetamol (359) |
| ¿Qué pares de componentes son más frecuentes? | Glimepiride + Metformin (325 medicamentos), dominando ampliamente |
| ¿El mercado está dominado por mono o multi-componentes? | Sí: 59,8% monocomponente, 30,4% dúos. El 90,2% tiene 1–2 componentes |
| ¿Más componentes implica más efectos secundarios? | **No.** Los complejos (5+) tienen la mediana de efectos más baja |
| ¿La valoración varía con el número de componentes? | Los dúos (~41%) tienen la mejor valoración; decrece desde tríos en adelante |
| ¿Existen componentes hub? | Sí. Metformin es el hub absoluto con 664 apariciones |

---

## 2. Archivos Desarrollados

| Archivo | Responsabilidad |
|---|---|
| `src/enfoque_01_combinaciones_componentes/cleaning.py` | Limpieza: duplicados, normalización, extracción de componentes, columnas derivadas |
| `src/enfoque_01_combinaciones_componentes/transform.py` | Transformaciones: explode, pares con `itertools.combinations`, matriz de co-ocurrencia |
| `src/enfoque_01_combinaciones_componentes/analysis.py` | 7 visualizaciones y exportación de gráficos (.png) y tablas (.csv) |
| `src/enfoque_01_combinaciones_componentes/validation.py` | Checksum MD5, validación de esquema, comparación de shapes |

---

## 3. Pipeline Implementado

### 3.1 Limpieza — `cleaning.py`

Función principal: `run_cleaning_pipeline(df)`

| Paso | Función | Acción |
|---|---|---|
| 1 | `eliminar_duplicados()` | Elimina 84 filas completamente idénticas |
| 2 | `normalizar_composicion()` | Estandariza espacios y el separador `+` en `Composition` |
| 3 | `extraer_componentes()` | Parsea nombres de principios activos, descarta dosis entre paréntesis, aplica Title Case |
| 4 | `añadir_columnas_componentes()` | Genera `components_list`, `n_components` y `size_category` (`pd.Categorical`, `ordered=True`) |
| 5 | `flag_anomalies()` | Marca registros con `n_components == 0` sin eliminarlos automáticamente |

**Columnas generadas:**

| Columna | Tipo | Descripción |
|---|---|---|
| `components_list` | `list[str]` | Lista de componentes sin dosis (ej: `['Amoxycillin', 'Clavulanic Acid']`) |
| `n_components` | `int` | Número de principios activos por medicamento |
| `size_category` | `pd.Categorical` | Categoría ordinal: `mono < duo < trio < cuádruple < complejo` |
| `composition_anomaly` | `bool` | `True` si no se extrajo ningún componente válido |

**Impacto cuantificado:**

| Métrica | Valor |
|---|---|
| Filas raw | 11.825 |
| Duplicados eliminados | 84 (−0,71%) |
| Filas post-limpieza | 11.741 |
| Columnas añadidas | 4 |
| Componentes únicos detectados | 1.058 |
| Anomalías detectadas | 0 |

> **Decisión técnica clave:** `size_category` se define como `pd.Categorical(ordered=True)` para que el orden farmacológico (`mono < duo < ... < complejo`) sea respetado en todas las operaciones posteriores: gráficos, `sort_values`, comparaciones y `groupby`.

---

### 3.2 Transformaciones — `transform.py`

Función principal: `run_transform_pipeline(df_clean)` → `(df_exploded, df_pairs, cooc_matrix)`

| Función | Salida | Descripción |
|---|---|---|
| `explotar_componentes()` | `df_exploded` (17.957 filas) | Explode de `components_list` → una fila por componente. Permite contar frecuencias individuales |
| `explotar_pares()` | `df_pairs` (8.227 pares) | Genera todos los pares C(N,2) por medicamento con N≥2 componentes usando `itertools.combinations` |
| `construir_matriz_coocurrencia()` | `cooc_matrix` (20×20) | `pd.crosstab()` → matriz cuadrada simétrica. `cooc[i][j]` = medicamentos con ambos componentes i y j |

> **Decisión técnica:** Los pares se ordenan alfabéticamente con `sorted(components)` antes de generarse, garantizando que `(A, B)` y `(B, A)` siempre se representen de la misma forma y no aparezcan como pares distintos.

Archivos exportados a `data/processed/`:
- `medicine_exploded.csv`
- `medicine_pairs.csv`
- `cooc_matrix.csv`

---

### 3.3 Validación de Integridad — `validation.py`

Función principal: `run_validation_pipeline(df_raw, df_clean)` → exporta `outputs/reports/reporte_integridad.json`

| # | Función | Verificación | Resultado |
|---|---|---|---|
| 1 | `verificar_checksum()` | MD5 del CSV raw | `93656e73e4e8fbf7dd8da9ecfab7ce07` ✅ |
| 2 | `validar_esquema()` | Columnas y tipos del DataFrame raw | 9 columnas con tipos correctos ✅ |
| 3 | `comparar_shapes()` | Dimensiones antes/después | 84 filas eliminadas (0,71%) ✅ |
| 4 | `validar_columnas_clean()` | Columnas derivadas en df_clean | Las 4 columnas presentes ✅ |

---

### 3.4 Análisis y Visualizaciones — `analysis.py`

Función principal: `run_analysis_pipeline(df_clean, df_exploded, df_pairs, cooc_matrix)`

Genera **7 gráficos** en `outputs/figures/` y **2 tablas CSV** en `outputs/tables/`:

| # | Función | Archivo generado | Pregunta respondida |
|---|---|---|---|
| 1 | `plot_histograma_componentes()` | `histograma_n_componentes.png` | ¿Cómo se distribuyen los medicamentos por número de componentes? |
| 2 | `plot_top_componentes()` | `top_componentes_individuales.png` | ¿Qué principios activos son más frecuentes? |
| 3 | `plot_top_pares()` | `top_pares_componentes.png` | ¿Qué combinaciones de dos componentes dominan? |
| 4 | `plot_heatmap_coocurrencia()` | `heatmap_coocurrencia.png` | ¿Qué pares co-ocurren más entre los 20 componentes top? |
| 5 | `plot_efectos_secundarios_por_tamanio()` | `boxplot_efectos_secundarios.png` | ¿Más componentes = más efectos secundarios? |
| 6 | `plot_network_graph()` | `network_graph_coocurrencia.png` | ¿Cómo se conectan los componentes en una red? |
| 7 | `plot_scatter_valoracion()` | `scatter_valoracion_componentes.png` | ¿La valoración varía con el número de componentes? |

---

## 4. Resultados Principales

### 4.1 Distribución por Tamaño de Combinación

El dataset presenta distribución de cola larga, fuertemente concentrada en monocomponentes y dúos. El **90,2%** del mercado representado tiene 1 o 2 principios activos.

| N° Componentes | Medicamentos | Porcentaje |
|---|---|---|
| 1 (mono) | 7.019 | 59,8% |
| 2 (duo) | 3.569 | 30,4% |
| 3 (trio) | 929 | 7,9% |
| 4 (cuádruple) | 147 | 1,3% |
| 5+ (complejo) | 77 | 0,7% |
| **Total** | **11.741** | **100%** |

---

### 4.2 Componentes Hub — Top 10

**Metformin** es el componente hub dominante con **664 apariciones**, un 75% más que el segundo lugar. Su dominio refleja la alta prevalencia de diabetes tipo 2 en India, país de origen del dataset.

| Pos. | Componente | Medicamentos | Área Terapéutica |
|---|---|---|---|
| 1 | Metformin | 664 | Antidiabético |
| 2 | Telmisartan | 379 | Antihipertensivo |
| 3 | Glimepiride | 379 | Antidiabético |
| 4 | Paracetamol | 359 | Analgésico/Antipirético |
| 5 | Amlodipine | 314 | Antihipertensivo |
| 6 | Montelukast | 224 | Antiasmático |
| 7 | Pregabalin | 214 | Antiepiléptico/Analgésico |
| 8 | Methylcobalamin | 214 | Vitamina B12 |
| 9 | Metoprolol Succinate | 209 | Betabloqueante |
| 10 | Rosuvastatin | 209 | Estatina |

---

### 4.3 Pares de Componentes Más Frecuentes — Top 10

**Glimepiride + Metformin** domina con **325 medicamentos**, casi 2,6 veces el segundo par. Esta combinación une dos mecanismos complementarios para la diabetes tipo 2.

| Pos. | Par | Medicamentos | Área Terapéutica |
|---|---|---|---|
| 1 | Glimepiride + Metformin | 325 | Antidiabético |
| 2 | Levocetirizine + Montelukast | 124 | Alérgico/Asma |
| 3 | Metformin + Voglibose | 124 | Antidiabético |
| 4 | Methylcobalamin + Pregabalin | 122 | Neuropatía |
| 5 | Amoxycillin + Clavulanic Acid | 97 | Antibiótico |
| 6 | Ambroxol + Guaifenesin | 91 | Respiratorio |
| 7 | Amlodipine + Telmisartan | 90 | Antihipertensivo |
| 8 | Aceclofenac + Paracetamol | 88 | Analgésico |
| 9 | Metformin + Pioglitazone | 87 | Antidiabético |
| 10 | Glimepiride + Voglibose | 86 | Antidiabético |

---

### 4.4 Clusters de Co-ocurrencia

La matriz de co-ocurrencia (20×20) y el grafo de red revelan **tres clusters terapéuticos bien separados**. Los componentes prácticamente no cruzan clusters, lo que valida la coherencia clínica del dataset.

| Cluster | Componentes principales | Co-ocurrencia máxima | Observación |
|---|---|---|---|
| Antidiabético | Metformin, Glimepiride, Voglibose | 325 (Metformin–Glimepiride) | Conexión más fuerte del dataset |
| Antihipertensivo | Telmisartan, Amlodipine, Hydrochlorothiazide | 90 (Amlodipine–Telmisartan) | Telmisartan actúa como hub del cluster |
| Analgésico/Resp. | Paracetamol, Aceclofenac, Phenylephrine | 88 (Paracetamol–Aceclofenac) | Paracetamol es el nodo de mayor grado |

---

### 4.5 Efectos Secundarios según Tamaño de Combinación

**Hallazgo contraintuitivo:** los medicamentos complejos (5+ componentes) tienen la mediana **más baja** de efectos secundarios (~4), mientras que los tríos tienen la más alta (~7). Esto refuta la hipótesis de que más componentes implica más efectos.

| Categoría | Mediana efectos | Rango IQR |
|---|---|---|
| mono (1) | 6 | 5 – 9 |
| duo (2) | 6 | 5 – 9 |
| trio (3) | **7** | 5 – 11 |
| cuádruple (4) | 5 | 4 – 10 |
| complejo (5+) | **4** | 3 – 5 |

**Interpretación:** Las formulaciones complejas son altamente especializadas con perfiles de seguridad controlados. Los monocomponentes y dúos incluyen fármacos de amplio espectro con perfiles de efectos más extensos.

---

### 4.6 Valoración de Usuarios por Número de Componentes

Los **dúos** obtienen la mejor valoración promedio (~41%), superando a los monocomponentes (~38%). Desde 3 componentes en adelante la valoración decrece de forma consistente.

| N° Componentes | Excellent Review % promedio |
|---|---|
| 1 (mono) | 37,3% |
| 2 (duo) | **41,0%** ← máximo |
| 3 (trio) | 38,9% |
| 4 (cuádruple) | 35,8% |
| 5 (complejo) | 35,6% |
| 6 | 25,4% |

> Los grupos de 7, 8 y 9 componentes tienen muestras insuficientes (7, 2 y 1 medicamentos respectivamente) para conclusiones estadísticamente robustas.

---

## 5. Conclusiones

1. **Concentración del mercado:** El 90,2% del dataset corresponde a formulaciones de 1 o 2 componentes. Los medicamentos de 5+ componentes son estadísticamente marginales y no deben dominar las conclusiones generales.

2. **Dominio terapéutico:** Los hubs del dataset son Metformin, Glimepiride, Telmisartan y Amlodipine, reflejando que el mercado representado está centrado en **diabetes tipo 2, hipertensión arterial y dolor crónico**.

3. **Estructura de red:** La red de co-ocurrencias forma tres clusters terapéuticos bien definidos y separados. No hay cruce de componentes entre áreas terapéuticas, lo cual valida la calidad y coherencia clínica del dataset.

4. **Efectos secundarios:** La complejidad de la formulación no aumenta linealmente los efectos secundarios. Las formulaciones complejas son más especializadas y tienen perfiles de seguridad más controlados.

5. **Valoración de usuario:** Los dúos representan el punto óptimo: mayor volumen, co-ocurrencias claras y mejor valoración promedio. La complejidad adicional (3+ componentes) no mejora la percepción del usuario.

6. **Reproducibilidad:** El pipeline es completamente trazable: checksum MD5 del archivo fuente (`93656e73e4e8fbf7dd8da9ecfab7ce07`), reporte JSON de validación y exportación automática de todos los DataFrames intermedios a `data/processed/`.

---

## 6. Instrucciones de Ejecución

```python
from src.load_data import load_medicine_data
from src.enfoque_01_combinaciones_componentes.cleaning import run_cleaning_pipeline
from src.enfoque_01_combinaciones_componentes.transform import run_transform_pipeline
from src.enfoque_01_combinaciones_componentes.analysis import run_analysis_pipeline
from src.enfoque_01_combinaciones_componentes.validation import run_validation_pipeline

df_raw = load_medicine_data()
df_clean = run_cleaning_pipeline(df_raw)
df_exploded, df_pairs, cooc_matrix = run_transform_pipeline(df_clean)
run_analysis_pipeline(df_clean, df_exploded, df_pairs, cooc_matrix)
run_validation_pipeline(df_raw, df_clean)
```

O ejecutar los notebooks en orden desde `notebooks/enfoque_01_combinaciones_componentes/`.

---

## Documentos relacionados

- [`informe_tecnico_enfoque_01.docx`](./informe_tecnico_enfoque_01.docx) — Versión Word de este informe
- [`decisiones_limpieza.md`](./decisiones_limpieza.md) — Justificación técnica de cada decisión de limpieza
- [`analisis_graficos.md`](./analisis_graficos.md) — Interpretación detallada de los 7 gráficos
- [`../analisis_integrado_enfoques.md`](../analisis_integrado_enfoques.md) — Síntesis comparativa de los tres enfoques
