from db_class import Ware, Category, Transaction

class Factory:
    def __init__(self, item_type=None):
    
        self.type_map = {
            "ware" : Ware,
            "category" : Category,
            "transaction"  : Transaction,
        }
    
        if not item_type in self.type_map:
            raise AttributeError(f'input {item_type} is not a valid type')
        else:
            self.item_type = item_type
    
    def create(self, data_dict=None, **kwargs):
        if data_dict is not None:
            kwargs.update(data_dict)
        return self.type_map[self.item_type](**kwargs)