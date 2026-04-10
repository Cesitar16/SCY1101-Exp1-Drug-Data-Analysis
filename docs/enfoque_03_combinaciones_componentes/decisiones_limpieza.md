# Decisiones de Limpieza — Foco: Efectos Secundarios por Componentes

**Proyecto:** SCY1101 - Programación para la Ciencia de Datos  
**Dataset:** Medicine_Details.csv  
**MD5 del archivo original:** `93656e73e4e8fbf7dd8da9ecfab7ce07`  
**Tamaño del archivo:** 4.360.239 bytes  
**Fecha de procesamiento:** 2026-04-10  

---

## Contexto

El objetivo del foco es analizar la relación entre los **componentes activos**
(columna `Composition`) y los **efectos secundarios** (columna `Side_effects`)
de los medicamentos del dataset. Para ello fue necesario diseñar un flujo de
limpieza que preparara ambas columnas sin alterar su valor informativo original.

El desafío técnico principal de este foco reside en que **los efectos secundarios
no tienen separador explícito**: están concatenados usando la mayúscula inicial
de cada efecto como delimitador implícito (p. ej. `"Nausea Abdominal pain Diarrhea"`).

Todas las decisiones descritas en este documento están implementadas en
`src/enfoque_03_efectos_secundarios_componentes/cleaning.py` y fueron validadas
mediante `src/enfoque_03_efectos_secundarios_componentes/validation.py`.

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
valoraciones. Conservarlos inflaría artificialmente las coocurrencias
componente–efecto en el análisis posterior.

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

## Decisión 2 — Extracción de componentes sin dosis

**Función:** `extraer_componentes()`

### Qué se hizo
Se creó la columna `componentes` extrayendo únicamente los nombres de
los principios activos desde `Composition`, eliminando las dosis entre
paréntesis mediante la expresión regular `r"\(.*?\)"` y normalizando el
separador `+`.

Ejemplo:
```
Entrada : "Amoxycillin  (500mg) +  Clavulanic Acid (125mg)"
Salida  : ['amoxycillin', 'clavulanic acid']
```

### Por qué se eliminaron las dosis
Para el análisis de **qué componentes causan qué efectos**, la dosis no es
relevante como clave de agrupación. `Amoxycillin (500mg)` y `Amoxycillin (250mg)`
son el mismo componente. Conservar la dosis habría fragmentado artificialmente
los grupos, reduciendo la potencia estadística del análisis.

La columna `Composition` original se conserva intacta para trazabilidad,
por lo que la información de dosis no se pierde del dataset.

### Por qué se normalizan a minúsculas
Los nombres de componentes en el dataset presentan capitalización inconsistente
(`Amoxycillin` vs `amoxycillin`). Normalizar a minúsculas garantiza que el mismo
principio activo se agrupe bajo una única clave, evitando duplicados artificiales.

### Impacto cuantificado
| Columna generada | Descripción |
|---|---|
| `componentes` | Lista de nombres de componentes en minúsculas sin dosis |
| Componentes únicos detectados (post-limpieza) | 875 (con mín. 5 observaciones) |
| Registros con lista vacía (anomalías) | 0 |

---

## Decisión 3 — Parseo de efectos secundarios con regex

**Función:** `extraer_efectos_secundarios()`

### Qué se hizo
Se creó la columna `efectos_secundarios` parseando la columna `Side_effects`
mediante una expresión regular que separa los efectos por las mayúsculas
iniciales. La lógica:

1. Se aplica `re.findall(r"[A-Z][^A-Z]*", texto)` para detectar cada segmento
   que comienza con mayúscula.
2. Cada token se normaliza eliminando espacios sobrantes y convirtiéndolo a
   minúsculas.
3. Los tokens vacíos se filtran.

Ejemplo:
```
Entrada : "Rectal bleeding Taste change Headache Nosebleeds"
Salida  : ['rectal bleeding', 'taste change', 'headache', 'nosebleeds']
```

### Por qué este enfoque de parseo
El dataset no usa separadores convencionales (comas, punto y coma). Los efectos
están concatenados con la mayúscula inicial como único delimitador implícito.
Esta es la estrategia de parseo más robusta para la estructura observada en el
EDA: captura correctamente efectos multipalabra (`"Rectal bleeding"`,
`"High blood pressure"`) sin fragmentarlos.

### Limitación conocida
Si un efecto tiene todas las palabras en minúsculas (sin mayúscula inicial),
el regex no puede segmentarlo correctamente y lo fusionaría con el efecto
anterior. En el EDA se verificó que **todos los efectos observados comienzan
con mayúscula**, por lo que esta limitación no afecta la calidad del dataset.

### Impacto cuantificado
| Columna generada | Descripción |
|---|---|
| `efectos_secundarios` | Lista de efectos secundarios en minúsculas |
| Efectos únicos detectados (post-limpieza) | 761 (con mín. 5 observaciones) |
| Registros con lista vacía (anomalías) | 0 |

---

## Decisión 4 — Generación de columnas de conteo derivadas

**Función:** `añadir_columnas_derivadas()`

### Qué se hizo
A partir de `componentes` y `efectos_secundarios` se generaron cuatro columnas
adicionales:

- **`n_componentes`** (int): cantidad de componentes activos por medicamento.
- **`n_efectos`** (int): cantidad de efectos secundarios por medicamento.
- **`anomalia_componentes`** (bool): `True` si el medicamento no tiene ningún
  componente extraído.
- **`anomalia_efectos`** (bool): `True` si el medicamento no tiene ningún
  efecto secundario extraído.

### Por qué no se elimina directamente en este paso
Las columnas de anomalía marcan el problema sin eliminarlo automáticamente,
dejando la decisión documentada y explícita. Permite al analista inspeccionar
los casos antes de decidir.

### Distribución por número de componentes (post-limpieza)
| Componentes | Medicamentos |
|---|---|
| 1 | 7.019 |
| 2 | 3.569 |
| 3 | 929 |
| 4 | 147 |
| 5 | 51 |
| 6+ | 26 |
| **Total** | **11.741** |

### Distribución de efectos secundarios (resumen estadístico)
| Estadístico | Valor |
|---|---|
| Media | 6,92 efectos / medicamento |
| Mediana | 6,00 |
| Mínimo | 1 |
| Máximo | 36 |

---

## Decisión 5 — Marcado de anomalías sin eliminación automática

**Funciones:** `flag_anomalias()`

### Qué se hizo
Se usaron las columnas `anomalia_componentes` y `anomalia_efectos` generadas
en el paso anterior para marcar registros problemáticos.

### Por qué no se eliminan automáticamente
La eliminación automática de registros anómalos sin inspección previa
es una mala práctica: podría descartar información válida por un problema
de formato que se podría corregir con imputación. Al marcar en vez de
eliminar, se deja la decisión final documentada y explícita.

### Resultado
Se detectaron **0 anomalías** de componentes y **0 anomalías** de efectos.
Todos los registros tienen al menos un componente y al menos un efecto
secundario válidos.

---

## Resumen del pipeline de limpieza

| Paso | Función | Filas eliminadas | Columnas añadidas |
|---|---|---|---|
| 1. Eliminar duplicados | `eliminar_duplicados` | 84 | 0 |
| 2. Extraer componentes | `extraer_componentes` | 0 | 1 (`componentes`) |
| 3. Parsear efectos | `extraer_efectos_secundarios` | 0 | 1 (`efectos_secundarios`) |
| 4. Columnas de conteo | `añadir_columnas_derivadas` | 0 | 5 (`manufacturer`, `n_componentes`, `n_efectos`, `anomalia_componentes`, `anomalia_efectos`) |
| **Total** | | **84 (-0,71%)** | **7** |

---

## Validación de integridad

La validación completa se ejecutó mediante `run_validation_pipeline()`
y el reporte fue exportado a `outputs/reports/reporte_integridad_e03.json`.

| Verificación | Estado |
|---|---|
| Checksum MD5 del CSV original | `93656e73e4e8fbf7dd8da9ecfab7ce07` |
| Esquema del DataFrame raw | ⚠️ Diferencia de tipo str vs object (pandas ≥2.0) — no funcional |
| Shapes antes/después | ✅ 84 filas eliminadas (0,71%) |
| Columnas derivadas en df_clean | ✅ Las 7 columnas presentes |

> **Nota sobre el esquema:** La discrepancia `str` vs `object` se debe a que
> pandas ≥ 2.0 reporta `str` para columnas de texto puro, mientras que la
> validación espera el tipo legacy `object`. Esto no afecta el comportamiento
> funcional del dataset ni del pipeline.

---

## Columnas del dataset final

| Columna | Origen | Tipo | Descripción |
|---|---|---|---|
| Medicine Name | Raw | str | Nombre comercial del medicamento |
| Composition | Raw | str | Composición original con dosis |
| Uses | Raw | str | Usos terapéuticos |
| Side_effects | Raw | str | Efectos secundarios concatenados (raw) |
| Image URL | Raw | str | URL de imagen referencial |
| Manufacturer | Raw | str | Fabricante original |
| Excellent Review % | Raw | int64 | % de valoraciones excelentes |
| Average Review % | Raw | int64 | % de valoraciones promedio |
| Poor Review % | Raw | int64 | % de valoraciones malas |
| manufacturer | Derivada | str | Fabricante normalizado a minúsculas |
| componentes | Derivada | list[str] | Componentes activos sin dosis |
| efectos_secundarios | Derivada | list[str] | Efectos secundarios parseados |
| n_componentes | Derivada | int | Cantidad de componentes activos |
| n_efectos | Derivada | int | Cantidad de efectos secundarios |
| anomalia_componentes | Derivada | bool | Marca: lista de componentes vacía |
| anomalia_efectos | Derivada | bool | Marca: lista de efectos vacía |
