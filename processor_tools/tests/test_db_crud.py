"""processor_tools.tests.test_db_crud - tests for processor_tools.db_crud"""

import unittest
import sqlalchemy.orm
from sqlalchemy.engine.url import make_url
from sqlalchemy import inspect
from processor_tools.db_crud import DatabaseCRUD
import geoalchemy2
import shapely.geometry
from unittest.mock import patch
import string
import random
from datetime import date, datetime
import os
import shutil
from sqlalchemy import String, Float, Integer, Boolean, Date, DateTime
from sqlalchemy_utils import drop_database


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = []

THIS_DIRECTORY = os.path.dirname(__file__)

TEST_MODEL = {
    "table1": {
        "1id": {"type": int, "primary_key": True},
        "column1": {"type": str},
    },
    "table2": {
        "2id": {"type": int, "primary_key": True},
        "column2": {
            "type": int,
        },
        "ref_1id": {"type": int, "foreign_key": "table1.1id"},
    },
}

TEST_MODEL_GEO = {
    "table1": {
        "1id": {"type": int, "primary_key": True},
        "column1": {"type": shapely.geometry.Polygon},
    }
}


class TestDatabaseCRUD(unittest.TestCase):
    def setUp(self) -> None:
        letters = string.ascii_lowercase
        self.tmp_dir_name = "tmp_" + "".join(random.choice(letters) for i in range(5))
        self.tmp_dir_path = os.path.join(THIS_DIRECTORY, self.tmp_dir_name)
        os.makedirs(self.tmp_dir_path)

    def test___init___dict_sqlite(self):
        temp_name = "".join(random.choices(string.ascii_lowercase, k=6)) + ".db"
        url = "sqlite:///" + self.tmp_dir_path + "/" + temp_name

        db_crud = DatabaseCRUD(url, TEST_MODEL)

        self.assertEqual(db_crud._model_def, TEST_MODEL)
        self.assertEqual(str(db_crud.engine.url), url)
        self.assertIsNone(db_crud._model)

    def test___init___dict_postgres(self):
        temp_name = "".join(random.choices(string.ascii_lowercase, k=6)) + ".db"
        url = "postgresql:///" + self.tmp_dir_path + "/" + temp_name

        db_crud = DatabaseCRUD(url, TEST_MODEL)

        self.assertEqual(db_crud._model_def, TEST_MODEL)
        self.assertEqual(str(db_crud.engine.url), url)
        self.assertIsNone(db_crud._model)

    def test___init___dict_invalidurl(self):
        temp_name = "".join(random.choices(string.ascii_lowercase, k=6)) + ".db"
        url = "other:///" + self.tmp_dir_path + "/" + temp_name

        db_crud = self.assertRaises(
            ValueError,
            DatabaseCRUD,
            url,
            TEST_MODEL,
        )

    @patch("processor_tools.db_crud.read_config")
    def test___init___path(self, mock_read_config):
        temp_name = "".join(random.choices(string.ascii_lowercase, k=6)) + ".db"
        url = "sqlite:///" + self.tmp_dir_path + "/" + temp_name

        dummy_path = "path/to/model.yaml"
        db_crud = DatabaseCRUD(url, dummy_path)

        mock_read_config.assert_called_once_with(dummy_path)
        self.assertEqual(db_crud._model_def, mock_read_config.return_value)
        self.assertEqual(str(db_crud.engine.url), url)
        self.assertIsNone(db_crud._model)

    @patch("processor_tools.db_crud.DatabaseCRUD._create_model")
    def test___model(self, mock_cm):
        temp_name = "".join(random.choices(string.ascii_lowercase, k=6)) + ".db"
        url = "sqlite:///" + self.tmp_dir_path + "/" + temp_name

        db_crud = DatabaseCRUD(url, TEST_MODEL)
        self.assertIsNone(db_crud._model)

        model = db_crud.model

        mock_cm.assert_called_once_with(TEST_MODEL)
        self.assertEqual(db_crud._model, mock_cm.return_value)

        self.assertEqual(model, mock_cm.return_value)

    @patch("processor_tools.db_crud.create_engine")
    def test__engine(self, mock_eng):
        temp_name = "".join(random.choices(string.ascii_lowercase, k=6)) + ".db"
        url = "sqlite:///" + self.tmp_dir_path + "/" + temp_name

        db_crud = DatabaseCRUD(url, TEST_MODEL)
        self.assertIsNone(db_crud._engine)

        engine = db_crud.engine

        mock_eng.assert_called_once_with(make_url(url))
        self.assertEqual(db_crud._engine, mock_eng.return_value)

        self.assertEqual(engine, mock_eng.return_value)

    @patch(
        "processor_tools.db_crud.DatabaseCRUD._map_column_type", return_value=Integer
    )
    def test__return_mapped_column(self, mock_type):

        column_def = {"type": int, "foreign_key": "tbl.clm"}

        mapped_column = DatabaseCRUD._return_mapped_column(column_def)

        self.assertTrue(isinstance(mapped_column, sqlalchemy.orm.MappedColumn))
        self.assertTrue(isinstance(mapped_column.column.type, Integer))
        self.assertEqual(len(mapped_column.column.foreign_keys), 1)

    def test__map_column_type(self):
        self.assertEqual(DatabaseCRUD._map_column_type(bool), Boolean)
        self.assertEqual(DatabaseCRUD._map_column_type("bool"), Boolean)
        self.assertEqual(DatabaseCRUD._map_column_type(int), Integer)
        self.assertEqual(DatabaseCRUD._map_column_type("int"), Integer)
        self.assertEqual(DatabaseCRUD._map_column_type(float), Float)
        self.assertEqual(DatabaseCRUD._map_column_type("float"), Float)
        self.assertEqual(DatabaseCRUD._map_column_type(str), String)
        self.assertEqual(DatabaseCRUD._map_column_type("str"), String)
        self.assertEqual(DatabaseCRUD._map_column_type(date), Date)
        self.assertEqual(DatabaseCRUD._map_column_type("date"), Date)
        self.assertEqual(DatabaseCRUD._map_column_type(datetime), DateTime)
        self.assertEqual(DatabaseCRUD._map_column_type("datetime"), DateTime)
        self.assertTrue(
            isinstance(
                DatabaseCRUD._map_column_type(shapely.geometry.Point),
                geoalchemy2.Geometry,
            )
        )
        self.assertEqual(
            DatabaseCRUD._map_column_type(shapely.geometry.LineString).geometry_type,
            "LINESTRING",
        )
        self.assertEqual(
            DatabaseCRUD._map_column_type("polygon").geometry_type, "POLYGON"
        )
        self.assertRaises(ValueError, DatabaseCRUD._map_column_type, "hello")

    def test__create_model(self):
        temp_name = "".join(random.choices(string.ascii_lowercase, k=6)) + ".db"
        url = "sqlite:///" + self.tmp_dir_path + "/" + temp_name

        db_crud = DatabaseCRUD(url, TEST_MODEL)

        model = db_crud._create_model(TEST_MODEL)

        # test entry for each table
        self.assertCountEqual(model.keys(), TEST_MODEL.keys())

        # test content of table1
        self.assertEqual(model["table1"].__table__.name, "table1")
        self.assertCountEqual(
            model["table1"].__table__.columns.keys(), ["1id", "column1"]
        )

        # test content of table2
        self.assertEqual(model["table2"].__table__.name, "table2")
        self.assertCountEqual(
            model["table2"].__table__.columns.keys(), ["2id", "column2", "ref_1id"]
        )

    def test__get_model_def_types(self):
        model_def_types = DatabaseCRUD._get_model_def_types(TEST_MODEL)

        self.assertCountEqual(model_def_types, [str, int])

    def test__get_model_types(self):
        temp_name = "".join(random.choices(string.ascii_lowercase, k=6)) + ".db"
        url = "sqlite:///" + self.tmp_dir_path + "/" + temp_name

        db_crud = DatabaseCRUD(url, TEST_MODEL)

        model_types = db_crud._get_model_types()
        self.assertCountEqual(model_types, [Integer, String])

    def test__is_postgis_false(self):
        temp_name = "".join(random.choices(string.ascii_lowercase, k=6)) + ".db"
        url = "sqlite:///" + self.tmp_dir_path + "/" + temp_name

        db_crud = DatabaseCRUD(url, TEST_MODEL)

        self.assertFalse(db_crud._is_postgis())

    def test__is_postgis_true(self):
        temp_name = "".join(random.choices(string.ascii_lowercase, k=6)) + ".db"
        url = "sqlite:///" + self.tmp_dir_path + "/" + temp_name

        db_crud = DatabaseCRUD(url, TEST_MODEL_GEO)

        self.assertTrue(db_crud._is_postgis())

    def test_create_sqlite(self):
        temp_name = "".join(random.choices(string.ascii_lowercase, k=6)) + ".db"
        url = "sqlite:///" + self.tmp_dir_path + "/" + temp_name

        db_crud = DatabaseCRUD(url, TEST_MODEL)

        db_crud.create()

        insp = inspect(db_crud.engine)

        self.assertCountEqual(insp.get_table_names(), ["table1", "table2"])

    def test_create_postgresql(self):
        temp_name = "".join(random.choices(string.ascii_lowercase, k=6))

        url = "postgresql://localhost/" + temp_name

        db_crud = DatabaseCRUD(url, TEST_MODEL)

        db_crud.create()

        insp = inspect(db_crud.engine)

        self.assertCountEqual(insp.get_table_names(), ["table1", "table2"])

        drop_database(url)

    def test_create_postgresql_postgis(self):
        temp_name = "".join(random.choices(string.ascii_lowercase, k=6))

        url = "postgresql://localhost/" + temp_name

        db_crud = DatabaseCRUD(url, TEST_MODEL_GEO)

        db_crud.create()

        insp = inspect(db_crud.engine)

        self.assertCountEqual(insp.get_table_names(), ["table1", "spatial_ref_sys"])

        drop_database(url)

    def test_create_session(self):
        temp_name = "".join(random.choices(string.ascii_lowercase, k=6)) + ".db"
        url = "sqlite:///" + self.tmp_dir_path + "/" + temp_name

        db_crud = DatabaseCRUD(url, TEST_MODEL)

        session = db_crud.create_session()

        self.assertEqual(db_crud.engine, session.bind.engine)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir_path)


if __name__ == "__main__":
    unittest.main()
