Instalacion y Uso
=================

Requisitos
----------

- Python 3.11 o superior
- entorno virtual recomendado
- dependencias del proyecto instaladas desde ``requirements.txt``

Instalacion del proyecto
------------------------

En PowerShell:

.. code-block:: powershell

   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   pip install -e .

Ejecucion del proyecto
----------------------

Cargar el dataset:

.. code-block:: powershell

   python src\load_data.py

Ejecutar el orquestador principal:

.. code-block:: powershell

   python main.py

Ejecutar el pipeline completo del enfoque 2:

.. code-block:: powershell

   python -m src.enfoque_02_comparacion_empresas.pipeline

Construccion de esta documentacion
----------------------------------

Instalar dependencias de Sphinx:

.. code-block:: powershell

   pip install -r docs\sphinx\requirements.txt

Construir HTML:

.. code-block:: powershell

   python -m sphinx -b html docs\sphinx\source docs\sphinx\_build\html

En Windows tambien puedes usar:

.. code-block:: powershell

   .\docs\sphinx\make.bat html

Notebooks
---------

El trabajo exploratorio y demostrativo del proyecto esta separado por carpetas:

- ``notebooks/general/``
- ``notebooks/enfoque_01_combinaciones_componentes/``
- ``notebooks/enfoque_02_comparacion_empresas/``
- ``notebooks/enfoque_03_efectos_secundarios_componentes/``
