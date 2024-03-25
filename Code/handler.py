from sdc import SingletonDatabaseConnect as SDC
import db_class
from factory import Factory
import time
from datetime import datetime
from enum import Enum
from pprint import pprint
import operator

"""
Enumerator class for showing all columns of a table
"""
class db_classes(Enum):
    ware = db_class.Ware
    category = db_class.Category
    transaction = db_class.Transaction

"""
Handler class for handling all the different calls.

When created it needs to be given a url for logging in and managing a session.
"""
class Datahandler:
    
    def __init__(self, db_url):
        self.db_url = db_url
        self.db = SDC(db_url)
        self.session = self.db.get_session()
        self.engine = self.db.get_engine()
    

#add_ware is a function that takes a name, stock, description, category and price
#and creates a new column in the ware table, but if it already exists instead adds
#stock to that column.

    def add_ware(self, name,  stock = 0, desc = '', category = '', price = -1):
        session = self.session
        try:
            ware_obj = session.query(db_class.Ware).filter_by(name = name).first()
            if ware_obj == None:
                if stock < 0:
                    raise ValueError("stock cannot be below 0")
                elif desc == '':
                    raise ValueError("When creating a new item, description must not be empty")
                elif category == '':
                    raise ValueError("Ware must have a category")
                elif price < 0:
                    raise ValueError("We are not a charity, price must be 0 or higher")

                self.__add_ware__(name, stock, desc, category, price)
#                ware = Factory('ware').create({'name' : name, 'desc' : desc, 
#                                              'price' : price, 'category' : 
#                                                  category, 'stock' : stock})
#                session.add(ware)
#                session.commit()
         
                self.__add_category__(category, 'nope')
            else:
                if (ware_obj.stock + stock) < 0:
                    raise ValueError("stock cannot be below 0")
                ware_obj.stock += stock
                session.commit()
            session.close()
            return True
        
        except Exception as e:
            return e

    def __add_ware__(self, name, stock, desc, category, price):
        session = self.session
        ware = Factory('ware').create({'name' : name, 'desc' : desc, 
                                              'price' : price, 'category' : 
                                                  category, 'stock' : stock})
        session.add(ware)
        session.commit()
        session.close()

        
    def __add_category__(self, name, desc):
        session = self.session
        cat_obj = session.query(db_class.Category).filter_by(name = name).first()

# If the category does not exist yet create it
        if cat_obj == None:
            cat = Factory('category').create({'name' : name, 'desc' : 'not added yet'})
                    
            session.add(cat)
            session.commit()
        session.close()
        

#remove_ware tries to remove a column in ware given by name, and returns the result.
    
    def remove_ware(self, name):
        session = self.session
        res = session.query(db_class.Ware).filter_by(name = name).delete()
        session.commit()
        session.close()
        return res
    
    

# transaction makes a transaction change to the stock of the ware_id by the amount
# specified, and creates a new column in the transaction table of what occured.

    def transaction(self, name, amount):
        if amount == 0:
            raise ValueError('for a transaction to happen the change must not be 0')
        elif amount > 0:
            trans_type = 'buy'
        else:
            trans_type = 'sell'
        session = self.session
        
        ware_obj = session.query(db_class.Ware).filter_by(name = name).first()
        
        if ware_obj == None:
            raise KeyError('given key does not exist in the database')
        elif (ware_obj.stock + amount) < 0:
            raise ValueError('We cannot sell more than we have left')
        
        ware_obj.stock += amount
        change = -1 * (amount * ware_obj.price)
        transact = Factory('transaction').create({'ware_id' : ware_obj.id, 'amount' :
                            amount, 'trans_type' : trans_type, 'change' : change})
        session.add(transact)
        session.commit()
        session.close()
        
        return True

# Want to add filter criteria.
    def show(self, table, key = None, comp = None, cond = None):
        try:
            table_class = db_classes[table.lower()].value
        except Exception:
            raise KeyError('given table name is not in db')
        session = self.session
        if key != None and cond != None and comp != None:
            comp = comp.strip()
            if comp == 'less' or comp == '<':
                objs = session.query(table_class).filter(getattr(table_class, key) < cond)
            elif comp == 'equal' or comp == '=':
                objs = session.query(table_class).filter(getattr(table_class, key) == cond)
            elif comp == 'greater' or comp == '>':
                objs = session.query(table_class).filter(getattr(table_class, key) > cond)
            else:
                raise AttributeError(f'comparison has no {comp} function.')
        else:
            objs = session.query(table_class).all()
        data = []
        for o in objs:
            o_data = dict(vars(o))
            data.append(o_data)
#        pprint(data)
        session.close()
        return data
        
        
