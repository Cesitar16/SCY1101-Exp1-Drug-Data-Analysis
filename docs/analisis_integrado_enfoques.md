# Analisis Integrado de los Tres Enfoques

## Contexto

Este documento consolida los hallazgos mas relevantes de los tres focos del proyecto sobre `Medicine_Details.csv`.

- Dataset raw: `11,825` filas y `9` columnas.
- Duplicados completos detectados: `84`.
- Base post-limpieza usada en enfoques 1 y 2: `11,741` registros.
- Nota: el pipeline actual del enfoque 3 trabaja sobre `11,825` filas porque su limpieza no elimina duplicados completos antes de derivar columnas.

## Resumen Ejecutivo

- El dataset esta dominado por patologias cronicas de alta prevalencia, especialmente diabetes, hipertension, dolor e infecciones.
- El foco mas fuerte desde negocio y comparabilidad es el enfoque 2: hay `940` composiciones presentes en al menos 2 empresas y `660` presentes en al menos 3.
- Ni el numero de componentes ni la cantidad de efectos secundarios muestran por si solos una relacion lineal fuerte con peores valoraciones.
- El tamano de la empresa en el dataset tampoco garantiza mejor reputacion: la correlacion entre cantidad de medicamentos y `% Excellent` promedio es casi nula (`r = 0.019`).

---

## Enfoque 1: Combinaciones de Componentes

### Pregunta del foco

Entender como se estructuran las formulaciones del dataset, que componentes aparecen con mayor frecuencia y que combinaciones dominan el mercado representado.

### Hallazgos principales

#### 1. El mercado esta fuertemente concentrado en mono y duo componentes

| n_componentes | Medicamentos | Porcentaje |
|---|---:|---:|
| 1 | 7,019 | 59.78% |
| 2 | 3,569 | 30.40% |
| 3 | 929 | 7.91% |
| 4 | 147 | 1.25% |
| 5 o mas | 77 | 0.66% |

Interpretacion:

- El `90.18%` del dataset esta en formulaciones de 1 o 2 componentes.
- Los medicamentos de 5 o mas componentes existen, pero son marginales y no deberian dominar conclusiones generales.

#### 2. Los hubs del dataset estan en diabetes e hipertension

Top 10 componentes mas frecuentes:

| Componente | Medicamentos |
|---|---:|
| Metformin | 664 |
| Glimepiride | 379 |
| Telmisartan | 379 |
| Paracetamol | 359 |
| Amlodipine | 314 |
| Montelukast | 224 |
| Methylcobalamin | 214 |
| Pregabalin | 214 |
| Metoprolol Succinate | 209 |
| Rosuvastatin | 209 |

Interpretacion:

- `Metformin` es el hub dominante del dataset.
- El peso conjunto de `Metformin`, `Glimepiride`, `Telmisartan`, `Amlodipine` y `Rosuvastatin` apunta a un mercado centrado en diabetes, hipertension y riesgo cardiovascular.

#### 3. Las combinaciones mas frecuentes tambien se concentran en enfermedades cronicas

Top 10 pares:

| Par de componentes | Frecuencia |
|---|---:|
| Glimepiride + Metformin | 325 |
| Levocetirizine + Montelukast | 124 |
| Metformin + Voglibose | 124 |
| Methylcobalamin + Pregabalin | 122 |
| Amoxycillin + Clavulanic Acid | 97 |
| Ambroxol + Guaifenesin | 91 |
| Amlodipine + Telmisartan | 90 |
| Aceclofenac + Paracetamol | 88 |
| Metformin + Pioglitazone | 87 |
| Glimepiride + Voglibose | 86 |

Interpretacion:

- `Glimepiride + Metformin` domina con amplia ventaja y consolida el cluster antidiabetico.
- Tambien aparecen clusters claros en respiratorio, gastrointestinal, analgesia e hipertension.

#### 4. La mejor valoracion promedio aparece en los duos, no en las formulaciones mas simples ni en las mas complejas

Promedio de `Excellent Review %` por numero de componentes:

| n_componentes | Excellent promedio |
|---|---:|
| 1 | 37.28 |
| 2 | 40.98 |
| 3 | 38.90 |
| 4 | 35.77 |
| 5 | 35.59 |
| 6 | 25.38 |

Interpretacion:

- Los duos son el punto mas fuerte del dataset en valoracion de usuarios.
- La complejidad adicional no mejora la percepcion; desde 3 componentes en adelante la media tiende a bajar.
- Los grupos 7, 8 y 9 componentes existen, pero son demasiado pequenos para soportar conclusiones robustas.

#### 5. Mas componentes no implica automaticamente mas efectos secundarios

Promedio aproximado de efectos listados por numero de componentes:

| n_componentes | Efectos promedio |
|---|---:|
| 1 | 6.92 |
| 2 | 6.92 |
| 3 | 7.27 |
| 4 | 6.22 |
| 5 | 4.55 |
| 6 | 2.56 |

Interpretacion:

- El grupo de 3 componentes es el mas cargado en efectos promedio.
- Las formulaciones mas complejas no muestran un aumento lineal de efectos; de hecho, en este dataset los grupos complejos tienden a bajar.
- Esto sugiere que el numero de ingredientes por si solo no explica el perfil de seguridad.

### Lectura del enfoque 1

El enfoque 1 muestra que el dataset esta estructurado alrededor de pocos hubs terapeuticos y que las combinaciones mas importantes son clinicamente coherentes. Tambien sugiere que las formulaciones dobles concentran buena parte del valor del dataset: tienen volumen, co-ocurrencia clara y mejores valoraciones promedio que otros tamanos.

---

## Enfoque 2: Comparacion por Empresa

### Pregunta del foco

Comparar fabricantes segun volumen, reputacion, consistencia interna y desempeno sobre una misma composicion.

### Hallazgos principales

#### 1. Hay muchas empresas, pero pocas con volumen suficiente

- Empresas unicas: `759`.
- Mediana de medicamentos por empresa: `2`.
- Empresas con `10` o mas medicamentos: `150`.

Interpretacion:

- La comparacion entre empresas necesita filtros minimos de volumen.
- Sin filtrar, el ranking se llena de casos pequenos y extremos.

#### 2. Las empresas mas grandes no son las mejor rankeadas por reputacion

Top por volumen dentro del dataset:

| Empresa | Medicamentos | Share proxy |
|---|---:|---:|
| Sun Pharmaceutical Industries Ltd | 819 | 6.98% |
| Intas Pharmaceuticals Ltd | 648 | 5.52% |
| Cipla Ltd | 569 | 4.85% |
| Torrent Pharmaceuticals Ltd | 441 | 3.76% |
| Lupin Ltd | 432 | 3.68% |

Top por reputacion promedio (`review_balance_mean`, minimo 10 medicamentos):

| Empresa | Medicamentos | Excellent promedio | Poor promedio | Review balance |
|---|---:|---:|---:|---:|
| AstraZeneca | 21 | 57.52 | 11.81 | 45.71 |
| Jubilant Life Sciences | 15 | 55.20 | 15.73 | 39.47 |
| Eli Lilly and Company India Pvt Ltd | 18 | 45.94 | 11.06 | 34.89 |
| Merck Ltd | 22 | 47.68 | 13.59 | 34.09 |
| Novartis India Ltd | 41 | 47.41 | 13.66 | 33.76 |

Interpretacion:

- Las empresas de mayor volumen no dominan automaticamente la reputacion.
- El liderazgo por calidad promedio esta mas repartido y no coincide con el liderazgo por tamano.

#### 3. El tamano de la empresa no explica las buenas valoraciones

- Correlacion entre cantidad de medicamentos y `% Excellent` promedio: `r = 0.019`.
- Correlacion entre cantidad de medicamentos y `review_balance_mean`: `r = 0.085`.

Interpretacion:

- Ambas correlaciones son practicamente nulas.
- Tener mas medicamentos en el dataset no implica mejores reviews promedio.

#### 4. La consistencia interna cambia mucho entre empresas

Ejemplos de empresas mas consistentes (menor desviacion en `review_balance`, minimo 10 medicamentos):

| Empresa | Medicamentos | Review balance medio | Desv. estandar |
|---|---:|---:|---:|
| Boehringer Ingelheim | 13 | 32.08 | 10.62 |
| Alcon Laboratories | 11 | 18.45 | 15.92 |
| Eli Lilly and Company India Pvt Ltd | 18 | 34.89 | 22.48 |

Ejemplos de empresas mas irregulares:

| Empresa | Medicamentos | Review balance medio | Desv. estandar |
|---|---:|---:|---:|
| Dios Lifesciences Pvt Ltd | 11 | 33.45 | 76.04 |
| Overseas Healthcare Pvt Ltd | 10 | -22.00 | 74.05 |
| Dr. Johns Laboratories Pvt Ltd | 14 | -9.79 | 70.07 |

Interpretacion:

- Un buen promedio no garantiza estabilidad.
- Algunas empresas combinan productos muy bien valorados con otros muy mal valorados.

#### 5. Este enfoque es el mas fuerte del proyecto porque hay muchas composiciones comparables entre empresas

- Composiciones presentes en al menos 2 empresas: `940`.
- Composiciones presentes en al menos 3 empresas: `660`.

Interpretacion:

- El dataset permite comparar fabricantes sobre una misma base farmacologica.
- Eso convierte al enfoque 2 en el foco mas potente para extraer insights de negocio.

#### 6. En varias composiciones el gap entre empresas es muy alto

En una version mas robusta del analisis, filtrando composiciones con al menos 3 fabricantes y al menos 2 observaciones por fabricante, aparecen diferencias fuertes:

| Composicion | Empresas | Medicamentos totales | Gap de review balance |
|---|---:|---:|---:|
| Dabigatran Etexilate | 7 | 16 | 160.83 |
| Cefpodoxime Proxetil | 8 | 28 | 143.00 |
| Ramipril | 9 | 20 | 141.50 |
| Glimepiride + Metformin + Pioglitazone | 22 | 53 | 140.17 |
| Glimepiride + Metformin | 34 | 155 | 133.50 |

Interpretacion:

- No solo importa la composicion; tambien importa quien la fabrica.
- El caso de `Glimepiride + Metformin` es especialmente valioso porque combina alto volumen y amplia presencia entre empresas.

#### 7. Tambien hay especializacion por empresa

Ejemplos de alta concentracion terapeutica:

| Empresa | Area dominante | Share interno |
|---|---|---:|
| Eli Lilly and Company India Pvt Ltd | Diabetes / Endocrine | 100.00% |
| Novo Nordisk India Pvt Ltd | Diabetes / Endocrine | 96.77% |
| Boehringer Ingelheim | Diabetes / Endocrine | 76.92% |
| Eskon Pharma | Dermatology | 64.71% |
| Tablets India Limited | Respiratory / Allergy | 58.33% |

Interpretacion:

- Algunas empresas se comportan como especialistas y no como portafolios generales.
- Esa especializacion ayuda a explicar por que empresas de volumen parecido pueden mostrar perfiles de reputacion diferentes.

### Lectura del enfoque 2

El enfoque 2 es el mas accionable desde negocio. Permite separar volumen de calidad, medir consistencia interna y, sobre todo, comparar la misma composicion entre distintos fabricantes. El hallazgo mas fuerte es que la ventaja competitiva no se explica por escala: se explica mejor por calidad relativa dentro de composiciones concretas.

---

## Enfoque 3: Efectos Secundarios por Componente

### Pregunta del foco

Estudiar la frecuencia de efectos secundarios, su co-ocurrencia y la relacion entre seguridad percibida, reviews y componentes activos.

### Hallazgos principales

#### 1. Los efectos secundarios mas frecuentes son generalistas

Top 10 efectos secundarios:

| Efecto | Medicamentos |
|---|---:|
| nausea | 6,216 |
| headache | 5,374 |
| diarrhea | 4,553 |
| dizziness | 4,064 |
| vomiting | 3,499 |
| abdominal pain | 1,883 |
| sleepiness | 1,791 |
| constipation | 1,699 |
| fatigue | 1,520 |
| stomach pain | 1,426 |

Interpretacion:

- Predominan efectos muy transversales a multiples familias farmacologicas.
- El dataset captura bien sintomas generales, pero no solo efectos hiper-especificos.

#### 2. La carga media de efectos listados es moderada, con cola larga

Estadisticas de `n_efectos` por medicamento:

| Medida | Valor |
|---|---:|
| Media | 6.92 |
| Mediana | 6.00 |
| P25 | 4.00 |
| P75 | 9.00 |
| Maximo | 36.00 |

Interpretacion:

- La mayoria de los medicamentos lista entre 4 y 9 efectos.
- Existen casos extremos, pero no son la norma.

#### 3. Algunos componentes concentran mucha diversidad de efectos

Top 10 componentes por cantidad de efectos distintos:

| Componente | Efectos distintos |
|---|---:|
| menthol | 67 |
| amlodipine | 60 |
| diclofenac | 56 |
| telmisartan | 55 |
| chlorpheniramine maleate | 54 |
| phenylephrine | 53 |
| paracetamol | 53 |
| hydrochlorothiazide | 52 |
| ambroxol | 52 |
| montelukast | 49 |

Interpretacion:

- Los componentes mas extendidos en el dataset tienden a arrastrar un catalogo mas amplio de efectos.
- Eso puede reflejar tanto diversidad terapeutica como mayor documentacion de seguridad.

#### 4. No hay evidencia fuerte de que mas efectos listados impliquen peores reviews

- Correlacion entre `n_efectos` y `Poor Review %`: `r = -0.040`.
- Correlacion entre `n_efectos` y `Excellent Review %`: `r = 0.036`.

Promedios por tramos de efectos:

| Tramo de efectos | Excellent promedio | Poor promedio |
|---|---:|---:|
| 1-3 | 36.92 | 27.25 |
| 4-6 | 37.95 | 26.44 |
| 7-9 | 39.81 | 24.31 |
| 10-12 | 38.87 | 25.49 |
| 13+ | 40.23 | 23.78 |

Interpretacion:

- La relacion lineal es practicamente nula.
- En este dataset, listar mas efectos no se traduce automaticamente en peores valoraciones.
- Posible explicacion: el conteo de efectos refleja cobertura documental, no necesariamente severidad clinica.

#### 5. Los componentes con mejor o peor perfil de reviews deben leerse con umbral minimo

Si se filtran componentes con al menos `100` observaciones, aparecen perfiles mas estables:

Mejores por `% Excellent`:

| Componente | Excellent promedio | Poor promedio | Observaciones |
|---|---:|---:|---:|
| ramipril | 58.12 | 13.69 | 465 |
| enalapril | 57.47 | 12.03 | 112 |
| desvenlafaxine | 57.05 | 16.67 | 189 |
| lisinopril | 55.50 | 10.94 | 129 |
| lacosamide | 54.94 | 10.17 | 144 |

Peores por `% Poor`:

| Componente | Poor promedio | Excellent promedio | Observaciones |
|---|---:|---:|---:|
| letrozole | 43.33 | 29.83 | 108 |
| deflazacort | 42.85 | 27.02 | 133 |
| lactulose | 42.08 | 25.54 | 128 |
| mirabegron | 40.36 | 32.97 | 174 |
| ethamsylate | 39.62 | 28.16 | 175 |

Interpretacion:

- Con umbral minimo, el enfoque deja de estar dominado por componentes raros con 1 sola observacion.
- El perfil de reviews varia mucho entre componentes, pero no de forma reducible al numero de efectos reportados.

### Lectura del enfoque 3

El enfoque 3 es fuerte para explorar seguridad y diversidad de efectos, pero menos concluyente para explicar reputacion por si sola. Sirve mejor como enfoque complementario: ayuda a contextualizar la experiencia del usuario, pero no demuestra que mas efectos listados impliquen peor valoracion.

---

## Sintesis Comparada de los Tres Enfoques

### Que nos dicen juntos

1. El dataset esta dominado por clusters terapeuticos claros.
   - Diabetes, hipertension, dolor, respiratorio e infecciones aparecen tanto en componentes frecuentes como en pares frecuentes y especializaciones por empresa.

2. La complejidad farmacologica no empeora automaticamente la experiencia del usuario.
   - Enfoque 1: los duos tienen la mejor media de `% Excellent`.
   - Enfoque 3: el numero de efectos secundarios listados no muestra relacion fuerte con peores reviews.

3. La empresa importa, pero no por tamano.
   - Enfoque 2 muestra que el volumen no correlaciona con mejores valoraciones.
   - La ventaja competitiva aparece mejor al comparar la misma composicion entre empresas.

4. El mejor insight transversal del proyecto es combinacion + fabricante.
   - Enfoque 1 identifica las formulaciones dominantes.
   - Enfoque 2 muestra que esas mismas formulaciones pueden rendir muy distinto segun empresa.
   - Enfoque 3 aporta la capa de seguridad para enriquecer esa comparacion.

### Foco mas fuerte para presentacion final

Si hubiera que priorizar un unico foco para defensa o entrega, la recomendacion es:

1. Enfoque 2 como eje principal.
2. Enfoque 1 como contexto estructural.
3. Enfoque 3 como capa complementaria de seguridad.

Razon:

- El enfoque 2 permite un insight de negocio mas claro.
- El enfoque 1 explica por que ciertas composiciones dominan.
- El enfoque 3 agrega profundidad sin convertirse en la unica explicacion causal.

---

## Recomendaciones para la siguiente iteracion

1. Estandarizar la eliminacion de duplicados en los tres enfoques para que todas las bases comparen exactamente el mismo universo.
2. En enfoque 2, fijar umbrales minimos para comparacion por composicion.
   - Recomendado: minimo 3 fabricantes por composicion y minimo 2 registros por fabricante.
3. En enfoque 3, reportar siempre resultados por componente con umbral minimo de observaciones.
4. Exportar tablas finales a `outputs/tables/` para dejar trazabilidad de los rankings mas importantes.
5. Si se quiere una comparacion mas estricta en enfoque 2, pasar de `composition_key` a `Composition` exacta para controlar dosis.

---

## Conclusion General

El proyecto muestra un dataset coherente, con patrones claros y varios niveles de analisis utiles. El hallazgo mas valioso es que la calidad percibida no depende simplemente de tener mas medicamentos, mas componentes o mas efectos secundarios listados. La senal mas fuerte aparece cuando se compara una misma composicion entre empresas: ahi es donde el dataset entrega el insight mas defendible y mas cercano a una conclusion de negocio real.
