# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Float, JSON, Boolean, ForeignKey, DATETIME
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

# Declares the 3 table classes in my database.
# My database value acquisition is set to lazy. This means that select is first
# used, when direct access to a table value is declared. This is done to 
# minimize sql calls.

Base = declarative_base()

class Ware(Base):
    __tablename__ = 'Ware'
    
    id = Column(Integer, primary_key = True)
    name = Column(String(30))
    description = Column(String(100))
    price = Column(Integer)
    stock = Column(Integer)
    category_id = Column(Integer, ForeignKey('Category.id'))
    
    category = relationship('Category', back_populates = 'ware')
    
    def __init__(self, name, desc, price, stock = 0):
        self.name = name
        self.description = desc
        self.price = price
        self.stock = stock

class Category(Base):
    __tablename__ = 'Category'
    
    id = Column(Integer, primary_key = True)
    name = Column(String(30))
    description = Column(String(100))
    
    ware = relationship('Ware', back_populates = 'category')

    def __init__(self, name, desc):
        self.name = name
        self.description = desc

class Transaction(Base):
    __tablename__ = 'Transaction'
    
    id = Column(Integer, primary_key = True)
    ware_id = Column(Integer, ForeignKey('Ware.id'))
    time = Column(DATETIME, default = datetime.now)
    amount = Column(Integer)
    transaction_type = Column(String(30))
    
    def __init__(self, ware_id, amount, trans_type):
        self.ware_id = ware_id
        self. amount = amount
        self.transaction_type = trans_type

