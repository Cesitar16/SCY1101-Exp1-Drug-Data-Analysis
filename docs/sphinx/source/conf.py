from __future__ import annotations

import sys
from pathlib import Path


DOCS_SOURCE = Path(__file__).resolve().parent
SPHINX_ROOT = DOCS_SOURCE.parent
PROJECT_ROOT = SPHINX_ROOT.parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


project = "Medicine Analysis"
author = "Equipo SCY1101"
copyright = "2026, Equipo SCY1101"
release = "0.1.0"
language = "es"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
]

templates_path: list[str] = []
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autosummary_generate = True
autodoc_member_order = "bysource"
autoclass_content = "both"
add_module_names = False
napoleon_google_docstring = True
napoleon_numpy_docstring = False

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

html_theme = "alabaster"
html_title = "Medicine Analysis - Documentacion"
html_theme_options = {
    "description": "Documentacion Sphinx del proyecto de analisis de medicamentos",
    "fixed_sidebar": True,
    "show_powered_by": False,
    "page_width": "1180px",
    "sidebar_width": "280px",
}
