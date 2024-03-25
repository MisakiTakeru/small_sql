from sdc import SingletonDatabaseConnect as SDC
from handler import Datahandler
import db_class
from pprint import pprint
import pymysql
from  sqlalchemy_utils import database_exists, create_database, drop_database

pymysql.install_as_MySQLdb()

if not database_exists("mysql://test:test@127.0.0.1/small_sql"):
    create_database("mysql://test:test@127.0.0.1/small_sql")

class Menu:
    def __init__(self):
        self.db_url = "mysql://test:test@127.0.0.1/small_sql"
        self.db = SDC(self.db_url)
        self.engine = self.db.get_engine()
        self.handler = Datahandler(self.db_url)
        # Create tables
        db_class.Ware.metadata.create_all(self.engine)
        db_class.Category.metadata.create_all(self.engine)
        db_class.Transaction.metadata.create_all(self.engine)

    def print_menu(self):
        print("1. Add Ware")
        print("2. Remove Ware")
        print("3. Make Transaction")
        print("4. Show table")
        print("0. Exit")
    
    def print_show(self):
        print("1. Ware table")
        print("2. Category table")
        print("3. Transaction table") 
        print("0. Go back")

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
        

if __name__ == '__main__':
    m = Menu()
#    cleanup(m.db.get_session())
    while True:
        m.print_menu()
        choice = input('Enter your choice: ')
        
        if choice == '1':
            name = input('What is the name of the new ware? ')
            stock = input('How many of them do we have? ')
            desc = input('What is the description? ')
            category = input('What type of category is it?')
            price = input('what is the wares current price? ')
            m.handler.add_ware(name, int(stock), desc, category, int(price))
        elif choice == '2':
            name = input('What is the name of the ware we no longer have? ')
            m.handler.remove_ware(name)
        elif choice == '3':
            bs = input('how many are we buying or selling (negative number is sell, positive is buy)? ')
            name = input('For what ware is this transaction happening? ')
            m.handler.transaction(name, int(bs))
        elif choice == '4':
            key = None
            op = None
            filtering = None
            fail = 0
            m.print_show()
            new_choice = input('what shall we show? ')
            if new_choice == '1':
                shows = 'ware'
                choice3 = input('do you want to filter? enter 1 for yes. ')
                if choice3 == '1':
                    print('Keys for filters are: id, name, description, price, stock, category')
                    key = input('Which key do you want to use? ')
                    print('Operators are <, > or =')
                    op = input('Which operator do you want to use? ')
                    filtering = input('What shall they be matched with?')
#                    l = m.handler.show(shows, key, op, filtering)
#                    pprint(l)
#                else:
#                    l = m.handler.show(shows)
#                    pprint(l)
            elif new_choice == '2':
                shows = 'category'
                choice3 = input('do you want to filter? enter 1 for yes else press enter. ')                
                if choice3 == '1':
                    print('Keys for filters are: id, name, description')
                    key = input('Which key do you want to use? ')
                    print('Operators are <, > or =')
                    op = input('Which operator do you want to use? ')
                    filtering = input('What shall they be matched with?')
#                    l = m.handler.show(shows, key, op, filtering)
#                    pprint(l)
#                else:
#                    l = m.handler.show(shows)
#                    pprint(l)
            elif new_choice == '3':
                shows = 'transaction'
                choice3 = input('do you want to filter? enter 1 for yes. ')            
                if choice3 == '1':
                    print('Keys for filters are: id, ware_id, time, amount, change, transaction_type')
                    key = input('Which key do you want to use? ')
                    print('Operators are <, > or =')
                    op = input('Which operator do you want to use? ')
                    filtering = input('What shall they be matched with?')
#                    l = m.handler.show(shows, key, op, filtering)
#                    pprint(l)
#                else:
#                    l = m.handler.show(shows)
#                    pprint(l)

            elif new_choice == 0:
                pass
            else:
                print(f'invalid choice. you gave us {new_choice}, and the possible are 1, 2, 3, 0')
                fail = 1
            if not fail:
                l = m.handler.show(shows, key, op , filtering)
                pprint(l)
                
        elif choice == '0':
            break
        else:
            print(f'invalid choice. you gave us {choice}, but the possibilities are 1, 2, 3, 4, 0')