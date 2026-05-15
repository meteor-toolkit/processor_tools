#!/usr/bin/env python
#
# processor_tools documentation build configuration file
#

from importlib.metadata import version as _pkg_version, PackageNotFoundError

try:
    _version = _pkg_version("processor_tools")
except PackageNotFoundError:
    _version = "0.0.0"

project_title = "processor_tools".replace("_", " ").title()


# -- General configuration ---------------------------------------------

default_role = "code"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "IPython.sphinxext.ipython_directive",
    "IPython.sphinxext.ipython_console_highlighting",
    "sphinx_design",
    "myst_parser",
]

templates_path = ["_templates"]

source_suffix = [".rst", ".md"]

master_doc = "index"

project = project_title
copyright = "MetEOR Toolkit Team"
author = "MetEOR Toolkit Team"

version = _version
release = _version

language = "en"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

pygments_style = "sphinx"

todo_include_todos = False


# -- Options for HTML output -------------------------------------------

html_theme = "sphinx_book_theme"

html_title = "processor_tools"

html_static_path = ["_static"]

htmlhelp_basename = "processor_toolsdoc"


# -- Options for LaTeX output ------------------------------------------

latex_elements = {}

latex_documents = [
    (
        "content/user/user_guide",
        "user_manual.tex",
        "{}: User Guide".format(project_title),
        "MetEOR Toolkit Team",
        "manual",
    ),
]
