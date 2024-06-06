.. _context:

########################################
Determining and Storing Processing State
########################################

`Processor` classes can be initialised with a defined `context`. The `context` object is a container for storing data defining the processor state/configuration.  This can be accessed within the processor through the :py:attr:`context <processor_tools.processor.BaseProcessor.context>` attribute.

`context` may be a simple :py:class:`dict`, however **processor_tools** provides a specific :py:class:`Context <processor_tools.context.Context>` object that provides useful extra functionality for handling `Processor` state/configuration.

This page provides a guide on how to use :py:class:`Context <processor_tools.context.Context>` objects.

Building a Context object
=========================

:py:class:`Context <processor_tools.context.Context>` objects can be defined with a dictionary of configuration values - as follows:

.. ipython:: python

   from processor_tools import Context
   config_vals = {
       "entry1": "value1",
       "entry2": "value2"
   }
   context = Context(config_vals)

They can also be built from an equivalent configuration file (of a format readable by :py:func:`read_config <processor_tools.config_io.read_config>`), by defining the file path.

.. ipython:: python
   :suppress:

   from processor_tools.config_io import write_config
   path = "context_file.yaml"
   write_config(path, config_vals)

   from processor_tools.config_io import write_config
   path2 = "context_file2.yaml"
   write_config(path2, config_vals)

So if you define the configuration file `"context_file.yaml"`, with the content:

.. code-block:: YAML

   entry1: value1
   entry2: value2

This can be loaded into a :py:class:`Context <processor_tools.context.Context>` object as:

.. ipython:: python

   path = "context_file.yaml"
   context = Context(path)

The path can also be to directory containing set of configuration files. Providing a list of configuration paths loads the values from each of the configuration files/directories of files.

In the case where multiple input configuration files provide the same value, earlier in the list overwrites later in the list. So in the example,

.. ipython:: python

   path1 = "context_file.yaml"
   path2 = "context_file2.yaml"
   context = Context([path1, path2])

if the same configuration value is defined in both of these files, the value in `"context_file1.yaml"` overwrites that in `"context_file2.yaml"`.

The :py:class:`Context <processor_tools.context.Context>` class variable `default_config` enables you to set configuration file(s)/directory(ies) of files that are loaded every time the class is initialised. Configuration values from these files come lower in the priority list than those defined at initialisation.

Therefore, the following has the same effect as the previous example:

.. ipython:: python

   Context.default_config = path2
   context = Context(path1)

Interfacing with the Context object
===================================

The `Processor` context can be accessed within the processor through the :py:attr:`context <processor_tools.processor.BaseProcessor.context>` attribute.

Configuration values are listed in the context keys :py:meth:`keys <processor_tools.context.Context.keys>`.

.. ipython:: python

   print(context.keys())

Configuration values can be accessed by indexing:

.. ipython:: python

   print(context["entry1"])
   context["entry3"] = "value3"
   print(context.keys())

.. ipython:: python
   :suppress:

   import os
   os.remove(path)
   os.remove(path2)