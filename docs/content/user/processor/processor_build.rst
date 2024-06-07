.. _processor_build:

###########################
Building a Processor Object
###########################

.. ipython:: python
   :suppress:

   import processor_tools

The core of **processor_tools** functionality involves building `Processor` classes that are subclasses of :py:class:`BaseProcessor <processor_tools.processor.BaseProcessor>`. This section of user guide provides information for how to build and use your own `Processor` classes.

Creating a Processor Class
==========================

Processor classes are defined by subclassing the :py:class:`BaseProcessor <processor_tools.processor.BaseProcessor>` class. The processor's processing algorithm should be defined by overriding :py:meth:`BaseProcessor.run <processor_tools.processor.BaseProcessor.run>` method.

In this example we define a processor class for multiplying input values together.

.. ipython:: python

   class Multiplication(processor_tools.BaseProcessor):
       def run(self, val1, val2):
          return val1 * val2
   mult_proc = Multiplication()
   print(mult_proc.run(2,3))

.. _context:
Defining Configuration Values
=============================

Configuration values can be provided when the processor class is initialised with a ``context`` object. The context object should be a container (such as a :py:class:`dict`) with the necessary values defined. Within an initialised processor object, the ``context`` object can be accessed as an instance attribute.


:ref:`more <context>`

.. ipython:: python

   class Exponentiate(processor_tools.BaseProcessor):
       def run(self, val1):
          return val1 ** self.context["exponent"]
   context = {"exponent": 2}
   exp_proc = Exponentiate(context=context)
   print(exp_proc)
   print(exp_proc.run(3))

.. _name:
Setting Processor Names
=======================

By default the processor name is defined as the class name (e.g., ``"Multiplication"`` and ``"Exponentiate"``). This may be updated by setting the ``cls_processor_name`` class attribute when defining the class. The processor name may be accessed from processor objects via the ``processor_name`` attribute.

.. ipython:: python

   class FirstProcessor(processor_tools.BaseProcessor):
       pass
   class SecondProcessor(processor_tools.BaseProcessor):
       cls_processor_name = "my_new_name"
   proc1 = FirstProcessor()
   proc2 = SecondProcessor()
   print(proc1.processor_name, proc2.processor_name)

Using Subprocessors
===================

Processor classes may be related to other processor classes as "subprocessors". Subprocessors are effectively plugins that can represent modular parts of a processing chain. A defined subprocessor may be switched out for alternative implementation by replacing it with a different processor class. This allows for user configurable processing chains in cases where a variety of processing options are available.

Appending subprocessors to a processor object
---------------------------------------------

A processor may be added to another processor class's subprocessors using the :py:meth:`append_subprocessor <processor_tools.processor.BaseProcessor.append_subprocessor>` method. Subprocessors may be added as instantiated processor objects, processor classes, or processor factories (more of which below). :py:meth:`append_subprocessor <processor_tools.processor.BaseProcessor.append_subprocessor>` stores an instantiated processor object for any of these options.

A processor object's subprocessors are stored in a dictionary that is accessible via the ``subprocessors`` attribute.

.. ipython:: python

   class MyProcessor(processor_tools.BaseProcessor):
       pass

   proc = MyProcessor()
   proc.append_subprocessor("subprocessor1", MyProcessor)
   print(proc.subprocessors)


This can continue recursively, where a processor class's subprocessor may itself have it's own subprocessors and so on.

.. ipython:: python

   subproc2 = MyProcessor()
   subproc2.append_subprocessor("subprocessor2a", MyProcessor)
   proc.append_subprocessor("subprocessor2", subproc2)
   print(proc.subprocessors)
   print(proc.subprocessors["subprocessor2"].subprocessors)

.. _path:
Subprocessor paths
------------------

The relative paths for these processors within the subprocessor structure are accessible via the ``processor_path`` attribute.

.. ipython:: python

   print(proc.subprocessors["subprocessor2"].processor_path)
   print(proc.subprocessors["subprocessor2"].subprocessors["subprocessor2a"].processor_path)

Configuring subprocessor options with processor factories
---------------------------------------------------------

In many cases subprocessor elements within a processing chain may be completed by several different processor implementations, the choice of which may depend on the circumstance.

``processor_tools`` processors handle this with a :py:class:`ProcessorFactory <processor_tools.processor.ProcessorFactory>`. Processor factories are effectively containers which can store a set of processors.

.. ipython:: python

   class Algo1(processor_tools.BaseProcessor):
        cls_processor_name = "algorithm1"

   class Algo2(processor_tools.BaseProcessor):
        cls_processor_name = "algorithm2"

   algo_factory = processor_tools.ProcessorFactory()
   algo_factory.add_processor(Algo1)
   algo_factory.add_processor(Algo2)

   print(algo_factory["algorithm2"])

These factories can be used to define the set of optional implementations for a subprocessor. As before, they can be appended to a processor's subprocessors using the the :py:meth:`append_subprocessor <processor_tools.processor.BaseProcessor.append_subprocessor>` method. The choice of processor implementation is set by the user in the processor :ref:`context <context>`. The context object should define an entry for the :ref:`subprocessor path <path>` that is defined by the factory with a value of the :ref:`processor name <name>` of choice.

.. ipython:: python

   context = {"opt_algo": "algorithm1"}
   proc_with_opts = MyProcessor(context=context)
   proc_with_opts.append_subprocessor("opt_algo", algo_factory)
   print(proc_with_opts.subprocessors)

If all the processors required for a factory are in one or more package modules, you can point to that module(s) when building the class.

.. code-block:: python

   mod_algo_factory = processor_tools.ProcessorFactory("package.subpackage.module")

So ``mod_algo_factory`` would now contain all :py:class:`BaseProcessor <processor_tools.processor.BaseProcessor>` subclasses in the module ``package.subpackage.module``.

Defining processor class default subprocessors
----------------------------------------------

In defining a processor class, it is usually clear what subprocessor steps and options are required. To simplify the definition of such processors, the class subprocessors can be defined as a class attribute at the definition of the class.

.. ipython:: python

   class ProcessingChain(processor_tools.BaseProcessor):
       cls_subprocessors = {"sub1": MyProcessor, "sub2": algo_factory}
   context = {"sub2": "algorithm2"}
   proc_cls_sps = ProcessingChain(context=context)
   print(proc_cls_sps.subprocessors)

Running processors with subprocessors
-------------------------------------

A processor with defined subprocessors can make use them when defining it's :py:meth:`run` method.

.. ipython:: python

   class Exponentiate(processor_tools.BaseProcessor):
       def run(self, val1):
          return val1 ** self.context["exponent"]
   class Pythagoras(processor_tools.BaseProcessor):
       cls_subprocessors = {"exp": Exponentiate}
       def run(self, a, b):
           exp_proc = self.subprocessors["exp"]
           return (exp_proc.run(a) + exp_proc.run(b))**0.5
   context = {"exponent": 2}
   pyth_proc = Pythagoras(context=context)
   print(pyth_proc.run(3,4))

By default however, for a processor with defined subprocessors, it's :py:meth:`run` will run each of the subprocessors sequentially in order, the output of each feeding into the next. This may be of use when the subprocessors define each step of a processing chain.

.. ipython:: python

   import numpy as np
   class Square(processor_tools.BaseProcessor):
       def run(self, val):
          return val ** 2
   class Ave(processor_tools.BaseProcessor):
       def run(self, val):
          return np.mean(val)
   class Sqrt(processor_tools.BaseProcessor):
       def run(self, val):
          return val ** 0.5
   class RMS(processor_tools.BaseProcessor):
       cls_subprocessors = {"sq": Square, "mean": Ave, "root": Sqrt}
   rms_proc = RMS()
   print(rms_proc.run(np.array([4,3,2,5,6])))