.. _init_config:

################################
Initialising Package Config Files
################################

**processor_tools** provides the :py:class:`ConfigInit <processor_tools.config.init_config.ConfigInit>` class to define and initialise a set of configuration files for a package. It is designed to be instantiated once per package, then used to create config files in the appropriate location on first use, or re-run via a CLI entry point.

.. ipython:: python
   :suppress:

   import os, shutil, tempfile
   tmp_dir = tempfile.mkdtemp()
   src_yaml = os.path.join(tmp_dir, "source.yaml")
   with open(src_yaml, "w") as f:
       f.write("db_host: localhost\ndebug: false\n")

Defining config files
=====================

A :py:class:`ConfigInit <processor_tools.config.init_config.ConfigInit>` is created with a ``package_name`` and a ``configs`` dictionary. The dictionary maps each config filename to a template defining the file's initial content.

Three template types are supported:

* ``dict`` — a dictionary of values written to a new config file
* ``str`` — a path to an existing file that is copied to the target location
* ``callable`` — a function called at init time with no arguments, returning a ``dict``

.. ipython:: python

   import os
   from processor_tools.config import ConfigInit

   config_init = ConfigInit(
       package_name="mypackage",
       configs={
           "settings.yaml": {"db_host": "localhost", "debug": False},
           "defaults.yaml": src_yaml,
           "env.yaml": lambda: {"hostname": os.uname().nodename},
       },
   )

The callable form is useful when default values can only be determined at runtime, such as environment-specific settings.

Config directory locations
==========================

Rather than specifying full paths in the ``configs`` dictionary, :py:class:`ConfigInit <processor_tools.config.init_config.ConfigInit>` resolves a config directory at init time. Two standard locations are provided.

User home directory
-------------------

:py:meth:`home_dir <processor_tools.config.init_config.ConfigInit.home_dir>` returns ``~/.<package_name>``. This is the default and is appropriate for per-user configuration:

.. ipython:: python

   config_init.home_dir()

Project directory
-----------------

:py:meth:`project_dir <processor_tools.config.init_config.ConfigInit.project_dir>` returns ``<base>/.<package_name>``, placing config alongside the project. By default the base is the current working directory:

.. ipython:: python

   config_init.project_dir()

Passing ``base_file=__file__`` from the calling module gives a deterministic location regardless of where the process was started from:

.. code-block:: python

   # in mypackage/config.py
   config_init.project_dir(base_file=__file__)  # -> <mypackage dir>/.mypackage

An explicit base path can also be provided:

.. ipython:: python

   config_init.project_dir(project_path="/path/to/project")

Initialising config files
=========================

The :py:meth:`init <processor_tools.config.init_config.ConfigInit.init>` method creates all defined config files in the chosen directory. The directory is created automatically if it does not exist.

By default, ``exists_skip=True`` — existing files are left unchanged so that any user edits are preserved:

.. ipython:: python

   config_dir = os.path.join(tmp_dir, "config")
   config_init.init(path=config_dir)
   os.listdir(config_dir)

To overwrite any existing files, pass ``exists_skip=False``:

.. code-block:: python

   config_init.init(path=config_dir, exists_skip=False)

Checking initialisation state
==============================

:py:meth:`is_initialised <processor_tools.config.init_config.ConfigInit.is_initialised>` returns ``True`` if all defined config files are present in the directory:

.. ipython:: python

   config_init.is_initialised(path=config_dir)

:py:meth:`missing <processor_tools.config.init_config.ConfigInit.missing>` returns a list of any filenames that are absent:

.. ipython:: python

   config_init.missing(path=config_dir)

Both methods default to :py:meth:`home_dir <processor_tools.config.init_config.ConfigInit.home_dir>` when no path is given. They are useful for guarding against missing config at package startup and for writing tests.

Recommended usage patterns
===========================

Lazy first-run initialisation
------------------------------

The recommended approach is to check at package startup whether config has been initialised, and run it automatically if not. This requires no action from the user after install.

As with the CLI entry point pattern below, first define the :py:class:`ConfigInit <processor_tools.config.init_config.ConfigInit>` object in a dedicated module:

.. code-block:: python

   # mypackage/config.py
   from processor_tools.config import ConfigInit

   config_init = ConfigInit(
       package_name="mypackage",
       configs={
           "settings.yaml": {"db_host": "localhost"},
       },
   )

Then import it in the package's ``__init__.py`` and check on startup:

.. code-block:: python

   # mypackage/__init__.py
   from mypackage.config import config_init

   if not config_init.is_initialised():
       print(f"Initialising config at {config_init.home_dir()}...")
       config_init.init()

Because ``exists_skip=True`` by default, this is safe to call on every startup — it only creates files that are genuinely absent.

CLI entry point
---------------

A :py:meth:`cli <processor_tools.config.init_config.ConfigInit.cli>` method is provided for wiring up a command-line entry point. This allows users to re-initialise config, point it at a different location, or script setup in CI environments.

Define a thin wrapper function and register it in ``pyproject.toml``:

.. code-block:: python

   # mypackage/config.py
   from processor_tools.config import ConfigInit

   config_init = ConfigInit(
       package_name="mypackage",
       configs={
           "settings.yaml": {"db_host": "localhost"},
       },
   )

   def init_cli():
       config_init.cli()

.. code-block:: toml

   # pyproject.toml
   [project.scripts]
   mypackage-init = "mypackage.config:init_cli"

After install, users can then run:

.. code-block:: console

   $ mypackage-init                          # initialise in ~/.<package_name>/
   $ mypackage-init --project                # initialise in <cwd>/.<package_name>/
   $ mypackage-init --path /explicit/path    # initialise at an explicit path
   $ mypackage-init --overwrite              # overwrite any existing files

.. ipython:: python
   :suppress:

   shutil.rmtree(tmp_dir)