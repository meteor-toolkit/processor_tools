"""processor_tools.db_crud - utilities for creating, reading, updating and deleting databases"""

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy_utils import drop_database, database_exists, create_database
from copy import copy
from typing import Optional, Dict, Union, Type
from processor_tools import read_config


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = ["DatabaseCRUD"]


class DatabaseCRUD:
    """
    Class containing utilities for creating, reading, updating and deleting databases.
    """

    def __init__(self, url: str, model_def: Optional[Union[str, dict]]):
        """
        Create database at defined url

        :param url: url of database to create (sqlite or postgresql)
        :param model_def : path of config file or dictionary that defines schema
        """

        # init declarative base baseclass
        class DBBase(DeclarativeBase):
            pass

        # init attributes
        self.DBBase = DBBase
        self.url = copy(make_url(url))
        self.engine = None
        self._model_def: Dict = read_config(model_def) if isinstance(model_def, str) else model_def
        self._model: Optional[Dict[str, Type[DBBase]]] = None

        # check url valid
        if self.url.drivername.startswith("sqlite"):
            pass

        elif self.url.drivername.startswith("postgres"):
            create_database(url)
        else:
            raise NameError("invalid url - engine must be either sqlite or postgresql")

        self.engine = create_engine(self.url)

    @property
    def model(self) -> Dict[str, Type["DBBase"]]:
        """
        Database sqlalchemy declarative database model classes

        :return:
        """

        if self._model is not None:
            return self._model

        self._model = self._create_model(self._model_def)

        return self._model

    @staticmethod
    def _create_model(model: Dict) -> Dict[str, Type["DBBase"]]:
        """
        Create sqlalchemy declarative database model classes for defined schema

        :param model: database schema definition
        :return: model dictionary
        """

        model = dict()

        # todo - add create model code

        return model

    def create(self) -> None:
        """
        Create database
        """

        if not database_exists(self.url):
            create_database(self.url)

        else:
            raise ValueError("Database already exists: " + str(self.url))

        self.DBBase.metadata.create_all(self.engine)

    def delete(self) -> None:
        """
        Deletes database
        """

        drop_database(self.url)


if __name__ == "__main__":
    pass
