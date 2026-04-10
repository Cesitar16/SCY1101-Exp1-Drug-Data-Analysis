# Enfoque 3 — Efectos Secundarios por Componentes

**Proyecto:** SCY1101 - Programación para la Ciencia de Datos  
**Dataset:** `Medicine_Details.csv` — 11.741 registros post-limpieza  
**Universidad:** DuocUC 2026  

---

## ¿De qué trata este enfoque?

El **Enfoque 3** estudia la **relación entre los componentes activos de un medicamento y sus efectos secundarios**: qué efectos son más frecuentes en el dataset, qué componentes concentran mayor diversidad de efectos, cómo se distribuye la carga de efectos por tipo de medicamento y si existe una relación entre el número de componentes y el número de efectos secundarios.

Las columnas clave son dos:
- **`Composition`**: componentes activos del medicamento (con dosis), ej: `"Amoxycillin (500mg) + Clavulanic Acid (125mg)"`
- **`Side_effects`**: efectos secundarios concatenados **sin separador explícito**, usando la mayúscula inicial como delimitador implícito, ej: `"Nausea Abdominal pain Diarrhea"`

El desafío técnico único de este enfoque es el parseo de `Side_effects`, que requiere una estrategia de extracción por regex en lugar de un split simple.

---

## Preguntas que responde

| Pregunta | Respuesta (resumen) |
|---|---|
| ¿Qué efectos secundarios son más frecuentes en todo el dataset? | Nausea (6.216), Headache (5.374), Diarrhea (4.553), Dizziness (4.064) |
| ¿Qué componentes tienen mayor diversidad de efectos distintos? | Menthol (67), Amlodipine (60), Diclofenac (56), Telmisartan (55) |
| ¿Cuántos efectos secundarios tiene típicamente un medicamento? | Mediana = 6, media = 6,92, rango IQR = 4–9 |
| ¿Más componentes implica más efectos secundarios? | **No.** No hay relación lineal clara; los tríos tienen la media más alta |
| ¿Más efectos listados implica peores valoraciones? | **No.** Correlación casi nula (r = −0,040 con `Poor Review %`) |
| ¿Existen patrones de asociación componente → efecto? | Sí. El heatmap normalizado revela afinidades específicas por área terapéutica |

---

## Estructura de archivos

```
src/enfoque_03_efectos_secundarios_componentes/
├── cleaning.py       # Limpieza: parseo de componentes y efectos secundarios
├── transform.py      # Transformaciones: explode, crosstab, normalización, matriz binaria
├── analysis.py       # Visualizaciones y exportación de gráficos/tablas
└── validation.py     # Validación de integridad y checksums

notebooks/enfoque_03_efectos_secundarios_componentes/
├── 01_eda_efectos_secundarios_componentes.ipynb              # Exploración inicial
├── 02_limpieza_transformacion_efectos_secundarios.ipynb      # Ejecución del pipeline
└── 03_analisis_efectos_secundarios_componentes.ipynb         # Análisis y visualizaciones

docs/enfoque_03_combinaciones_componentes/
├── README.md                  # Este archivo
└── decisiones_limpieza.md     # Justificación técnica de cada decisión de limpieza
```

---

## Pipeline técnico

El análisis se ejecuta en tres etapas encadenadas:

### Etapa 1 — Limpieza (`cleaning.py`)

Función principal: `run_cleaning_pipeline(df)` → devuelve `df_clean`

| Paso | Función | Acción |
|---|---|---|
| 1 | `eliminar_duplicados()` | Elimina 84 filas completamente duplicadas |
| 2 | `extraer_componentes()` | Parsea nombres de principios activos desde `Composition`, elimina dosis y normaliza a minúsculas |
| 3 | `extraer_efectos_secundarios()` | Parsea `Side_effects` usando `re.findall(r"[A-Z][^A-Z]*")` — captura cada efecto por su inicial mayúscula |
| 4 | `añadir_columnas_derivadas()` | Genera `componentes`, `efectos_secundarios`, `manufacturer`, `n_componentes`, `n_efectos` |
| 5 | `flag_anomalias()` | Marca registros con 0 componentes o 0 efectos sin eliminarlos |

> **Diferencia clave vs Enfoque 1:** Los componentes se normalizan a **minúsculas** (no a Title Case) y los efectos se parsean con regex porque no tienen separador explícito.

**Columnas generadas:**

| Columna | Tipo | Descripción |
|---|---|---|
| `componentes` | `list[str]` | Componentes activos en minúsculas sin dosis |
| `efectos_secundarios` | `list[str]` | Efectos secundarios parseados en minúsculas |
| `manufacturer` | `str` | Fabricante normalizado a minúsculas |
| `n_componentes` | `int` | Número de principios activos por medicamento |
| `n_efectos` | `int` | Número de efectos secundarios por medicamento |
| `anomalia_componentes` | `bool` | `True` si no se extrajo ningún componente |
| `anomalia_efectos` | `bool` | `True` si no se extrajo ningún efecto |

**Impacto de la limpieza:**

| Métrica | Antes | Después |
|---|---|---|
| Filas | 11.825 | 11.741 |
| Filas eliminadas | — | 84 (-0,71%) |
| Columnas añadidas | — | 7 |
| Anomalías en componentes | — | 0 |
| Anomalías en efectos | — | 0 |
| Componentes únicos (min. 5 obs.) | — | 875 |
| Efectos únicos (min. 5 obs.) | — | 761 |

---

### Etapa 2 — Transformaciones (`transform.py`)

Función principal: `run_transform_pipeline(df_clean)` → devuelve `(df_long, crosstab, crosstab_norm)`

Este enfoque tiene la transformación más compleja del proyecto porque trabaja con **dos columnas de listas** simultáneamente:

| Transformación | Función | Salida | Descripción |
|---|---|---|---|
| Explode por efectos | `explotar_efectos()` | `df_efectos` | Una fila por (medicamento, efecto) |
| Explode por componentes | `explotar_componentes()` | `df_comp` | Una fila por (medicamento, componente) |
| **Producto cartesiano** | `explotar_todo()` | `df_long` | **Una fila por (medicamento, componente, efecto)** — N×M filas por medicamento con N componentes y M efectos |
| Tabla de contingencia | `construir_crosstab()` | `crosstab` | Matriz componente × efecto con frecuencias absolutas. Filtrado: mínimo 5 obs. por componente |
| Normalización | `normalizar_crosstab()` | `crosstab_norm` | Proporciones por fila: permite comparar componentes independientemente de su frecuencia total |
| Matriz binaria | `construir_matriz_efectos()` | — | Medicamento × top-30 efectos codificados 0/1 mediante `MultiLabelBinarizer`. Base para clustering |

Los tres DataFrames principales se exportan a `data/processed/`:
- `e03_medicine_long.csv`
- `e03_crosstab_componente_efecto.csv`
- `e03_crosstab_componente_efecto_norm.csv`

> **Por qué normalizar el crosstab:** Sin normalizar, un componente que aparece en 1.000 medicamentos siempre tendrá frecuencias absolutas mayores que uno con 10 apariciones, creando un sesgo visual. La normalización por fila convierte todo a proporciones, haciendo la comparación justa.

---

### Etapa 3 — Análisis y Visualizaciones (`analysis.py`)

Función principal: `run_analysis_pipeline(df_clean, df_long, crosstab, crosstab_norm)`

Genera **6 gráficos** en `outputs/figures/` y **3 tablas CSV** en `outputs/tables/`:

| # | Gráfico | Archivo | Pregunta que responde |
|---|---|---|---|
| 1 | Barplot top efectos globales | `e03_top_efectos_globales.png` | ¿Qué efectos secundarios son más transversales en todo el dataset? |
| 2 | Barplot diversidad por componente | `e03_componentes_por_diversidad_efectos.png` | ¿Qué componentes presentan el catálogo más amplio de efectos distintos? |
| 3 | Heatmap componente × efecto (norm.) | `e03_heatmap_componente_efecto_norm.png` | ¿Qué efectos tiene mayor afinidad con cada componente específico? |
| 4 | Boxplot efectos por N componentes | `e03_boxplot_efectos_por_n_componentes.png` | ¿Medicamentos más complejos tienen más efectos secundarios? |
| 5 | Scatterplot top efectos por comp. | `e03_top_efectos_por_componente_detalle.png` | Detalle de efectos frecuentes para los 5 componentes más representados |
| 6 | Histograma distribución n_efectos | `e03_histograma_n_efectos.png` | ¿Cuántos efectos secundarios tiene típicamente un medicamento? |

---

### Etapa 4 — Validación (`validation.py`)

Función principal: `run_validation_pipeline(df_raw, df_clean)`

| Verificación | Método | Resultado |
|---|---|---|
| Integridad del archivo fuente | MD5 checksum | `93656e73e4e8fbf7dd8da9ecfab7ce07` |
| Esquema del DataFrame raw | Validación de columnas y tipos | ⚠️ Mínima discrepancia `str` vs `object` (pandas ≥2.0, no funcional) |
| Impacto de la limpieza | Comparación de shapes | ✅ 84 filas eliminadas (0,71%) |
| Columnas derivadas en df_clean | Lista de columnas esperadas | ✅ Las 7 columnas presentes |

El reporte se exporta a `outputs/reports/reporte_integridad_e03.json`.

> **Nota técnica:** La discrepancia `str` vs `object` en el esquema ocurre porque pandas ≥ 2.0 infiere `str` para columnas de texto puro. No afecta el comportamiento del pipeline.

---

## Hallazgos principales

### 1. Los efectos secundarios más frecuentes son generalistas y transversales

Los 10 efectos más comunes afectan a una gran proporción del dataset y no son específicos de ninguna área terapéutica particular:

| Posición | Efecto | Medicamentos |
|---|---|---|
| 1 | Nausea | 6.216 |
| 2 | Headache | 5.374 |
| 3 | Diarrhea | 4.553 |
| 4 | Dizziness | 4.064 |
| 5 | Vomiting | 3.499 |
| 6 | Abdominal pain | 1.883 |
| 7 | Sleepiness | 1.791 |
| 8 | Constipation | 1.699 |
| 9 | Fatigue | 1.520 |
| 10 | Stomach pain | 1.426 |

Nausea aparece en más de la mitad del dataset (6.216 de 11.741 medicamentos). La dominancia de síntomas gastrointestinales y neurológicos leves sugiere que estos efectos reflejan la respuesta general del organismo a la medicación, más que perfiles específicos de cada fármaco.

---

### 2. La carga de efectos por medicamento es moderada con cola larga

| Estadístico | Valor |
|---|---|
| Media | 6,92 efectos/medicamento |
| Mediana | 6,00 |
| P25 | 4,00 |
| P75 | 9,00 |
| Máximo | 36,00 |

La mayoría de los medicamentos lista entre 4 y 9 efectos secundarios. Los casos extremos (hasta 36 efectos) son raros y corresponden probablemente a fármacos de amplio espectro como quimioterápicos o inmunosupresores.

---

### 3. Los componentes con mayor diversidad de efectos son los más frecuentes en el dataset

Los componentes con más efectos distintos coinciden casi exactamente con los componentes con más apariciones (Enfoque 1). Esto sugiere que la diversidad de efectos es un artefacto de la frecuencia: aparecer en muchos medicamentos distintos acumula más documentación de efectos.

| Posición | Componente | Efectos distintos |
|---|---|---|
| 1 | menthol | 67 |
| 2 | amlodipine | 60 |
| 3 | diclofenac | 56 |
| 4 | telmisartan | 55 |
| 5 | chlorpheniramine maleate | 54 |
| 6 | phenylephrine | 53 |
| 7 | paracetamol | 53 |
| 8 | hydrochlorothiazide | 52 |
| 9 | ambroxol | 52 |
| 10 | montelukast | 49 |

**Interpretación:** La alta diversidad de efectos en componentes frecuentes puede reflejar tanto su uso en indicaciones variadas como una mayor cobertura documental de seguridad, no necesariamente mayor peligrosidad.

---

### 4. La tabla componente × efecto revela afinidades específicas por área terapéutica

El heatmap normalizado muestra que las asociaciones componente → efecto **no son aleatorias**: ciertos efectos están fuertemente marcados para componentes específicos.

Patrones observados:
- **Antidiabéticos (metformin, glimepiride):** mayor proporción de efectos gastrointestinales (nausea, diarrhea, abdominal pain)
- **Antihipertensivos (amlodipine, telmisartan):** dizziness, headache y fatigue con mayor proporción relativa
- **Antihistamínicos/descongestionantes (chlorpheniramine, phenylephrine):** sleepiness y dry mouth con mayor afinidad

La normalización por fila asegura que estas proporciones sean comparables entre componentes con volúmenes muy distintos.

---

### 5. Más componentes NO implica más efectos secundarios (relación no lineal)

El boxplot de `n_efectos` por `n_componentes` muestra un resultado **contraintuitivo**:

| N° componentes | Media efectos aprox. | Mediana aprox. |
|---|---|---|
| 1 | 6,92 | 6 |
| 2 | 6,92 | 6 |
| 3 | 7,27 | 7 |
| 4 | 6,22 | 5 |
| 5+ | 4,55 | 4 |

Los **tríos** tienen la media más alta (~7,27), pero los medicamentos complejos (5+ componentes) tienen la **carga más baja**. Esto es consistente con el hallazgo del Enfoque 1: las formulaciones complejas son altamente especializadas con perfiles de seguridad controlados y documentados de forma más restrictiva.

**Implicación:** El número de ingredientes no es un buen predictor de la carga de efectos secundarios listados en este dataset.

---

### 6. Más efectos secundarios listados no implica peores valoraciones de usuario

| Correlación | r |
|---|---|
| `n_efectos` ↔ `Poor Review %` | −0,040 |
| `n_efectos` ↔ `Excellent Review %` | +0,036 |

Ambas correlaciones son prácticamente nulas. A mayor número de efectos listados, la valoración no empeora — de hecho, hay una leve señal positiva (más efectos documentados → levemente mejor valoración). Esto sugiere que el conteo de efectos en `Side_effects` refleja **cobertura documental**, no severidad clínica percibida por el usuario.

Promedios por tramos de efectos:

| Tramo | Excellent % promedio | Poor % promedio |
|---|---|---|
| 1-3 efectos | 36,92% | 27,25% |
| 4-6 efectos | 37,95% | 26,44% |
| 7-9 efectos | 39,81% | 24,31% |
| 10-12 efectos | 38,87% | 25,49% |
| 13+ efectos | 40,23% | 23,78% |

---

### 7. El perfil de reviews varía entre componentes, pero no por carga de efectos

Con umbral mínimo de 100 observaciones por componente, emergen componentes con perfiles de valoración claramente diferenciados:

**Mejor valorados (Excellent % promedio):**
| Componente | Excellent % | Poor % | Obs. |
|---|---|---|---|
| ramipril | 58,12% | 13,69% | 465 |
| enalapril | 57,47% | 12,03% | 112 |
| desvenlafaxine | 57,05% | 16,67% | 189 |
| lisinopril | 55,50% | 10,94% | 129 |
| lacosamide | 54,94% | 10,17% | 144 |

**Peor valorados (Poor % promedio):**
| Componente | Poor % | Excellent % | Obs. |
|---|---|---|---|
| letrozole | 43,33% | 29,83% | 108 |
| deflazacort | 42,85% | 27,02% | 133 |
| lactulose | 42,08% | 25,54% | 128 |
| mirabegron | 40,36% | 32,97% | 174 |
| ethamsylate | 39,62% | 28,16% | 175 |

Los peor valorados corresponden a fármacos usados en condiciones crónicas o difíciles (quimioterapia hormonal, corticosteroides), donde la experiencia del paciente es intrínsecamente más negativa por la enfermedad subyacente, no por el medicamento en sí.

---

## Particularidad técnica: parseo de `Side_effects`

Este enfoque resuelve un problema de ingeniería de datos que los otros enfoques no tienen: la columna `Side_effects` **no tiene separador explícito** entre efectos. Los datos se ven así:

```
"Nausea Abdominal pain Diarrhea"
"Rectal bleeding Taste change Headache Nosebleeds"
```

La estrategia implementada usa `re.findall(r"[A-Z][^A-Z]*", texto)` para detectar cada segmento que comienza con mayúscula, capturando correctamente efectos multipalabra como `"Abdominal pain"` o `"High blood pressure"`.

**Limitación conocida y mitigada:** Si un efecto tuviera todas las palabras en minúsculas, no sería detectado. El EDA confirmó que **todos los efectos observados comienzan con mayúscula**, por lo que esta limitación no afecta la calidad del análisis.

---

## Cómo ejecutar el análisis

```python
from src.load_data import load_medicine_data
from src.enfoque_03_efectos_secundarios_componentes.cleaning import run_cleaning_pipeline
from src.enfoque_03_efectos_secundarios_componentes.transform import run_transform_pipeline
from src.enfoque_03_efectos_secundarios_componentes.analysis import run_analysis_pipeline
from src.enfoque_03_efectos_secundarios_componentes.validation import run_validation_pipeline

# 1. Cargar datos
df_raw = load_medicine_data()

# 2. Limpiar
df_clean = run_cleaning_pipeline(df_raw)

# 3. Transformar
df_long, crosstab, crosstab_norm = run_transform_pipeline(df_clean)

# 4. Analizar (genera todos los gráficos)
run_analysis_pipeline(df_clean, df_long, crosstab, crosstab_norm)

# 5. Validar integridad
run_validation_pipeline(df_raw, df_clean)
```

También se puede ejecutar paso a paso desde los notebooks en `notebooks/enfoque_03_efectos_secundarios_componentes/`.

---

## Datos técnicos del dataset en este enfoque

| Parámetro | Valor |
|---|---|
| Registros raw | 11.825 |
| Registros post-limpieza | 11.741 |
| Duplicados eliminados | 84 (0,71%) |
| Columnas derivadas creadas | 7 |
| Componentes únicos extraídos (min. 5 obs.) | 875 |
| Efectos únicos extraídos (min. 5 obs.) | 761 |
| MD5 del archivo fuente | `93656e73e4e8fbf7dd8da9ecfab7ce07` |

---

## Posición del enfoque 3 en el proyecto

El Enfoque 3 es la **capa de seguridad** del análisis. Solo, no es suficiente para explicar la reputación de los medicamentos (las correlaciones con reviews son casi nulas). Pero aporta contexto valioso al combinar con los otros enfoques:

- **Enfoque 1** identifica qué combinaciones dominan el mercado
- **Enfoque 2** compara fabricantes sobre las mismas formulaciones
- **Enfoque 3** agrega la dimensión de seguridad: ¿qué perfiles de efectos tienen los componentes más frecuentes?

El insight más defendible de este enfoque es que la **documentación de efectos secundarios no refleja peligrosidad percibida**: listar más efectos no empeora la valoración del usuario, lo que sugiere que los pacientes valoran la transparencia farmacológica.

---

## Documentos relacionados

- [decisiones_limpieza.md](./decisiones_limpieza.md) — Justificación técnica de cada decisión de limpieza, con impacto cuantificado y ejemplos de parseo
- [analisis_integrado_enfoques.md](../analisis_integrado_enfoques.md) — Síntesis comparativa de los tres enfoques del proyecto
- [Enfoque 1 README](../enfoque_01_combinaciones_componentes/README.md) — Documentación del análisis de combinaciones de componentes
