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

So if you define the configuration file `"context_file.yaml"`, with the content:

.. code-block:: YAML

   entry1: value1
   entry2: value2

This can be loaded into a :py:class:`Context <processor_tools.context.Context>` object as:

.. ipython:: python

   path = "context_file.yaml"
   context = Context(path)

Providing a list of configuration file paths loads the values from each of the configuration files. In the case where multiple input configuration files provide the same value, earlier in the list overwrites later in the list.

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