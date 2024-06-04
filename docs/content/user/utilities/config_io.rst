.. _config_io:

############################
Handling Configuration Files
############################

**processor_tools** provides some utilities for handling of configuration files of various formats.

Writing Configuration Files
===========================

The :py:func:`write_config <processor_tools.config_io.write_config>` function provides the capability to write a configuration file by defining:

* `path` - where the file extension defines the format of file that is written. Currently `".yaml"` files are supported.
* `config_dict` - a dictionary of configuration values to write to the file.

This can be achieved as follows:

.. ipython:: python

   from processor_tools import write_config
   config_dict = {"val1": True, "val2": {"subval": "data"}}
   path = "config_file.yaml"
   write_config(path, config_dict)

This writes the file `"config_file.yaml"` with content:

.. code-block:: yaml

    val1: true
    val2:
      subval: data

Reading configuration files
===========================

The :py:func:`write_config <processor_tools.config_io.read_config>` function provides the capability to read configuration files. This is done as follows:

.. ipython:: python

   from processor_tools import read_config
   config = read_config(path)
   print(config)

This supports file types:

* `default python <https://docs.python.org/3/library/configparser.html>`_ - with file extension `".cfg"` or `".config"`
* yaml - with file extension `".yaml"` or `".yml"`


.. ipython:: python
   :suppress:

   import os
   # os.remove(path)
