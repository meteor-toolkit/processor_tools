.. _setup_utils:

################################
Customising Package Installation
################################

It can be useful to automatically execute some additional initialisation code during a package's installation process (i.e. when `pip install package` is run) - for example, setting up the package configuration files.

In general, this is relatively `complicated to achieve <https://niteo.co/blog/setuptools-run-custom-code-in-setup-py>`_. First, one must appropriately subclass the `setuptools.command.install` class. Such custom `setuptools.command.install` subclasses are then run by setting the `cmdclass` parameter of the package `setup() <https://setuptools.pypa.io/en/latest/references/keywords.html>`_ function in a dictionary:

.. code-block::

    setup(
        ...
        cmdclass={
            'install': CustomInstallCommand,
        },
        ...
    )

**processor_tools**, however, provides some functionality to make this much simpler to achieve!

Buidling custom setup cmdclass
==============================

**processor_tools** provides the :py:class:`CustomCmdClassUtils <processor_tools.setup_utils.CustomCmdClassUtils>` class to support building `cmdclass` that execute user defined python functions during a package's installation process.

First you need to define the function(s) you want to run during installation. For the sake of this example, let's assume the user wants to print a message at the start and the end of the installation.

.. ipython:: python

    def print_message(message_str):
        print(message_str)

This can be built into a `cmdclass` for `setup() <https://setuptools.pypa.io/en/latest/references/keywords.html>`_ using the :py:meth:`CustomCmdClassUtils <processor_tools.setup_utils.CustomCmdClassUtils.build_cmdclass>` method.

.. ipython:: python

   from processor_tools.setup_utils import CustomCmdClassUtils
   cmdutils = CustomCmdClassUtils()
   custom_cmdclass = cmdutils.build_cmdclass(
       preinstall=print_message,     # pre-install function
       pre_args="hello",             # pre-install function args
       postinstall=print_message,    # post-install function
       post_args="goodbye"           # post-install function args
   )

Provide your `custom_cmdclass` to the `setup() <https://setuptools.pypa.io/en/latest/references/keywords.html>`_ function in your package's `setup.py` so that your custom code is run during installation.

.. code-block::

    from setuptools import setup

    setup(
        name="package_name",
        cmdclass=custom_cmdclass,
    )

For this example, `"hello"` will now get printed at the start of the installation and `"goodbye"` will get printed at the end.
