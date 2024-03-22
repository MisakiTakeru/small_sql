import unittest
from factory import Factory
from sdc import SingletonDatabaseConnect as SDC
from handler import Datahandler
import db_class
import time
from pprint import pprint
import pymysql
from  sqlalchemy_utils import database_exists, create_database, drop_database

pymysql.install_as_MySQLdb()

if not database_exists("mysql://test:test@127.0.0.1/small_sql"):
    create_database("mysql://test:test@127.0.0.1/small_sql")

def cleanup(session):
        try:
            session.query(db_class.Ware).delete()
        except:
            pass
        try:
            session.query(db_class.Category).delete()
        except:
            pass
        try:
            session.query(db_class.Transaction).delete()
        except:
            pass
        session.commit()   

class TestData(unittest.TestCase):
    def __init__(self):

        self.user_data = {
            "name": "John Doe",
            "address": "1234 Main St",
            "email": "john@doe.com",
            #"book_statuses": [db_class.BookStatus(**{"timestamp": 1633027442, "user_id": 1, "book_id": 1, "status_borrowed": False, "status_reserved": False, "status_available": True})]
        }
        self.other_user_data = {
            "name": "Jane Doe",
            "address": "1234 Main St",
            "email": "jane@doe.com",
            #"book_statuses": [db_class.BookStatus(**{"timestamp": 1633027442, "user_id": 2, "book_id": 1, "status_borrowed": False, "status_reserved": False, "status_available": True})]
        }

        self.book_data = {
            "isbn": "123",
            "title": "John Book",
            "author": "John Doe",
            "release_date": 1619827200,
            #"book_statuses": [db_class.BookStatus(**{"timestamp": 1633027442, "user_id": 0, "book_id": 0, "status_borrowed": False, "status_reserved": False, "status_available": True})]
        }

        self.other_book_data = {
            "isbn": "1234",
            "title": "Jane Book",
            "author": "Jane Doe",
            "release_date": 1619827200,
            #"book_statuses": [db_class.BookStatus(**{"timestamp": 1633027442, "user_id": 2, "book_id": 2, "status_borrowed": False, "status_reserved": False, "status_available": True})]
        }

class TestSingletonDatabaseConnect(unittest.TestCase):
    def setUp(self) -> None:
        self.db_url = "mysql://test:test@127.0.0.1/small_sql"
        self.db = SDC(self.db_url)
        self.data = TestData()
        self.user_data = self.data.user_data
        self.other_user_data = self.data.other_user_data
        self.book_data = self.data.book_data
        self.other_book_data = self.data.other_book_data
        self.engine = self.db.get_engine()
        self.session = self.db.get_session()

    def test_singleton(self):
        db = SDC(self.db_url)
        self.assertEqual(self.db, db)
    
    def test_get_session(self):
        session = self.db.get_session()
        self.assertIsNotNone(session)

    def test_wrong_factory_type(self):
        with self.assertRaises(AttributeError):
            Factory('test')
        
    def test_engine_is_singleton(self):
        db1 = SDC(self.db_url)
        db2 = SDC(self.db_url)
        engine1 = db1.get_engine()
        engine2 = db2.get_engine()
        self.assertIs(engine1, engine2)

    def test_database_exists(self):
        self.assertTrue(database_exists(self.db_url))

    def test_add_ware(self):
        cleanup(self.session)
        self.engine.connect()
        db_class.Ware.metadata.create_all(self.engine)
        db_class.Category.metadata.create_all(self.engine)
        handler = Datahandler(self.db_url)
        
        handler.add_ware('yogurt', 10, 'all new yogurt now with a taste of mint', 60)
        
        yog = self.session.query(db_class.Ware).first()
        self.assertEqual('yogurt', yog.name)
        self.assertEqual('all new yogurt now with a taste of mint', yog.description)
        self.assertEqual(60, yog.price)
        self.assertEqual(10, yog.stock)
        
        cleanup(self.session)
    
    def test_add_and_remove_ware_stock(self):
        cleanup(self.session)
        self.engine.connect()
        db_class.Ware.metadata.create_all(self.engine)
        db_class.Category.metadata.create_all(self.engine)

        handler = Datahandler(self.db_url)
        
        handler.add_ware('cheese', 2, 'new super rotten cheese', 1000)

        self.assertRaisesRegex(ValueError, "stock cannot be below 0");\
                               handler.add_ware('cheese', stock =  -4)
    
        handler.add_ware('cheese', stock = 10)
        
        cheese = self.session.query(db_class.Ware).first()
        self.assertEqual(12, cheese.stock)
        
        cleanup(self.session)

    def test_remove_ware(self):
        self.engine.connect()
        db_class.Ware.metadata.create_all(self.engine)
        db_class.Category.metadata.create_all(self.engine)

        handler = Datahandler(self.db_url)

        handler.add_ware('cheese', 2, 'new super rotten cheese', 1000)

# Remove a row, with name cheese and fail to get it.
        trueval = handler.remove_ware('cheese')
                
        nonetype = self.session.query(db_class.Ware).filter_by(name = 'cheese').first()

# Test removing a row that no longer exists.
        falseval = handler.remove_ware('cheese')
        
        self.assertEqual(trueval, 1)
        self.assertEqual(falseval, 0)
        self.assertEqual(nonetype, None)

    def test_transaction(self):
        cleanup(self.session)
        self.engine.connect()
        db_class.Ware.metadata.create_all(self.engine)
        db_class.Category.metadata.create_all(self.engine)
        db_class.Transaction.metadata.create_all(self.engine)
   
        handler = Datahandler(self.db_url)
     
        handler.add_ware('cheese', 2, 'new super rotten cheese', 1000)
        
        ware_obj = self.session.query(db_class.Ware).first()
        
        handler.transaction(ware_obj.id, 5)
        
        trans_obj = self.session.query(db_class.Transaction).first()
        print(trans_obj)
        
        self.assertEqual(trans_obj.ware_id, ware_obj.id)
        self.assertEqual(trans_obj.amount, 5)
        self.assertEqual(trans_obj.transaction_type, 'buy')        


class CustomTestResult(unittest.TextTestResult):
    def printErrors(self):
        self.stream.writeln("Passed: {}".format(self.testsRun - len(self.failures) - len(self.errors)))
        self.stream.writeln("Failed: {}".format(len(self.failures)))
        self.stream.writeln("Errors: {}".format(len(self.errors)))
        super().printErrors()

class CustomTestRunner(unittest.TextTestRunner):
    resultclass = CustomTestResult

if __name__ == '__main__':
    unittest.main(testRunner=CustomTestRunner())
