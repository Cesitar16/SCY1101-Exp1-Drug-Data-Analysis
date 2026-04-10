# Análisis de Visualizaciones y Tablas
## Foco: Combinaciones de Componentes Activos
**Dataset:** Medicine_Details.csv | 11.741 registros (post-limpieza) | DuocUC 2026

---

## 1. Histograma — Distribución según número de componentes

### Descripción técnica
Gráfico de barras que muestra la frecuencia absoluta de medicamentos según su número de componentes activos. El eje X representa el número de componentes (de 1 a 9) y el eje Y la cantidad de medicamentos en cada grupo.

### Análisis

El dataset presenta una **distribución de cola larga hacia la derecha**, fuertemente concentrada en los primeros valores. Los datos son los siguientes:

| N° componentes | Medicamentos | Porcentaje |
|---|---|---|
| 1 (mono) | 7.019 | 59,8% |
| 2 (duo) | 3.569 | 30,4% |
| 3 (trio) | 929 | 7,9% |
| 4 (cuádruple) | 147 | 1,3% |
| 5+ (complejo) | 77 | 0,7% |

El **59,8% del mercado farmacéutico** representado en este dataset corresponde a formulaciones de un solo principio activo. Esto es consistente con la práctica farmacéutica general, donde los monocomponentes son la base terapéutica y las combinaciones se reservan para patologías crónicas que requieren acción sinérgica entre principios activos.

La caída entre dúos (3.569) y tríos (929) es pronunciada: los tríos representan apenas el 26% de los dúos. Esto sugiere que combinar tres o más principios activos en una sola formulación implica una barrera técnica y regulatoria significativamente mayor.

Los valores en 5-9 componentes son estadísticamente marginales (77 medicamentos en total, 0,7%), por lo que cualquier análisis sobre estos grupos debe interpretarse con precaución.

### Implicación para el análisis
Esta distribución **justifica el foco del análisis en dúos y tríos**, que concentran el 38,3% del dataset y tienen suficiente volumen para extraer patrones significativos. Los grupos de 5+ componentes se agrupan en la categoría "complejo" para análisis comparativos.

---

## 2. Barplot — Top 20 componentes activos más frecuentes

### Tabla de datos completa

| Posición | Componente | Medicamentos | Área terapéutica |
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
| 11 | Domperidone | 198 | Procinético |
| 12 | Hydrochlorothiazide | 197 | Diurético |
| 13 | Levocetirizine | 195 | Antihistamínico |
| 14 | Olmesartan Medoxomil | 191 | Antihipertensivo |
| 15 | Ketoconazole | 181 | Antifúngico |
| 16 | Atorvastatin | 175 | Estatina |
| 17 | Rabeprazole | 167 | Inhibidor de bomba de protones |
| 18 | Voglibose | 161 | Antidiabético |
| 19 | Aceclofenac | 157 | Antiinflamatorio |
| 20 | Ambroxol | 143 | Mucolítico |

### Análisis

**Metformin es el componente hub dominante** con 664 medicamentos, casi un 75% más que el segundo lugar (Telmisartan y Glimepiride, con 379 cada uno). Esta diferencia es sustancial y no casual: Metformin es el tratamiento de primera línea para la diabetes tipo 2, una de las enfermedades crónicas más prevalentes a nivel mundial y especialmente en India, país de origen del dataset.

Al clasificar los 20 componentes por área terapéutica, emerge un patrón claro:

- **Antidiabéticos:** Metformin (664), Glimepiride (379), Voglibose (161) — 3 componentes en el top 20
- **Antihipertensivos:** Telmisartan (379), Amlodipine (314), Hydrochlorothiazide (197), Olmesartan Medoxomil (191) — 4 componentes
- **Analgésicos/AINE:** Paracetamol (359), Aceclofenac (157) — 2 componentes
- **Neurológicos:** Pregabalin (214), Methylcobalamin (214) — frecuentemente combinados para neuropatía diabética

La co-presencia de antidiabéticos y antihipertensivos en el top refleja la alta comorbilidad entre diabetes tipo 2 e hipertensión arterial, condición conocida como síndrome metabólico.

**Hallazgo notable:** Paracetamol (359) aparece en el top pese a ser un analgésico de amplio espectro, lo que sugiere que es frecuentemente usado como componente en formulaciones combinadas con antiinflamatorios y descongestionantes.

---

## 3. Barplot — Top 20 pares de componentes más frecuentes

### Tabla de datos completa

| Posición | Par | Medicamentos | Área terapéutica |
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
| 11 | Chlorpheniramine Maleate + Phenylephrine | 84 | Descongestionante |
| 12 | Hydrochlorothiazide + Telmisartan | 74 | Antihipertensivo |
| 13 | Chlorthalidone + Telmisartan | 67 | Antihipertensivo |
| 14 | Domperidone + Rabeprazole | 67 | Gastrointestinal |
| 15 | Glimepiride + Pioglitazone | 66 | Antidiabético |
| 16 | Domperidone + Pantoprazole | 62 | Gastrointestinal |
| 17 | Amlodipine + Hydrochlorothiazide | 57 | Antihipertensivo |
| 18 | Ambroxol + Levosalbutamol | 57 | Respiratorio |
| 19 | Nortriptyline + Pregabalin | 57 | Neurológico |
| 20 | Guaifenesin + Levosalbutamol | 56 | Respiratorio |

### Análisis

**Glimepiride + Metformin domina con 325 medicamentos**, casi 2,6 veces el segundo par más frecuente. Este par combina dos mecanismos de acción complementarios para la diabetes tipo 2: Metformin reduce la producción hepática de glucosa, mientras que Glimepiride estimula la secreción pancreática de insulina. Su alta frecuencia refleja que esta combinación es un estándar clínico consolidado.

Al analizar los 20 pares por área terapéutica:
- **Antidiabéticos:** 5 pares (posiciones 1, 3, 9, 10, 15) — dominan el ranking
- **Antihipertensivos:** 4 pares (posiciones 7, 12, 13, 17)
- **Respiratorio:** 3 pares (posiciones 6, 18, 20)
- **Gastrointestinal:** 2 pares (posiciones 14, 16) — Domperidone actúa como procinético combinado con inhibidores de bomba de protones

**Hallazgo notable:** El par Amoxycillin + Clavulanic Acid (97 medicamentos, posición 5) es el único antibiótico en el top 20. Clavulanic Acid es un inhibidor de betalactamasas que potencia la acción de Amoxycillin frente a bacterias resistentes, lo que explica su alta prevalencia: es una combinación de amplio uso en infecciones respiratorias y urinarias.

**Brecha de frecuencia:** Existe un salto significativo entre el primer par (325) y el grupo del segundo al cuarto (122-124). Esto indica que Glimepiride + Metformin no es simplemente el más frecuente, sino que tiene una posición de dominio absoluto en el dataset.

---

## 4. Heatmap — Matriz de co-ocurrencia entre componentes activos

### Análisis

La matriz de co-ocurrencia entre los 20 componentes más frecuentes revela la estructura de afinidad entre principios activos. Cada celda [i][j] indica cuántos medicamentos contienen simultáneamente los componentes i y j.

**Patrones principales identificados:**

**Cluster antidiabético** (esquina superior izquierda y zona central):
- Metformin–Glimepiride: 325 (el valor más alto de toda la matriz)
- Metformin–Voglibose: 124
- Glimepiride–Voglibose: 86
- Metformin–Methylcobalamin: 12 (conexión cruzada con neuropatía)

Estos tres componentes forman un triángulo de alta co-ocurrencia que domina visualmente la matriz por intensidad de color.

**Cluster antihipertensivo** (zona media):
- Amlodipine–Telmisartan: 90
- Hydrochlorothiazide–Telmisartan: 74
- Amlodipine–Hydrochlorothiazide: 57
- Amlodipine–Olmesartan Medoxomil: 52

Estos cuatro forman un segundo cluster bien definido, donde Telmisartan actúa como hub con conexiones fuertes hacia Amlodipine e Hydrochlorothiazide simultáneamente.

**Cluster neurológico/analgésico** (zona derecha):
- Methylcobalamin–Pregabalin: 122 (combinación estándar para neuropatía diabética)
- Paracetamol–Aceclofenac: 88 (analgésico + antiinflamatorio)
- Paracetamol–Diclofenac: 41
- Folic Acid–Vitamin B6: 37 (suplementos vitamínicos combinados)

**Hallazgo estructural:** La mayoría de las celdas son 0, lo que confirma que las combinaciones son altamente específicas por área terapéutica. Los componentes de distintos clusters prácticamente no co-ocurren entre sí, lo que es consistente con la práctica clínica: no se combina un antidiabético con un mucolítico en la misma formulación.

---

## 5. Boxplot — Efectos secundarios según tamaño de combinación


### Análisis

El boxplot compara la distribución del número de efectos secundarios entre los cinco grupos de tamaño de combinación, donde el número de efectos fue aproximado contando las palabras con inicial mayúscula en la columna `Side_effects`.

**Medianas observadas:**

| Categoría | Mediana aprox. | Rango IQR |
|---|---|---|
| mono | 6 | 5 – 9 |
| duo | 6 | 5 – 9 |
| trio | 7 | 5 – 11 |
| cuádruple | 5 | 4 – 10 |
| complejo | 4 | 3 – 5 |

**Hallazgo contraintuitivo:** Contrario a la hipótesis inicial de que más componentes implica más efectos secundarios, los medicamentos **complejos** tienen la mediana más baja (~4) y la menor varianza de todos los grupos. Los **tríos** tienen la mediana más alta (~7) y la mayor dispersión.

**Interpretación:** Las formulaciones complejas (5+ componentes) son altamente especializadas, desarrolladas para condiciones muy específicas con perfiles de seguridad controlados. En cambio, los monocomponentes y dúos incluyen fármacos de amplio espectro con indicaciones más variadas y, por tanto, perfiles de efectos secundarios más extensos.

**Outliers:** Los grupos mono y duo presentan numerosos outliers superiores (hasta 36 efectos), correspondiendo a medicamentos con perfiles de seguridad particularmente complejos, posiblemente quimioterápicos o inmunosupresores dentro del grupo de monocomponentes.

**Los tríos** presentan la mayor varianza (IQR más amplio), lo que sugiere que este grupo es el más heterogéneo del dataset: incluye tanto formulaciones simples como combinaciones farmacológicamente complejas.

---

## 6. Network Graph — Red de co-ocurrencia entre componentes activos

### Análisis

El grafo de red muestra los 15 componentes más frecuentes como nodos, conectados por aristas cuando co-ocurren en al menos 5 medicamentos. El tamaño del nodo es proporcional al número de conexiones (grado) y el grosor de la arista es proporcional a la frecuencia de co-ocurrencia.

**Tres clusters claramente separados:**

**Cluster antidiabético** (inferior derecho):
Conformado por Metformin, Glimepiride y Voglibose, con Metformin como el nodo de mayor tamaño del cluster. La conexión Metformin–Glimepiride es la de mayor grosor del grafo completo (325 co-ocurrencias). Este cluster también tiene una conexión débil hacia Methylcobalamin, reflejando el uso frecuente de vitamina B12 en pacientes diabéticos con neuropatía.

**Cluster antihipertensivo** (superior izquierdo):
Conformado por Telmisartan, Amlodipine, Hydrochlorothiazide y Montelukast. Hydrochlorothiazide actúa como nodo central con conexiones hacia Telmisartan y Amlodipine. La presencia de Montelukast en este cluster es una conexión débil que podría reflejar comorbilidad entre hipertensión y asma.

**Cluster analgésico/respiratorio** (derecha):
Conformado por Paracetamol, Aceclofenac, Phenylephrine y Chlorpheniramine Maleate. Paracetamol es el nodo de mayor grado del cluster, conectado con Aceclofenac (analgésico combinado) y con Phenylephrine/Chlorpheniramine Maleate (descongestionantes para resfríos).

**Aislados:**
Methylcobalamin–Pregabalin y Ambroxol–Guaifenesin aparecen como pares aislados sin conexión a otros clusters, lo que confirma su especificidad terapéutica (neuropatía y mucólisis respiratoria respectivamente).

**Hallazgo estructural:** La separación clara entre clusters confirma que los componentes **no cruzan áreas terapéuticas** en las combinaciones del dataset. Esto es clínicamente coherente y valida la calidad del dataset.

---

## 7. Scatterplot — Valoración de usuarios según número de componentes

### Análisis

El scatterplot muestra la relación entre el número de componentes activos de cada medicamento y su porcentaje de valoraciones excelentes. Los puntos individuales están con jitter horizontal para evitar solapamiento, y la línea roja indica la media por grupo.

**Tendencia de la media (grupos 1 a 6):**

| N° componentes | Media aprox. (%) |
|---|---|
| 1 (mono) | 38% |
| 2 (duo) | 41% |
| 3 (trio) | 39% |
| 4 (cuádruple) | 35% |
| 5 (complejo) | 35% |
| 6 | 25% |

**Hallazgos principales:**

Los **dúos** tienen la mejor valoración promedio (~41%), superando incluso a los monocomponentes (~38%). Esto podría explicarse porque los dúos más frecuentes (como Glimepiride + Metformin o Levocetirizine + Montelukast) son terapias combinadas que ofrecen mejor control de la enfermedad que un solo componente, generando mayor satisfacción del paciente.

La **tendencia decreciente desde 2 hasta 6 componentes** sugiere que a mayor complejidad farmacológica, la experiencia del paciente tiende a ser más variable y el promedio de satisfacción decrece. Esto es consistente con el hecho de que medicamentos más complejos suelen usarse en estadios más avanzados de enfermedad, donde la experiencia clínica del paciente es intrínsecamente más difícil.

**Valores en 7, 8 y 9 componentes no son representativos** desde el punto de vista estadístico (7, 2 y 1 medicamentos respectivamente), por lo que la línea de media en esos puntos no refleja un patrón real sino la variabilidad de muestras muy pequeñas.

**Alta varianza en todos los grupos:** La dispersión vertical de los puntos en cada columna es muy amplia (de 0% a 100%), lo que indica que la valoración del usuario depende de muchos factores además del número de componentes.

---

## Síntesis general de hallazgos

| Pregunta del foco | Respuesta |
|---|---|
| ¿Qué pares son más frecuentes? | Glimepiride + Metformin (325), dominando con amplia ventaja |
| ¿Qué componentes co-ocurren más? | Metformin, Glimepiride y Voglibose forman el cluster antidiabético central |
| ¿Más componentes = más efectos secundarios? | No. Los complejos tienen menor mediana que mono, duo y trio |
| ¿Existen componentes hub? | Sí. Metformin (664 apariciones) es el hub absoluto del dataset |
| ¿La valoración varía con el número de componentes? | Sí, tendencia decreciente desde dúos hasta 6 componentes |

El análisis confirma que el dataset refleja principalmente el mercado farmacéutico para patologías crónicas de alta prevalencia: **diabetes tipo 2, hipertensión arterial y dolor crónico**, que dominan tanto los componentes individuales como las combinaciones más frecuentes.