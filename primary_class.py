import os
import json
import imaplib

class Data:
    def __init__(self):
        self.to_save = []
    

    def retrieve_data(self):
        data = {"__type": [base.__name__ for base in self.__class__.__bases__]}
        for attr_name in self.to_save:
            attr = getattr(self, attr_name)
            if isinstance(attr, Data):
                attr = attr.retrieve_data()
            elif isinstance(attr, list):
                attr_list = []
                for i in range(len(attr)):
                    attr_element = attr[i]
                    if isinstance(attr_element, Data):
                        attr_element = attr_element.retrieve_data()
                    
                    attr_list.append(attr_element)
                attr = attr_list
            
            data[attr_name] = attr

        return data
    

    def insert_data(self, data: dict):
        for attr_name, attr_data in data.items():
            if self.__class__.__name__ in attr_data.get("__type", None):
                pass
            
            setattr(self, attr_name, attr_data)


class Saveable(Data):
    def __init__(self, path):
        super().__init__()
        self.path = path

    def save(self):
        self.create_needed_dirs()
        with open(self.path, "w") as f:
            json.dump(self.retrieve_data(), f, indent=4)

    def load(self):
        self.create_needed_dirs()
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                self.insert_data(json.load(f))

    
    def create_needed_dirs(self):
        dirname = os.path.dirname(self.path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)