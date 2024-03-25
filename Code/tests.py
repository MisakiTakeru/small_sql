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

"""
Function to remove all data in the tables, used to cleanup before a test has been run
"""
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


class TestSingletonDatabaseConnect(unittest.TestCase):
    def setUp(self) -> None:
        self.db_url = "mysql://test:test@127.0.0.1/small_sql"
        self.db = SDC(self.db_url)
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
        
        handler.add_ware('yogurt', 10, 'all new yogurt now with a taste of mint', 'Produce', 60)
        
        session = self.db.get_session()
        yog = session.query(db_class.Ware).first()
        self.assertEqual('yogurt', yog.name)
        self.assertEqual('all new yogurt now with a taste of mint', yog.description)
        self.assertEqual(60, yog.price)
        self.assertEqual(10, yog.stock)
        
        produce = session.query(db_class.Category).first()
        
        self.assertEqual(produce.name, 'Produce')
        
        cleanup(self.session)
    
    def test_add_and_remove_ware_stock(self):
        cleanup(self.session)
        self.engine.connect()
        db_class.Ware.metadata.create_all(self.engine)
        db_class.Category.metadata.create_all(self.engine)

        handler = Datahandler(self.db_url)
        
        handler.add_ware('cheese', 2, 'new super rotten cheese', 'Produce', 1000)

        self.assertRaisesRegex(ValueError, "stock cannot be below 0");\
                               handler.add_ware('cheese', stock =  -4)
    
        handler.add_ware('cheese', stock = 10)
        
        session = self.db.get_session()
        
        cheese = session.query(db_class.Ware).first()
        self.assertEqual(12, cheese.stock)
        
        cleanup(self.session)

    def test_remove_ware(self):
        cleanup(self.session)
        self.engine.connect()
        db_class.Ware.metadata.create_all(self.engine)
        db_class.Category.metadata.create_all(self.engine)

        handler = Datahandler(self.db_url)

        handler.add_ware('cheese', 2, 'new super rotten cheese', 'Produce', 1000)

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
     
        handler.add_ware('cheese', 2, 'new super rotten cheese', 'Produce', 1000)


        
        ware_obj = self.session.query(db_class.Ware).first()
        
        handler.transaction(ware_obj.name, 5)
        
        session = self.db.get_session()
        
        trans_obj = session.query(db_class.Transaction).first()

                
        self.assertEqual(trans_obj.ware_id, ware_obj.id)
        self.assertEqual(trans_obj.amount, 5)
        self.assertEqual(trans_obj.transaction_type, 'buy')
  
        ware_obj = session.query(db_class.Ware).first()
        
        self.assertEqual(ware_obj.stock, 7)

# Tests both multiple transactions, and if ware stock would become less than 0.
    def test_multiple_transactions(self):
        cleanup(self.session)
        self.engine.connect()
        
        db_class.Ware.metadata.create_all(self.engine)
        db_class.Category.metadata.create_all(self.engine)
        db_class.Transaction.metadata.create_all(self.engine)
   
        handler = Datahandler(self.db_url)
        handler.add_ware('fumo', 5, 'very cute', 'Doll', 300)
        handler.add_ware('fumo2', 4, 'even cuter', 'Doll', 500)
        handler.add_ware('fumo3', 8, 'evil looking', 'Doll', 200)
        
        handler.transaction('fumo2', -3)
        handler.transaction('fumo', -1)
        handler.transaction('fumo2', 7)
        handler.transaction('fumo3', -8)
        
        session = self.db.get_session()
        
        ware_id = session.query(db_class.Ware).filter_by(name = 'fumo2').first().id
        
        fumo2_trans1 = session.query(db_class.Transaction).filter_by(ware_id = ware_id).first()
        
        self.assertEqual(fumo2_trans1.transaction_type, 'sell')
        
        fumo2_amount = session.query(db_class.Transaction).filter_by(ware_id = ware_id).all()
        
        self.assertEqual(len(fumo2_amount), 2)
        
        with self.assertRaises(ValueError):
            handler.transaction('fumo3', -3)

    def test_show(self):
        cleanup(self.session)
        self.engine.connect()
        
        db_class.Ware.metadata.create_all(self.engine)
        db_class.Category.metadata.create_all(self.engine)
        db_class.Transaction.metadata.create_all(self.engine)
   
        handler = Datahandler(self.db_url)
        handler.add_ware('fumo', 5, 'very cute', 'Doll', 300)
        handler.add_ware('fumo2', 4, 'even cuter', 'Doll', 500)
        handler.add_ware('fumo3', 8, 'evil looking', 'Doll', 200)
        
        handler.transaction('fumo2', -3)
        handler.transaction('fumo', -1)
        handler.transaction('fumo2', 7)
        handler.transaction('fumo3', -8)
        
        wares = handler.show('Ware')
        categories = handler.show('Category')
        transactions = handler.show('Transaction', 'amount',' <  ', 0)
        
        
        self.assertEqual(len(wares), 3)
        self.assertEqual(len(categories), 1)
        self.assertEqual(len(transactions), 3)

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
