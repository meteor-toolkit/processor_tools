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
Rather than specifying full paths in the ``configs`` dictionary, :py:class:`ConfigInit <processor_tools.config.init_config.ConfigInit>` resolves a config directory at init time.
By default, this is ``~/.config/<package_name>`` but it can be customised with the optional parameters described below. The config files are then created within this directory.

Optional configuration directory parameters
--------------------------------------------

The :py:class:`ConfigInit <processor_tools.config.init_config.ConfigInit>` constructor also accepts two optional parameters to customize config directory handling.
The first one is the ``config_directory`` — an explicit path where config files will be stored. If not provided, the path defaults to ``~/.<package_name>``.
When setting this parameter, the provided path is stored in a config directory file for persistence across sessions. By default, the config directory file is located 
at ``~/.<processor_tools>/config_directory_<package_name>.txt``, but this can be customized with the second parameter, ``config_directory_file_path``. 
This allows users to choose where the config directory path is stored, which can be useful in environments with specific directory structures or permissions. 
If neither parameter is provided, the system defaults to using the home directory for config storage, ensuring a sensible default while allowing flexibility for different use cases.

.. ipython:: python

   # Initialize with explicit config directory
   config_init = ConfigInit(
       package_name="mypackage",
       configs={"settings.yaml": {"db_host": "localhost"}},
       config_directory="/custom/config/path",
   )

   # Or specify a custom location for the config directory file
   config_init = ConfigInit(
       package_name="mypackage",
       configs={"settings.yaml": {"db_host": "localhost"}},
       config_directory="/custom/config/path",
       config_directory_file_path="/custom/path/to/config_directory_file.txt",
   )


Managing config directory location
===================================

The :py:meth:`get_config_directory <processor_tools.config.init_config.ConfigInit.get_config_directory>` method retrieves the current config directory path. This reads from the config directory file, or returns the default home directory if the file doesn't exist:

.. code-block:: python

   config_dir = config_init.get_config_directory()
   print(f"Config directory: {config_dir}")

The :py:meth:`set_config_directory <processor_tools.config.init_config.ConfigInit.set_config_directory>` method updates the config directory path. It creates both the config directory and its parent directories as needed, and writes the path to the config directory file:

.. code-block:: python

   # Set config directory to a custom location
   config_init.set_config_directory(config_directory="/my/custom/config/path")


Config directory locations
==========================

Some common config directory locations are provided as methods for convenience. They can be used directly, or as a reference when writing custom directory methods.

User home directory
-------------------

:py:meth:`home_dir <processor_tools.config.init_config.ConfigInit.home_dir>` returns ``~/.config/<package_name>``. This is the default and is appropriate for per-user configuration:

.. ipython:: python

   config_init.home_dir()

Project directory
-----------------

:py:meth:`project_dir <processor_tools.config.init_config.ConfigInit.project_dir>` returns ``<base>/.<package_name>``, placing config alongside the project. By default the base is the current working directory (which is typically the project root where the init gets called from):

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
   config_init.set_config_directory(config_directory=config_dir)  # creates config files in tmp_dir/config
   config_init.init()
   os.listdir(config_dir)

To overwrite any existing files, pass ``exists_skip=False``:

.. code-block:: python

   config_init.init(exists_skip=False)

It is also possible to set the config directory at init time by passing a path or location keyword to the ``config_directory`` parameter. At this stage it is also possible to set to the home directory with the keyword "home" and the project directory with the keyword "project":

.. ipython:: python

   ConfigInit(package_name="mypackage",
              configs={"settings.yaml": {"db_host": "localhost"}},
              config_directory="project")  # creates config files in project directory

Checking initialisation state
==============================

:py:meth:`is_initialised <processor_tools.config.init_config.ConfigInit.is_initialised>` returns ``True`` if all defined config files are present in the directory:

.. ipython:: python

   config_init.is_initialised()

:py:meth:`missing <processor_tools.config.init_config.ConfigInit.missing>` returns a list of any filenames that are absent:

.. ipython:: python

   config_init.missing()

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
       print(f"Initialising config at {config_init.get_config_directory()}...")
       config_init.init()

Because ``exists_skip=True`` by default, this is safe to call on every startup — it only creates files that are genuinely absent.

Integrating with Context objects
------------------------------
If your package uses :py:class:`Context <processor_tools.context.Context>` objects, 

.. code-block:: python

   from processor_tools.context import Context
   from mypackage.config import config_init

   # Create a context and load custom values in addition to all values from config files defined in config_init
   context = Context({"<section>": {"<key>": "<value>"}}, config_init=config_init)

Or one can subclass :py:class:`Context <processor_tools.context.Context>` and pass a :py:class:`ConfigInit <processor_tools.config.init_config.ConfigInit>` to the constructor. This ensures that config files are initialised and loaded whenever the context is created, without needing to call the CLI entry point or check for initialisation separately.

.. code-block:: python

   from processor_tools.context import Context
   from mypackage.config import config_init

   class MyContext(Context):
      default_config: Optional[Union[str, List[str]]] = None

      def __init__(self, *args, **kwargs):
         self.default_config = ["path/to/default_config.yaml"]  # one or more default config files to load with every context
         super().__init__(*args, config_init=config_init, **kwargs)

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

   $ mypackage-init --home                   # initialise in ~/.config/<package_name>/
   $ mypackage-init --project                # initialise in <cwd>/.<package_name>/
   $ mypackage-init --path /explicit/path    # initialise at an explicit path
   $ mypackage-init --overwrite              # overwrite any existing files

.. ipython:: python
   :suppress:

   shutil.rmtree(tmp_dir)