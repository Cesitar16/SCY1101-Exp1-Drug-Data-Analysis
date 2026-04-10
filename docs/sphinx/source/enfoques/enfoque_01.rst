Enfoque 01: Combinaciones de Componentes
========================================

Pregunta principal
------------------

Que tipos de combinaciones de componentes activos existen en el dataset y con
que frecuencia aparecen juntos.

Variables centrales
-------------------

- ``Composition``
- ``components_list``
- ``n_components``
- ``size_category``

Pipeline
--------

1. Eliminacion de duplicados exactos.
2. Normalizacion de ``Composition``.
3. Extraccion de componentes sin dosis.
4. Generacion de columnas derivadas.
5. Transformacion a formato largo y pares de co-ocurrencia.
6. Construccion de la matriz de co-ocurrencia.

Decisiones de limpieza citadas
------------------------------

Normalizacion de ``Composition``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../src/enfoque_01_combinaciones_componentes/cleaning.py
   :language: python
   :pyobject: normalizar_composicion

**Para que se uso**

- estandarizar espacios y el separador ``+`` en la columna ``Composition``;
- preparar un parseo estable antes de separar componentes;
- evitar que el mismo medicamento quede fragmentado por diferencias de formato.

Extraccion de componentes activos
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../src/enfoque_01_combinaciones_componentes/cleaning.py
   :language: python
   :pyobject: extraer_componentes

**Para que se uso**

- eliminar dosis entre parentesis;
- quedarse solo con los principios activos;
- construir una representacion comparable para estudiar combinaciones.

Marcado de anomalias
^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../src/enfoque_01_combinaciones_componentes/cleaning.py
   :language: python
   :pyobject: flag_anomalies

**Para que se uso**

- marcar registros con ``n_components == 0``;
- conservar trazabilidad sin eliminar automaticamente informacion;
- dejar explicitados los casos anormales para revision posterior.

Modulos principales
-------------------

- ``src.enfoque_01_combinaciones_componentes.cleaning``
- ``src.enfoque_01_combinaciones_componentes.transform``
- ``src.enfoque_01_combinaciones_componentes.validation``
- ``src.enfoque_01_combinaciones_componentes.analysis``

Notebooks relacionados
----------------------

- ``notebooks/enfoque_01_combinaciones_componentes/01_eda_combinaciones_componentes.ipynb``
- ``notebooks/enfoque_01_combinaciones_componentes/02_limpieza_transformacion_combinaciones_componentes.ipynb``
- ``notebooks/enfoque_01_combinaciones_componentes/03_analisis_combinaciones_componentes.ipynb``

Documentos relacionados
-----------------------

- ``docs/enfoque_01_combinaciones_componentes/decisiones_limpieza.md``
- ``docs/enfoque_01_combinaciones_componentes/analisis_graficos.md``
