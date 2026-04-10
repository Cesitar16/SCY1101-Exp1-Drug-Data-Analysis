# Analisis de Visualizaciones y Tablas
## Foco: Comparacion por Empresa / Manufacturer
**Dataset:** Medicine_Details.csv | 11,741 registros (post-limpieza) | DuocUC 2026

---

## 1. Barplot - Top fabricantes por cantidad de medicamentos

### Descripcion tecnica
Grafico de barras horizontales que ordena a los fabricantes segun la cantidad de medicamentos presentes en el dataset. Funciona como un proxy de presencia relativa dentro de la muestra.

### Tabla de referencia

| Posicion | Empresa | Medicamentos | Share proxy |
|---|---|---:|---:|
| 1 | Sun Pharmaceutical Industries Ltd | 819 | 6.98% |
| 2 | Intas Pharmaceuticals Ltd | 648 | 5.52% |
| 3 | Cipla Ltd | 569 | 4.85% |
| 4 | Torrent Pharmaceuticals Ltd | 441 | 3.76% |
| 5 | Lupin Ltd | 432 | 3.68% |
| 6 | Mankind Pharma Ltd | 336 | 2.86% |
| 7 | Zydus Cadila | 326 | 2.78% |
| 8 | Alkem Laboratories Ltd | 325 | 2.77% |
| 9 | Macleods Pharmaceuticals Pvt Ltd | 316 | 2.69% |
| 10 | Abbott | 279 | 2.38% |

### Analisis

El dataset contiene `759` empresas distintas, pero la distribucion es muy desigual. La mediana de medicamentos por empresa es apenas `2`, lo que confirma una cola larga de fabricantes pequenos y un grupo reducido de actores con volumen suficiente para comparaciones mas estables.

Las 10 empresas mas grandes concentran una fraccion relevante del dataset, pero ninguna domina por si sola. La mayor, Sun Pharmaceutical Industries Ltd, representa menos del `7%` del total post-limpieza. Esto sugiere un mercado atomizado dentro de la muestra, con varios laboratorios medianos y grandes compitiendo simultaneamente.

### Implicacion para el analisis

La comparacion por empresa debe incorporar filtros minimos de volumen. Sin un umbral como `>= 10` medicamentos, los rankings se llenan de casos pequenos con alta varianza.

---

## 2. Ranking de reputacion por empresa

### Descripcion tecnica
Tabla y barplot basados en `review_balance_mean`, definido como:

`review_balance = Excellent Review % - Poor Review %`

Se calcula por empresa y se ordena de mayor a menor, exigiendo un minimo de 10 medicamentos para evitar rankings inestables.

### Tabla de referencia

| Posicion | Empresa | Medicamentos | Excellent promedio | Poor promedio | Review balance |
|---|---|---:|---:|---:|---:|
| 1 | AstraZeneca | 21 | 57.52 | 11.81 | 45.71 |
| 2 | Jubilant Life Sciences | 15 | 55.20 | 15.73 | 39.47 |
| 3 | Eli Lilly and Company India Pvt Ltd | 18 | 45.94 | 11.06 | 34.89 |
| 4 | Merck Ltd | 22 | 47.68 | 13.59 | 34.09 |
| 5 | Novartis India Ltd | 41 | 47.41 | 13.66 | 33.76 |

### Analisis

Las empresas mejor rankeadas no coinciden con las mas grandes del dataset. Esto es importante: el volumen no parece ser el principal predictor de reputacion promedio. El liderazgo por calidad esta repartido entre empresas de tamano medio, no necesariamente entre los fabricantes con mas productos.

La diferencia entre `Excellent` y `Poor` en este top es amplia. AstraZeneca, por ejemplo, muestra una brecha de casi `46` puntos, lo que indica una percepcion notablemente favorable en la mezcla de reviews de sus medicamentos.

### Implicacion para el analisis

El ranking por reputacion debe leerse separado del ranking por volumen. El enfoque 2 gana fuerza precisamente porque permite mostrar que "empresa grande" y "empresa mejor valorada" no son sinonimos.

---

## 3. Boxplot - Distribucion de `review_balance` en las empresas mas grandes

### Descripcion tecnica
Boxplot aplicado a las 10 empresas con mas medicamentos del dataset. Cada caja resume la distribucion de `review_balance` de todos los productos de esa empresa.

### Analisis

Este grafico agrega una dimension que el ranking promedio no captura: la consistencia interna. Una empresa puede tener buen promedio y aun asi ser muy irregular si combina productos excelentes con otros muy mal evaluados.

En el dataset se observa que casi todas las empresas grandes mantienen la mediana de `review_balance` por encima de `0`, lo que indica una tendencia general a tener mas reviews excelentes que malas. Sin embargo, la dispersion cambia bastante entre fabricantes.

Ejemplos de empresas mas consistentes con minimo 10 medicamentos:

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

### Implicacion para el analisis

Este grafico justifica separar dos conceptos:

- reputacion promedio
- estabilidad del portafolio

En presentacion, este punto es clave: no basta con mostrar quien "gana"; tambien importa cuan predecible es la calidad dentro de cada laboratorio.

---

## 4. Scatterplot - Correlacion entre tamano de empresa y buenas valoraciones

### Descripcion tecnica
Scatterplot con:

- eje X: cantidad de medicamentos por empresa
- eje Y: `% Excellent Review` promedio
- linea de tendencia lineal
- correlacion de Pearson

### Resultado principal

- Correlacion entre cantidad de medicamentos y `% Excellent` promedio: `r = 0.019`
- Correlacion entre cantidad de medicamentos y `review_balance_mean`: `r = 0.085`

### Analisis

Ambas correlaciones son practicamente nulas. El tamano de la empresa dentro del dataset no explica ni una mayor proporcion de reviews excelentes ni un mejor balance reputacional.

Visualmente, las empresas grandes se concentran en una zona media del grafico, mientras que muchas empresas pequenas presentan valores extremos, tanto altos como bajos. Eso sugiere que las empresas mas grandes pueden ser mas estables, pero no necesariamente mejores.

### Implicacion para el analisis

El enfoque 2 entrega aqui un insight fuerte:

**la escala no garantiza calidad**

Ese hallazgo descarta una lectura simplista del dataset y refuerza la necesidad de comparar empresas dentro de composiciones concretas.

---

## 5. Tabla - Misma composicion en varias empresas

### Descripcion tecnica
La tabla `composition_company_comparison` agrupa por `composition_key` y `manufacturer_clean`, calculando el desempeno medio de cada fabricante sobre la misma composicion.

### Alcance analitico

- Composiciones presentes en al menos 2 empresas: `940`
- Composiciones presentes en al menos 3 empresas: `660`

Esto convierte al enfoque 2 en el foco mas potente del proyecto, porque habilita comparaciones casi "controladas": la composicion es la misma, pero el fabricante cambia.

### Hallazgos robustos

Si se filtran composiciones con al menos 3 fabricantes y al menos 2 observaciones por fabricante, aparecen gaps muy fuertes:

| Composicion | Empresas | Medicamentos totales | Gap de review balance |
|---|---:|---:|---:|
| Dabigatran Etexilate | 7 | 16 | 160.83 |
| Cefpodoxime Proxetil | 8 | 28 | 143.00 |
| Ramipril | 9 | 20 | 141.50 |
| Glimepiride + Metformin + Pioglitazone | 22 | 53 | 140.17 |
| Glimepiride + Metformin | 34 | 155 | 133.50 |

### Analisis

El caso de `Glimepiride + Metformin` es especialmente importante porque combina:

- alto volumen
- alta presencia entre empresas
- gran brecha de reputacion entre fabricantes

Ese patron sustenta el insight central del enfoque:

**no solo importa que se fabrica, sino quien lo fabrica**

### Implicacion para el analisis

Si hubiera que elegir un unico subestudio para defender el enfoque 2, este deberia ser el principal.

---

## 6. Seguridad por empresa - side effects y reputacion

### Descripcion tecnica
La tabla `manufacturer_side_effect_summary` resume por empresa:

- promedio de side effects por medicamento
- mediana de side effects
- `Poor Review %` promedio
- `review_balance_mean`
- cantidad de efectos distintos observados

### Tabla de referencia

| Empresa | Medicamentos | Side effects promedio | Poor promedio | Review balance |
|---|---:|---:|---:|---:|
| Serdia Pharmaceuticals India Pvt Ltd | 10 | 11.20 | 23.10 | 14.20 |
| Natco Pharma Ltd | 23 | 10.48 | 19.57 | 26.78 |
| Mylan Pharmaceuticals Pvt Ltd - A Viatris Company | 13 | 10.46 | 23.38 | 17.69 |
| Arinna Lifescience Pvt Ltd | 22 | 10.18 | 19.68 | 27.05 |
| Icon Life Sciences | 71 | 9.92 | 24.03 | 20.25 |

### Analisis

El volumen de efectos secundarios reportados no invalida automaticamente la reputacion de una empresa. Hay fabricantes con carga alta de side effects y aun asi con balance reputacional positivo. Esto refuerza una idea que tambien aparece en el enfoque 3: la cantidad de efectos listados no debe leerse como una penalizacion lineal sobre la valoracion del usuario.

### Implicacion para el analisis

La comparacion por empresa gana profundidad cuando cruza reputacion y seguridad. Este bloque funciona mejor como complemento del ranking principal, no como ranking aislado.

---

## 7. Heatmap - Especializacion terapeutica por empresa

### Descripcion tecnica
El heatmap muestra la proporcion interna de areas terapeuticas por fabricante, usando `Uses` transformado a categorias amplias.

### Ejemplos de alta especializacion

| Empresa | Area dominante | Share interno |
|---|---|---:|
| Eli Lilly and Company India Pvt Ltd | Diabetes / Endocrine | 100.00% |
| Novo Nordisk India Pvt Ltd | Diabetes / Endocrine | 96.77% |
| Boehringer Ingelheim | Diabetes / Endocrine | 76.92% |
| Eskon Pharma | Dermatology | 64.71% |
| Tablets India Limited | Respiratory / Allergy | 58.33% |

### Analisis

No todas las empresas compiten en el mismo espacio terapeutico. Algunas operan como laboratorios generalistas, mientras otras muestran una concentracion fuerte en un nicho especifico. Esto explica por que comparar empresas solo por promedio global puede ser engañoso: estan jugando en segmentos terapeuticos distintos.

### Implicacion para el analisis

La especializacion es una variable de contexto obligatoria cuando se interpretan rankings por empresa. Ayuda a evitar conclusiones simplistas del tipo "empresa A es mejor que empresa B" sin considerar que sus portafolios son diferentes.

---

## 8. Scatterplot - Balance calidad vs cantidad

### Descripcion tecnica
Scatterplot con:

- eje X: cantidad de medicamentos en el dataset
- eje Y: `review_balance_mean`
- color: `Poor Review %` promedio
- tamaño del punto: `% Excellent` promedio

### Analisis

Este grafico resume cuatro variables en una sola vista. Permite ubicar empresas en cuadrantes utiles:

- grandes y fuertes
- grandes pero promedio
- pequenas premium
- pequenas y debiles

El patron general confirma lo mismo que el scatter de correlacion: las empresas grandes no dominan por calidad promedio. Varias pequenas y medianas obtienen balances reputacionales superiores, mientras las grandes se concentran mas cerca del promedio.

### Implicacion para el analisis

Es el mejor grafico para cerrar el enfoque 2, porque sintetiza volumen, calidad y riesgo reputacional en un solo plano.

---

## 9. Top medicamentos por empresa

### Descripcion tecnica
La tabla `top_medicines_by_manufacturer` identifica los mejores medicamentos de cada empresa elegible, usando `review_balance`, `% Excellent` y `% Poor`.

### Analisis

Este bloque es util para pasar del nivel empresa al nivel producto. Permite responder:

- cual es el producto estrella de cada laboratorio
- si el ranking de empresa depende de pocos medicamentos sobresalientes
- si una empresa tiene al menos un activo claramente competitivo

### Implicacion para el analisis

Este output es especialmente util para entrega o defensa, porque traduce el analisis agregado a ejemplos concretos y faciles de comunicar.

---

## Sintesis general del enfoque 2

| Pregunta del foco | Respuesta |
|---|---|
| Quien domina en volumen dentro del dataset | Sun, Intas y Cipla lideran por cantidad de medicamentos |
| Las empresas mas grandes son las mejor valoradas | No. El volumen y la reputacion no muestran correlacion relevante |
| El ranking promedio basta para comparar empresas | No. Tambien hay que mirar consistencia interna |
| La misma composicion cambia segun empresa | Si. Existen gaps muy altos entre fabricantes para varias composiciones |
| Hay especializacion por laboratorio | Si. Varias empresas se concentran claramente en nichos terapeuticos |

### Conclusion

El enfoque 2 es el foco mas fuerte del proyecto desde la perspectiva de negocio. Su mayor fortaleza es que permite comparar fabricantes sobre una misma composicion, separando claramente tres dimensiones:

- escala
- reputacion
- consistencia

El hallazgo central es claro:

**la calidad percibida no depende del tamaño del fabricante, sino de como rinde cada empresa dentro de composiciones concretas.**
