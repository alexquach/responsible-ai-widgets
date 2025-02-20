# Copyright (c) Microsoft Corporation
# Licensed under the MIT License.
#
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import inspect
import os
import raiwidgets
import sys
sys.path.insert(0, os.path.abspath(os.path.join('..', 'raiwidgets')))


# -- Project information -----------------------------------------------------

project = 'Responsible AI Widgets'
copyright = 'Microsoft Corporation'
author = 'Roman Lutz, Ilya Matiach, Ke Xu'

# The full version, including alpha/beta/rc tags
release = f'v{raiwidgets.__version__}'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinx.ext.linkcode',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


intersphinx_mapping = {
    'python3': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),
    'sklearn': ('https://scikit-learn.org/stable/', None),
    'fairlearn': ('https://fairlearn.github.io/main/', None),
    'dice-ml': ('http://interpret.ml/DiCE/', None)
}


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'pydata_sphinx_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "external_links": [
        # {"name": "StackOverflow",
        #  "url": "https://stackoverflow.com/questions/tagged/raiwidgets"}
    ],
    "github_url": "https://github.com/microsoft/responsible-ai-widgets",
    "show_prev_next": False
}

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = "landing_page/img/error-analysis-logo.svg"

# Additional templates that should be rendered to pages, maps page names to
# template names.
html_additional_pages = {
}

# If false, no index is generated.
html_use_index = True

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_css_files = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# Use filename_pattern so that plot_adult_dataset is not
# included in the gallery, but its plot is available for
# the quickstart
# sphinx_gallery_conf = {
#     'examples_dirs': '../examples',
#     'gallery_dirs': 'auto_examples',
#     # pypandoc enables rst to md conversion in downloadable notebooks
#     'pypandoc': True,
# }

# html_sidebars = {
#     "**": [
#         "version-sidebar.html",
#         "sidebar-search-bs.html",
#         "sidebar-nav-bs.html"
#     ],
# }

# Auto-Doc Options
# ----------------

# Change the ordering of the member documentation
autodoc_member_order = 'groupwise'


# Linking Code
# ------------

# The following is used by sphinx.ext.linkcode to provide links to github
# based on pandas doc/source/conf.py
def linkcode_resolve(domain, info):
    """Determine the URL corresponding to Python object."""
    if domain != "py":
        return None

    modname = info["module"]
    fullname = info["fullname"]

    submod = sys.modules.get(modname)
    if submod is None:
        return None

    obj = submod
    for part in fullname.split("."):
        try:
            obj = getattr(obj, part)
        except AttributeError:
            return None

    try:
        fn = inspect.getsourcefile(inspect.unwrap(obj))
    except TypeError:
        fn = None
    if not fn:
        return None

    try:
        source, lineno = inspect.getsourcelines(obj)
    except OSError:
        lineno = None

    if lineno:
        linespec = f"#L{lineno}-L{lineno + len(source) - 1}"
    else:
        linespec = ""

    tag_or_branch = os.getenv("SPHINX_MULTIVERSION_NAME", default="main")
    fn = os.path.relpath(fn, start=os.path.dirname(raiwidgets.__file__)) \
        .replace(os.sep, '/')
    return f"http://github.com/microsoft/responsible-ai-widgets/blob/" \
        f"{tag_or_branch}/raiwidgets/raiwidgets/{fn}{linespec}"
