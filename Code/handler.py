from sdc import SingletonDatabaseConnect as SDC
import db_class
from factory import Factory
import time
from datetime import datetime

class Datahandler:
    
    def __init__(self, db_url):
        self.db_url = db_url
        self.db = SDC(db_url)
        self.session = self.db.get_session()
        self.engine = self.db.get_engine()
    
    
    def add_ware(self, name,  stock = 0, desc = '', price = -1):
        session = self.session
        try:
            ware_obj = session.query(db_class.Ware).filter_by(name = name).first()
            if ware_obj == None:
                if stock < 0:
                    raise ValueError("stock cannot be below 0")
                elif desc == '':
                    raise ValueError("When creating a new item, description must not be empty")
                elif price < 0:
                    raise ValueError("We are not a charity, price must be 0 or higher")
                    
                ware = Factory('ware').create({'name' : name, 'desc' : desc, 
                                              'price' : price, 'stock' : stock})
                session.add(ware)
            else:
                if (ware_obj.stock + stock) < 0:
                    raise ValueError("stock cannot be below 0")
                ware_obj.stock += stock
            session.commit()
            session.close()
            return True
        
        except Exception as e:
            return e
    
    def remove_ware(self, name):
        session = self.session
        res = session.query(db_class.Ware).filter_by(name = name).delete()
        session.commit()
        session.close()
        return res
    
    
    
    def transaction(self, ware_id, amount):
        if amount == 0:
            raise ValueError('for a transaction to happen the change must not be 0')
        elif amount > 0:
            trans_type = 'buy'
        else:
            trans_type = 'sell'
        session = self.session
        
        ware_obj = session.query(db_class.Ware).filter_by(id = ware_id).first()
        
        if ware_obj == None:
            raise KeyError('given key does not exist in the database')
        elif (ware_obj.stock + amount) < 0:
            raise ValueError('We cannot sell more than we have left')
        
        ware_obj.stock += amount
        transact = Factory('transaction').create({'ware_id' : ware_id, 'amount' :
                            amount, 'trans_type' : trans_type})
        session.add(transact)
        session.commit()
        session.close()
        
        return        
