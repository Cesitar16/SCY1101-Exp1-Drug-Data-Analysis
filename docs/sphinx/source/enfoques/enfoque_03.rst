Enfoque 03: Efectos Secundarios por Componentes
===============================================

Pregunta principal
------------------

Que componentes activos se asocian con que efectos secundarios y si la
complejidad del medicamento altera esa relacion.

Variables centrales
-------------------

- ``Composition`` y ``componentes``
- ``Side_effects`` y ``efectos_secundarios``
- ``n_componentes``
- ``n_efectos``

Pipeline
--------

1. Eliminacion de duplicados.
2. Extraccion de componentes sin dosis.
3. Parseo de efectos secundarios mediante regex.
4. Generacion de variables de conteo y anomalias.
5. Transformacion al producto cartesiano componente x efecto.
6. Construccion y normalizacion del crosstab componente x efecto.
7. Analisis de frecuencias, diversidad, relacion y asociaciones.

Decisiones de limpieza citadas
------------------------------

Extraccion de componentes
^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../src/enfoque_03_efectos_secundarios_componentes/cleaning.py
   :language: python
   :pyobject: extraer_componentes

**Para que se uso**

- quitar dosis y normalizar la composicion a principios activos;
- agrupar un mismo componente bajo una clave consistente;
- preparar la posterior relacion componente-efecto.

Parseo de efectos secundarios con regex
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../src/enfoque_03_efectos_secundarios_componentes/cleaning.py
   :language: python
   :pyobject: extraer_efectos_secundarios

**Para que se uso**

- separar ``Side_effects`` cuando el dataset no trae delimitadores explicitos;
- convertir texto libre en una lista de efectos analizables;
- habilitar la construccion del producto cartesiano componente x efecto.

Marcado de anomalias
^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../src/enfoque_03_efectos_secundarios_componentes/cleaning.py
   :language: python
   :pyobject: flag_anomalias

**Para que se uso**

- detectar registros sin componentes o sin efectos parseados;
- revisar calidad del parseo antes del analisis;
- conservar los registros marcados en vez de borrarlos sin inspeccion.

Modulos principales
-------------------

- ``src.enfoque_03_efectos_secundarios_componentes.cleaning``
- ``src.enfoque_03_efectos_secundarios_componentes.transform``
- ``src.enfoque_03_efectos_secundarios_componentes.validation``
- ``src.enfoque_03_efectos_secundarios_componentes.analysis``

Notebooks relacionados
----------------------

- ``notebooks/enfoque_03_efectos_secundarios_componentes/01_eda_efectos_secundarios_componentes.ipynb``
- ``notebooks/enfoque_03_efectos_secundarios_componentes/02_limpieza_transformacion_efectos_secundarios_componentes.ipynb``
- ``notebooks/enfoque_03_efectos_secundarios_componentes/03_analisis_efectos_secundarios_componentes.ipynb``

Documentos relacionados
-----------------------

- ``docs/enfoque_03_combinaciones_componentes/decisiones_limpieza.md``
