# Decisiones de Limpieza Comparadas

## Analisis de las 3 limpiezas implementadas en el proyecto

Este documento compara las decisiones de limpieza tomadas en los tres enfoques del proyecto. La idea central es mostrar que la limpieza no fue generica ni igual para todos los casos: cada pipeline limpio el dataset en funcion de la pregunta analitica que debia responder.

## Resumen ejecutivo

Los tres enfoques parten del mismo dataset raw `Medicine_Details.csv` con `11,825` filas y `9` columnas. En los tres casos se eliminaron `84` duplicados exactos, dejando `11,741` registros. A partir de ahi, cada limpieza se separa segun su foco:

- **Enfoque 1** prioriza convertir `Composition` en una estructura estable para estudiar combinaciones de componentes.
- **Enfoque 2** prioriza normalizar fabricante, composicion, usos y reviews para comparar empresas.
- **Enfoque 3** prioriza extraer componentes y parsear `Side_effects` para construir relaciones componente-efecto.

La decision clave transversal fue esta: **no se limpiaron los datos "por limpiar", sino para volver comparables las variables que cada enfoque necesitaba analizar**.

## Comparacion general

| Enfoque | Pregunta principal | Filas finales | Columnas finales | Decision de limpieza dominante |
|---|---|---:|---:|---|
| 1. Combinaciones de Componentes | Que tipos de combinaciones de principios activos existen | 11,741 | 13 | Normalizar `Composition` y extraer componentes sin dosis |
| 2. Comparacion por Empresa | Si el fabricante influye en reputacion, consistencia y seguridad | 11,741 | 19 | Normalizar fabricante y construir claves comparables por composicion |
| 3. Efectos Secundarios por Componentes | Que componentes se asocian a que efectos secundarios | 11,741 | 16 | Parsear `Side_effects` y transformar texto libre en listas analizables |

## Decision comun a los 3 enfoques

### Eliminar solo duplicados exactos

En los tres pipelines se aplico `drop_duplicates()` sobre el dataset completo.

**Por que se hizo**

- Un duplicado exacto no aporta informacion nueva.
- Si se dejaba, inflaba conteos, frecuencias y asociaciones.
- Era una decision segura porque el registro repetido era identico en todas las columnas.

**Por que no se eliminaron duplicados parciales**

- Un mismo medicamento puede aparecer con distinta composicion, dosis o fabricante.
- En esos casos el registro no es ruido: representa una variante real del dataset.

**Impacto**

| Estado | Filas |
|---|---:|
| Raw | 11,825 |
| Limpio | 11,741 |
| Eliminadas | 84 |

## Enfoque 1: decisiones de limpieza

**Archivo fuente:** `src/enfoque_01_combinaciones_componentes/cleaning.py`

### 1. Normalizar `Composition`

Se limpiaron espacios sobrantes y se estandarizo el separador `+`.

**Por que**

- La columna `Composition` era la base del enfoque.
- Si los separadores venian con espacios inconsistentes, el `split("+")` posterior producia componentes mal parseados.
- Esta limpieza no cambia el significado del medicamento; solo vuelve confiable el parseo.

### 2. Extraer componentes sin dosis

Se removieron las dosis entre parentesis y se genero `components_list`.

**Por que**

- El enfoque 1 no busca comparar concentraciones, sino combinaciones de principios activos.
- Mantener la dosis habria fragmentado artificialmente combinaciones equivalentes.
- Ejemplo: `Paracetamol (500mg)` y `Paracetamol (650mg)` debian agruparse como el mismo componente.

### 3. Generar variables de complejidad

Se crearon:

- `components_list`
- `n_components`
- `size_category`
- `composition_anomaly`

**Por que**

- `n_components` permite medir el tamano de la combinacion.
- `size_category` traduce ese conteo a una categoria ordinal interpretable: `mono`, `duo`, `trio`, `cuadruple`, `complejo`.
- `composition_anomaly` marca registros problematicos sin eliminarlos automaticamente.

### 4. Marcar anomalias, no borrarlas

Si un registro quedaba con `n_components == 0`, se marcaba con `composition_anomaly`.

**Por que**

- Es mas riguroso marcar primero y decidir despues que eliminar automaticamente.
- La limpieza del enfoque 1 privilegia trazabilidad sobre agresividad.

### Lectura tecnica del enfoque 1

La limpieza del enfoque 1 esta pensada para convertir una columna textual cruda en una estructura semantica ordenable. La decision dominante no es "quitar ruido", sino **construir una representacion comparable de las composiciones**.

## Enfoque 2: decisiones de limpieza

**Archivo fuente:** `src/enfoque_02_comparacion_empresas/cleaning.py`

### 1. Validar columnas requeridas antes de limpiar

Antes de cualquier transformacion, el pipeline exige estas columnas:

- `Medicine Name`
- `Composition`
- `Uses`
- `Side_effects`
- `Manufacturer`
- `Excellent Review %`
- `Average Review %`
- `Poor Review %`

**Por que**

- El enfoque 2 cruza empresa, composicion, efectos, usos y reviews.
- Si falta alguna de esas columnas, el analisis deja de ser valido conceptualmente.

### 2. Normalizar texto en columnas clave

Se normalizaron:

- `Medicine Name`
- `Manufacturer`
- `Uses`
- `Side_effects`
- `Composition`

**Por que**

- `Manufacturer` es el eje del enfoque, por lo que cualquier diferencia de espacios o formato podia partir artificialmente una empresa en dos.
- `Uses` y `Side_effects` venian como texto libre y debian quedar listos para derivar variables nuevas.
- `Composition` necesitaba separadores consistentes para extraer ingredientes.

### 3. Convertir reviews a numerico

Se aplico `pd.to_numeric(..., errors="coerce")` a:

- `Excellent Review %`
- `Average Review %`
- `Poor Review %`

**Por que**

- Las tres columnas de reviews son el corazon del ranking de reputacion.
- Sin convertirlas a numerico no era seguro calcular promedios, balances ni correlaciones.

### 4. Construir variables derivadas orientadas a empresa

Se crearon:

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

**Por que**

- `manufacturer_clean` asegura agrupacion consistente por empresa.
- `composition_key` permite comparar la misma base farmacologica entre distintos laboratorios.
- `side_effects_list` y `therapeutic_areas` convierten texto libre en estructuras explotables.
- `review_balance` resume reputacion en una sola metrica interpretable.

### 5. Mantener los nombres legibles

A diferencia del enfoque 3, aqui no se baja todo a minusculas visibles para analisis final. `manufacturer_clean` conserva una forma legible.

**Por que**

- El enfoque 2 produce rankings, tablas y graficos para comparacion empresarial.
- En este caso importa que las etiquetas queden presentables para informe y visualizacion, no solo tecnicamente unificadas.

### Lectura tecnica del enfoque 2

La limpieza del enfoque 2 es la mas amplia de las tres, porque no solo prepara una columna: **convierte el dataset en una base multiproposito para comparar empresas desde varias dimensiones**. La decision dominante fue construir llaves limpias para agrupar fabricantes y compararlos bajo una misma composicion.

## Enfoque 3: decisiones de limpieza

**Archivo fuente:** `src/enfoque_03_efectos_secundarios_componentes/cleaning.py`

### 1. Extraer componentes sin dosis y en minusculas

Se genero `componentes` a partir de `Composition`, quitando dosis y normalizando a minusculas.

**Por que**

- El objetivo era estudiar asociaciones componente-efecto, no marcas ni concentraciones.
- La normalizacion a minusculas evita fragmentacion artificial por capitalizacion.

### 2. Parsear `Side_effects` con regex

Se genero `efectos_secundarios` usando:

```python
re.findall(r"[A-Z][^A-Z]*", texto)
```

**Por que**

- La columna `Side_effects` no trae separadores explicitos como comas o punto y coma.
- En el dataset, cada efecto comienza con mayuscula, por lo que esa estructura se uso como delimitador implicito.
- Era la decision tecnica necesaria para pasar de texto concatenado a una lista de efectos analizables.

### 3. Normalizar fabricante para agrupacion interna

Se genero `manufacturer` en minusculas.

**Por que**

- Aunque fabricante no es la variable central del enfoque 3, sirve como dato auxiliar para agrupar y controlar consistencia.
- En este caso se priorizo la homogeneidad tecnica por sobre la presentacion visual.

### 4. Crear variables de conteo y anomalia

Se crearon:

- `componentes`
- `efectos_secundarios`
- `manufacturer`
- `n_componentes`
- `n_efectos`
- `anomalia_componentes`
- `anomalia_efectos`

**Por que**

- `n_componentes` y `n_efectos` permiten estudiar complejidad y carga de efectos.
- Las columnas de anomalia marcan si fallaba el parseo de componentes o efectos, sin borrar registros automaticamente.

### 5. Aceptar una regla heuristica explicita

El enfoque 3 depende de una suposicion estructural: que los efectos estan concatenados y cada uno empieza con mayuscula.

**Por que esta decision es valida**

- La regla no se eligio al azar; responde al patron observado en el EDA.
- Permite recuperar una estructura que el dataset no trae explicitamente.
- Sin esa regla, no habria forma de construir el grafo componente-efecto ni la matriz de contingencia.

### Lectura tecnica del enfoque 3

La limpieza del enfoque 3 es la mas "estructural": toma dos columnas textuales complejas y las convierte en listas explotables. La decision dominante fue **transformar texto libre en relaciones observables**.

## Comparacion de decisiones tecnicas

### Que tienen en comun

- Los tres enfoques eliminan duplicados exactos.
- Los tres generan columnas derivadas en lugar de trabajar directamente sobre el raw.
- Los tres conservan las columnas originales para trazabilidad.
- Los tres prefieren marcar anomalias antes que borrar informacion sin justificacion.

### En que se diferencian

- **Enfoque 1** limpia para clasificar composiciones.
- **Enfoque 2** limpia para comparar entidades empresariales.
- **Enfoque 3** limpia para construir asociaciones entre listas.

### Diferencia clave de criterio

- En el enfoque 1, la dosis se elimina porque estorba al analisis de combinaciones.
- En el enfoque 2, se conserva una version legible del fabricante porque el resultado final es comparativo y visual.
- En el enfoque 3, se baja a minusculas y se usa regex porque lo prioritario es la consistencia tecnica del parseo.

## Conclusion

La principal conclusion metodologica es que **la limpieza depende del objetivo analitico**. Aunque los tres enfoques parten del mismo dataset, no era correcto aplicar exactamente la misma estrategia en todos.

- El enfoque 1 necesitaba una composicion estable y categorizable.
- El enfoque 2 necesitaba entidades comparables a nivel empresa.
- El enfoque 3 necesitaba reconstruir relaciones componente-efecto desde texto libre.

Por eso, la mejor forma de justificar las limpiezas del proyecto no es decir que "se limpiaron datos", sino explicar que **cada pipeline tomo decisiones especificas para hacer analizable la variable central de su propio enfoque**.

## Referencias

- `src/enfoque_01_combinaciones_componentes/cleaning.py`
- `src/enfoque_02_comparacion_empresas/cleaning.py`
- `src/enfoque_03_efectos_secundarios_componentes/cleaning.py`
- `docs/enfoque_01_combinaciones_componentes/decisiones_limpieza.md`
- `docs/enfoque_03_combinaciones_componentes/decisiones_limpieza.md`
