"""processor_tools.db_crud - utilities for creating, reading, updating and deleting databases"""

from copy import copy, deepcopy
import inspect
import types
from typing import Optional, Dict, Union, Type, List, Any
from datetime import date, datetime
import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.engine.url import make_url
from sqlalchemy_utils import drop_database, database_exists, create_database
from geoalchemy2 import Geometry
import shapely
from processor_tools import read_config


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = ["DatabaseCRUD"]


GEOM_STRINGS: List[str] = [
    "GEOMETRY",
    "POINT",
    "LINESTRING",
    "POLYGON",
    "MULTIPOINT",
    "MULTILINESTRING",
    "MULTIPOLYGON",
    "GEOMETRYCOLLECTION",
    "CURVE",
]


class DatabaseCRUD:
    """
    Class containing utilities for creating, reading, updating and deleting databases.

    Wraps sqlalchemy to simplify using databases.

    :param url: url of database to create (sqlite or postgresql)
    :param model_def: path of config file or dictionary that defines schema - see :ref:`user guide <db-model>` for description of database model definition syntax
    """

    def __init__(self, url: str, model_def: Union[str, dict]):
        """
        Create database at defined url
        """

        # init declarative base baseclass
        class DBBase(DeclarativeBase):
            pass

        # init attributes
        self.DBBase: Type[DeclarativeBase] = DBBase
        self.url: sqlalchemy.engine.url.URL = copy(make_url(url))
        self._model_def: Dict = (
            read_config(model_def) if isinstance(model_def, str) else model_def
        )
        self._model: Optional[Dict[str, Type[DeclarativeBase]]] = None
        self._engine: Optional[sqlalchemy.engine.Engine] = None

        # check url valid
        if self.url.drivername.startswith("sqlite"):
            pass

        elif self.url.drivername.startswith("postgres"):
            pass

        else:
            raise ValueError("invalid url - engine must be either sqlite or postgresql")

    @property
    def model(self) -> Dict[str, Type[DeclarativeBase]]:
        """
        Database sqlalchemy declarative database model classes

        :return: dictionary of sqlalchemy declarative classes for model tables
        """

        if self._model is not None:
            return self._model

        self._model = self._create_model(self._model_def)

        return self._model

    @property
    def engine(self) -> sqlalchemy.engine.Engine:
        """
        Returns sqlalchemy database engine

        :return: sqlalchemy database engine
        """

        if self._engine is not None:
            return self._engine

        self._engine = create_engine(self.url)

        return self._engine

    def _create_model(self, model_def: Dict) -> Dict[str, Type[DeclarativeBase]]:
        """
        Create sqlalchemy declarative database model classes for defined schema - see :ref:`user guide <db-model>` for description of database model definition syntax

        :param model_def: database schema definition
        :return: model dictionary
        """

        model: Dict[str, Type[DeclarativeBase]] = dict()

        for table_name, table_def in model_def.items():
            table_attrs = {"__tablename__": table_name}

            for column_name, column_def in table_def.items():
                table_attrs[column_name] = self._return_mapped_column(column_def)

            table_class = type(table_name, (self.DBBase,), table_attrs)

            model[table_name] = table_class

        return model

    @staticmethod
    def _return_mapped_column(column_def: dict) -> sqlalchemy.orm.MappedColumn:
        """
        Returns a :py:class:`sqlalchemy.orm.MappedColumn`object based on definition dictionary - see :ref:`user guide <db-model>` for description of database model definition syntax

        :param column_def: column definition dictionary
        :return: sqlalchemy mapped column object
        """

        column_def = deepcopy(column_def)

        mc_args: List[Any] = []

        # add type to args
        column_type = column_def.pop("type")
        mc_args.append(DatabaseCRUD._map_column_type(column_type))

        # add foreign key to args
        if "foreign_key" in column_def:
            foreign_key = column_def.pop("foreign_key")
            mc_args.append(ForeignKey(foreign_key))

        return mapped_column(*mc_args, **column_def)

    @staticmethod
    def _map_column_type(
        python_type: Union[type, str],
    ) -> Union[Type[sqlalchemy.types.TypeEngine], sqlalchemy.types.ARRAY, Geometry]:
        """
        Returns sqlalchemy type equivalent to given python type or type string

        :param python_type: python type or type string (i.e. `"int"`) - see :ref:`user guide <db-model-types>` for description of database model definition syntax

        :return: equivalent sqlalchemy type
        """

        # if python_type shapely.geometry set to geom_type string
        if inspect.isclass(python_type):
            if issubclass(python_type, shapely.geometry.base.BaseGeometry):  # type: ignore
                python_type = python_type().geom_type  # type: ignore

        if isinstance(python_type, types.GenericAlias):  # type: ignore
            if isinstance(python_type(), list):  # type: ignore
                python_type = str(python_type).replace("list", "array")

        # if python_type string set to uppercase
        if isinstance(python_type, str):
            python_type = python_type.upper()

        # map python_type object to sqlalchemy/geoalchemy2 object
        if python_type == bool or python_type == "BOOL":
            return sqlalchemy.types.Boolean
        elif python_type == int or python_type == "INT":
            return sqlalchemy.types.Integer
        elif python_type == float or python_type == "FLOAT":
            return sqlalchemy.types.Float
        elif python_type == str or python_type == "STR":
            return sqlalchemy.types.String
        elif python_type == datetime or python_type == "DATETIME":
            return sqlalchemy.types.DateTime
        elif python_type == date or python_type == "DATE":
            return sqlalchemy.types.Date
        elif isinstance(python_type, str) and python_type in GEOM_STRINGS:
            return Geometry(python_type)
        elif isinstance(python_type, str):
            if python_type[:5] == "ARRAY":
                array_dtype_str = python_type[6:-1]

                if array_dtype_str == "":
                    raise ValueError(
                        "Must define dtype of array - e.g., array[int] - not: "
                        + python_type
                    )

                array_dtype = DatabaseCRUD._map_column_type(array_dtype_str)
                return sqlalchemy.types.ARRAY(array_dtype)

            else:
                raise ValueError("Unknown type: " + str(python_type))

        else:
            raise ValueError("Unknown type: " + str(python_type))

    @staticmethod
    def _get_model_def_types(model_def: Dict) -> list:
        """
        Returns list of column types in database model definition

        :param model: database schema definition
        :return: database column types
        """

        model_types = []
        for table in model_def.keys():
            for column in model_def[table].keys():
                model_types.append(model_def[table][column]["type"])

        return list(set(model_types))

    def _get_model_types(self):
        """
        Returns list of column types in database model

        :param model: database schema definition
        :return: database column types
        """

        model_types = []

        for table in self.model.keys():
            for column in self.model[table].__table__.columns.keys():
                model_types.append(
                    self.model[table].__table__.columns[column].type.__class__
                )

        return list(set(model_types))

    def _is_postgis(self) -> bool:
        """
        Returns True if database requires PostGIS extension, otherwise False

        :return: PostGIS flag
        """
        return any([t == Geometry for t in self._get_model_types()])

    def create_session(self) -> sqlalchemy.orm.Session:
        """
        Returns :py:class:`~sqlalchemy.orm.Session` object for database transactions, using self.engine

        :return: sqlalchemy session object
        """

        return sqlalchemy.orm.Session(self.engine)

    def create(self) -> None:
        """
        Create database
        """

        # create database if it doesn't already exist
        if not database_exists(self.url):
            create_database(self.url)
        else:
            raise ValueError("Database already exists: " + str(self.url))

        # check if postgis extension necessary
        if self._is_postgis():
            if self.url.drivername.startswith("postgres"):
                with self.engine.connect() as connection:
                    connection.execute(sqlalchemy.text("CREATE EXTENSION postgis"))
                    connection.commit()
            else:
                raise ValueError(
                    "Invalid URL for schema with postgis types: " + str(self.url)
                )

        # initialise model
        self.model

        # create tables
        self.DBBase.metadata.create_all(self.engine)

    def delete(self) -> None:
        """
        Deletes database
        """

        drop_database(self.url)


if __name__ == "__main__":
    pass
