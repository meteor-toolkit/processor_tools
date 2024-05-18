.. _db:

#################
Database Handling
#################

**processor_tools** provides some utilities for working with databases. These utilities are aimed at providing a simple wrapper to the `sqlalchemy package <https://www.sqlalchemy.org>`_, to make it easier to get started.

The utilities are primarily aimed at supporting two types of databases: `SQLite <https://www.sqlite.org>`_ and `PostgreSQL <https://www.postgresql.org>`_ (which can be  extended to handle geospatial data types using `PostGIS <https://postgis.net>`_). There are `pro's and con's <https://www.digitalocean.com/community/tutorials/sqlite-vs-mysql-vs-postgresql-a-comparison-of-relational-database-management-systems>`_ to either sort of database, but in summary - SQLite is lightweight and portable but PostgreSQL (often just postgres) offers a lot more features, scalability, and performance. SQLite comes with bundled python, however you must separately install postgres before you can use it (and PostGIS if required).

The most common database actions are referred to as "`CRUD <https://en.wikipedia.org/wiki/Create,_read,_update_and_delete>`_" - create, read, update and delete. processor_tools provides the :py:class:`DatabaseCRUD <processor_tools.db_crud.DatabaseCRUD>` class to support this functionality.

To initialise the :py:class:`DatabaseCRUD <processor_tools.db_crud.DatabaseCRUD>`, you must define:

* *database url* - `formatted url <https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>`_ for sqlite or postgres database.
* *database model* - the definition of the database `schema <https://en.wikipedia.org/wiki/Database_schema>`_. This can be done either as a dictionary or a configuration file - as described in the following section.

.. _db-model:
Defining the Database Model
===========================

**processor_tools** enables the definition of the database model with a simple syntax either as a YAML configuration file or equivalent dictionary. From this :py:class:`DatabaseCRUD <processor_tools.db_crud.DatabaseCRUD>` is able to build the structure of `sqlalchemy declarative classes <https://docs.sqlalchemy.org/en/20/orm/quickstart.html>`_ that it requires to make the python/database interface.

The database model definition syntax defines the following hierarchy for each database table:

+ *table* - table name as string
   + *column* - column name as string
      + *type* - column type as string (e.g., `"int"`), or python type if defining model with dictionary (e.g., :py:class:`int`). :ref:`See below <db-model-types>` for allowed types
      + *primary_key* - (optional) True if column is primary_key (as string or :py:class:`bool` object if defining model with dictionary)
      + *foreign_key* (*str*) - (optional) foreign key mapping (e.g., as `"other_table.other_column"`)
      + plus other *kwargs* and values for :py:func:`~sqlalchemy.orm.mapped_column`

As mentioned above, database models using this syntax can be defined either as a YAML configuration file - e.g., this example database schema for a library:

.. code-block::

    book:
        book_id:
            type: int
            primary_key: true
        title:
            type: str
        author_id:
            type: int
            foreign_key: "author.author_id"

    author:
        author_id:
            type: int
            primary_key: true
        name:
            type: str

Or, as an equivalent dictionary - e.g.:

.. ipython:: python

   lib_model_def = {
       "book": {
           "book_id": {
               "type": int,
               "primary_key": True
           },
           "title": {
               "type": str,
           },
           "author_id": {
               "type": int,
               "foreign_key": "author.name"
           }
       },
       "author": {
           "author_id": {
               "type": int,
               "primary_key": True
           },
           "name": {
               "type": str
           }
       }
   }

If you are developing a python package remember that, as with other non-python data files, the model YAML configuration file should be included in the `"package_data"` files in the `setup.py <https://setuptools.pypa.io/en/latest/userguide/datafiles.html#subdirectory-for-data-files>`_.

.. _db-model-types:
Database Model Column Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following `sqlalchemy column types <https://docs.sqlalchemy.org/en/20/core/type_basics.html#generic-camelcase-types>`_ (or `geoalchemy2 column types <https://geoalchemy-2.readthedocs.io>`_ for PostGIS) may be defined in the **processor_tools** database model definition syntax, as:

* sqlachemy :py:class:`~sqlalchemy.types.Boolean` - defined in the definition syntax either as string `"bool"` or :py:class:`bool` type object (if defining model definition in dictionary).
* sqlalchemy :py:class:`~sqlalchemy.types.Integer` - defined in the definition syntax either as string `"int"` or :py:class:`int` type object.
* sqlalchemy :py:class:`~sqlalchemy.types.Float` - defined in the definition syntax either as string `"float"` or :py:class:`float` type object.
* sqlalchemy :py:class:`~sqlalchemy.types.String` - defined in the definition syntax either as string `"str"` or :py:class:`str` type object.
* sqlalchemy :py:class:`~sqlalchemy.types.DateTime` - defined in the definition syntax either as string `"datetime"` or :py:class:`~datatime.datetime` type.
* sqlalchemy :py:class:`~sqlalchemy.types.Date` - defined in the definition syntax either as string `"date"` or :py:class:`~datatime.date` type object.
* geoalchemy2 :py:class:`~geoalchemy2.types.Geometry` -  defined in the definition syntax either as a geometry type string (see `geoalchemy2 documentation <https://geoalchemy-2.readthedocs.io/en/0.2.5/types.html#geoalchemy2.types._GISType>`_ for options) or a `shapely Geometry <https://shapely.readthedocs.io/en/stable/geometry.html>`_ class (e.g., :py:class:`~shapely.Point`).

Initialising the DatabaseCRUD object
====================================

With a :ref:`database model <db-model>` defined, you can get started creating and interacting with your database. The following examples will use sqlite as this is the most simple.

The first step is initialising the :py:class:`DatabaseCRUD <processor_tools.db_crud.DatabaseCRUD>` object, as follows:

.. ipython:: python

   import processor_tools
   url = "sqlite:///library.db"
   lib_db_crud = processor_tools.DatabaseCRUD(url, lib_model_def)

This step has built the structure of `sqlalchemy declarative classes <https://docs.sqlalchemy.org/en/20/orm/quickstart.html>`_ that is required to make the python/database interface. These table classes can be accessed as a dictionary (by table name) with the :py:attr:`DatabaseCRUD.model <processor_tools.db_crud.DatabaseCRUD.model>` attribute, as follows:

.. ipython:: python

   print(lib_db_crud.model)

Also created is a sqlalchemy :py:class:`~sqlalchemy.engine.Engine` object, which is sqlalchemy's source of database connectivity. This can be accessed through the :py:attr:`DatabaseCRUD.engine <processor_tools.db_crud.DatabaseCRUD.engine>` attribute.

Using these interfaces you can easily access the full functionality of sqlalchemy (:ref:`see below <extending-db-crud>` for an example of this).

Creating the database
=====================

The database can then be created as follows:


.. ipython:: python

   lib_db_crud.create()

Creating, reading, updating and deleting data
=============================================

Future updates to :py:class:`DatabaseCRUD <processor_tools.db_crud.DatabaseCRUD>` will add helper methods to create, read, update, and delete data. Many operations will still require custom functionality, even when :py:class:`DatabaseCRUD <processor_tools.db_crud.DatabaseCRUD>` is updated to include more helper methods.

For time being all CRUD operations can be performed by directly accessing the `sqlalchemy declarative classes <https://docs.sqlalchemy.org/en/20/orm/quickstart.html>`_ for the database tables, using the :py:attr:`DatabaseCRUD.model <processor_tools.db_crud.DatabaseCRUD.model>` attribute. :ref:`See below <extending-db-crud>` for some guidance on how to approach this.

Deleting the database
=====================

If you require to delete the database this can be done as follows:

.. ipython:: python

   lib_db_crud.delete()

.. _extending-db-crud:
Extending DatabaseCRUD for custom operations
============================================

As mentioned above, currently all database CRUD operations require the definition of custom functions. These custom functions can make use of the `sqlalchemy declarative classes <https://docs.sqlalchemy.org/en/20/orm/quickstart.html>`_ for the database tables, accessible via :py:attr:`DatabaseCRUD.model <processor_tools.db_crud.DatabaseCRUD.model>` attribute.

Also useful for creating custom CRUD functions is the :py:meth:`DatabaseCRUD.create_session() <processor_tools.db_crud.DatabaseCRUD.create_session>` method, which uses the :py:attr:`DatabaseCRUD.engine <processor_tools.db_crud.DatabaseCRUD.engine>` to create a sqlalchemy :py:class:`~sqlalchemy.orm.Session`. A `sqlalchemy Session <https://docs.sqlalchemy.org/en/20/orm/session_basics.html#session-basics>`_ establishes a transaction with the database and represents a “holding zone” of operations that can be committed.

A nice design pattern for implementing custom CRUD functions is to subclass :py:class:`DatabaseCRUD <processor_tools.db_crud.DatabaseCRUD>`. This can be done as follows:

.. ipython:: python

   from sqlalchemy import select
   class LibraryCRUD(processor_tools.DatabaseCRUD):
       def add_author(self, name: str):
          Author = self.model["author"]
          with self.create_session() as session:
              new_author = Author(name=name)
              session.add(new_author)
              session.commit()
       def list_author_names(self) -> list:
           authors = []
           session = self.create_session()
           stmt = select(self.model["author"]).where()
           for author in session.scalars(stmt):
               authors.append(author.name)
           return authors

For more information on how to write database operations using sqlalchemy, see `sqlalchemy user guide <https://docs.sqlalchemy.org/en/20/orm/quickstart.html>`_.

This can then be interacted with in the same way as before:

.. ipython:: python

   lib_db_crud = LibraryCRUD(url, lib_model_def)
   lib_db_crud.create()
   lib_db_crud.add_author("JRR Tolkien")
   lib_db_crud.list_author_names()

.. ipython:: python
   :suppress:

   lib_db_crud.delete()