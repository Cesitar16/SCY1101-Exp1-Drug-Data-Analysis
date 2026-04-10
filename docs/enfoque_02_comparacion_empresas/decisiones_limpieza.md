# Decisiones de limpieza - Enfoque 02 Comparacion por empresas

## Objetivo

Preparar el dataset para comparar el mismo medicamento base entre distintas empresas, manteniendo la trazabilidad de las tres reviews, los efectos secundarios y la cobertura real de cada comparacion.

## Decisiones principales

### 1. Empresa de trabajo

- Se utiliza `Manufacturer` como base para la variable `empresa`.
- La limpieza aplicada consiste en normalizar espacios sobrantes.
- No se fuerza un nuevo casing para no alterar siglas o nombres comerciales.

### 2. Composicion comparable entre empresas

- Se construye una clave canonica `composition_key`.
- Esta clave conserva ingredientes y dosis.
- Se normalizan espacios y formato de parentesis.
- Los componentes se ordenan alfabeticamente para que:
  - `A (10mg) + B (5mg)` sea equivalente a `B (5mg) + A (10mg)`.

## Criterio de comparacion

- Solo se consideran comparables entre empresas las composiciones con `shared_company_count >= 2`.
- Si cambia la dosis, la composicion ya no se considera la misma formula.
- Esto evita mezclar medicamentos parecidos pero no equivalentes.
- No se construye un ranking global de empresas.
- La unidad principal de comparacion es `composition_key + empresa`.

## Cobertura y representatividad

- Cada comparacion debe reportar:
  - `n_medicamentos`: cuantos registros aporta una empresa dentro de una composicion.
  - `n_empresas`: cuantas empresas comparten la misma composicion.
  - `n_registros`: cuantos registros totales existen para esa composicion.
- Se etiqueta la cobertura de cada grupo empresa-composicion con `company_record_coverage`:
  - `baja`: 1 registro
  - `media`: 2 a 3 registros
  - `alta`: 4 o mas registros
- Se etiqueta la fortaleza global de cada composicion compartida con `comparison_strength`:
  - `debil`: cobertura limitada
  - `media`: comparacion exploratoria mas firme
  - `fuerte`: mejor cobertura relativa dentro del dataset
- Estas etiquetas describen cobertura del dataset, no significancia estadistica.

## Variables derivadas del enfoque

- `num_effects`: aproximacion al numero de efectos secundarios listados.
- `num_componentes`: cantidad de componentes declarados en la composicion.
- `review_sum`: suma de `Excellent Review %`, `Average Review %` y `Poor Review %`.
- `review_sum_valid`: valida si la suma de reviews es 100.
- `shared_company_count`: numero de empresas que comercializan la misma composicion canonica.
- `shared_company_composition`: bandera booleana para composiciones comparables.
- `company_record_coverage`: nivel de respaldo de cada comparacion empresa-composicion.
- `comparison_strength`: nivel de cobertura de cada composicion compartida.

## Alcance de esta limpieza

- Esta etapa no afirma causalidad farmacologica.
- Las diferencias observadas entre empresas se interpretan como variaciones del dataset y no como prueba definitiva de mejor o peor fabricacion.
- El dataset no incluye `n_reviews`, por lo que los porcentajes de reviews deben interpretarse como tendencia descriptiva y no como evidencia estadisticamente concluyente.
- El analisis posterior debe tratar estos resultados como evidencia exploratoria y priorizar composiciones con mayor cobertura.
