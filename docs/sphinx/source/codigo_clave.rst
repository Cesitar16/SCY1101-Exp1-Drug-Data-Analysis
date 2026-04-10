Codigo Clave para la Presentacion
=================================

Esta pagina resume los fragmentos de codigo que vale la pena mostrar en una
presentacion tecnica del proyecto. La idea no es enseñar todo el repositorio,
sino seleccionar piezas que expliquen:

- como se prepara el dataset;
- que decision tecnica importante toma cada enfoque;
- como se transforma el dato para volverlo analizable;
- y como se asegura reproducibilidad mediante pipelines.

Si el tiempo es corto, prioriza un fragmento por enfoque y el cargador general.

Carga del dataset
-----------------

``load_medicine_data``
^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../src/load_data.py
   :language: python
   :pyobject: load_medicine_data
   :linenos:

**Para que sirve**

- centraliza la carga del CSV raw;
- permite descargar el dataset si falta;
- garantiza que todos los enfoques partan de la misma fuente de datos.

**Por que conviene mostrarlo**

- explica el punto de entrada del proyecto;
- demuestra que el flujo es reproducible y no depende de cargar datos manualmente.

Enfoque 1: Combinaciones de Componentes
---------------------------------------

``extraer_componentes``
^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../src/enfoque_01_combinaciones_componentes/cleaning.py
   :language: python
   :pyobject: extraer_componentes
   :linenos:

**Para que sirve**

- elimina dosis en ``Composition``;
- separa principios activos usando ``+``;
- construye la lista base sobre la que se analiza la combinacion farmacologica.

**Por que conviene mostrarlo**

- es la decision de limpieza mas importante del enfoque 1;
- justifica por que se comparan componentes y no textos crudos de composicion.

``generar_pares``
^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../src/enfoque_01_combinaciones_componentes/transform.py
   :language: python
   :pyobject: generar_pares
   :linenos:

**Para que sirve**

- genera todos los pares posibles de componentes en un medicamento;
- ordena alfabéticamente para que ``(A, B)`` y ``(B, A)`` no cuenten distinto;
- alimenta la matriz de co-ocurrencia del enfoque 1.

**Por que conviene mostrarlo**

- traduce una combinacion farmacologica en una estructura analizable;
- conecta directamente limpieza, transformacion y analisis.

Enfoque 2: Comparacion por Empresa
----------------------------------

``build_composition_key``
^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../src/enfoque_02_comparacion_empresas/cleaning.py
   :language: python
   :pyobject: build_composition_key
   :linenos:

**Para que sirve**

- crea una clave canonica para comparar la misma composicion entre empresas;
- elimina el problema de depender del nombre comercial del medicamento;
- permite responder si la calidad cambia segun el fabricante.

**Por que conviene mostrarlo**

- es la decision tecnica mas fuerte del enfoque 2;
- explica por que la comparacion entre empresas es metodologicamente valida.

``manufacturer_reputation_ranking``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../src/enfoque_02_comparacion_empresas/analysis.py
   :language: python
   :pyobject: manufacturer_reputation_ranking
   :linenos:

**Para que sirve**

- resume cada empresa en una sola fila;
- calcula volumen de medicamentos y promedios de reviews;
- construye el ranking de reputacion del enfoque 2.

**Por que conviene mostrarlo**

- enseña claramente el paso de dato individual a comparacion entre empresas;
- conecta directo con tablas y graficos del informe.

``run_company_comparison_pipeline``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../src/enfoque_02_comparacion_empresas/pipeline.py
   :language: python
   :pyobject: run_company_comparison_pipeline
   :linenos:

**Para que sirve**

- ejecuta limpieza, transformacion y analisis en un flujo unico;
- exporta tablas, figuras y reporte JSON;
- deja el enfoque 2 reproducible fuera del notebook.

**Por que conviene mostrarlo**

- demuestra madurez tecnica del enfoque;
- sirve para justificar que no es solo un notebook exploratorio.

Enfoque 3: Efectos Secundarios por Componentes
----------------------------------------------

``extraer_efectos_secundarios``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../src/enfoque_03_efectos_secundarios_componentes/cleaning.py
   :language: python
   :pyobject: extraer_efectos_secundarios
   :linenos:

**Para que sirve**

- parsea ``Side_effects`` cuando el dataset no trae separadores explicitos;
- usa regex para reconstruir una lista de efectos;
- convierte texto concatenado en una estructura explotable.

**Por que conviene mostrarlo**

- es la decision de limpieza mas importante del enfoque 3;
- explica como se recupera informacion estructurada desde texto libre.

``construir_crosstab``
^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../src/enfoque_03_efectos_secundarios_componentes/transform.py
   :language: python
   :pyobject: construir_crosstab
   :linenos:

**Para que sirve**

- construye la matriz componente x efecto secundario;
- filtra componentes con pocas observaciones;
- prepara el heatmap y el analisis de asociaciones del enfoque 3.

**Por que conviene mostrarlo**

- muestra el paso mas importante de transformacion del enfoque;
- deja claro como se pasa de listas a una matriz interpretable.

Orden sugerido para exponer
---------------------------

Si necesitas una secuencia simple para la presentacion, esta suele funcionar bien:

1. ``load_medicine_data`` para mostrar el punto de entrada.
2. Un fragmento de limpieza por enfoque:
   ``extraer_componentes`` del enfoque 1,
   ``build_composition_key`` del enfoque 2,
   ``extraer_efectos_secundarios`` del enfoque 3.
3. Un fragmento de transformacion o agregacion por enfoque:
   ``generar_pares``, ``manufacturer_reputation_ranking`` y ``construir_crosstab``.
4. Cerrar con ``run_company_comparison_pipeline`` como ejemplo de pipeline reproducible.

Con esa secuencia se cubren entorno, limpieza, transformacion, analisis y
reproducibilidad sin saturar la presentacion con codigo.
