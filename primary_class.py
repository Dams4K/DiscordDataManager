import os
import json
import imaplib

class Data:
    def __init__(self):
        self.to_save = []
    

    def export_data(self):
        data = {"__type": self.__class__.__name__}
        for attr_name in self.to_save:
            attr = getattr(self, attr_name)
            if isinstance(attr, Data):
                attr = attr.export_data()
            elif isinstance(attr, list):
                attr_list = []
                for i in range(len(attr)):
                    attr_element = attr[i]
                    if isinstance(attr_element, Data):
                        attr_element = attr_element.export_data()
                    
                    attr_list.append(attr_element)
                attr = attr_list
            
            data[attr_name] = attr

        return data
    

    def import_data(data: dict, clazz):
        if not isinstance(data, dict):
            return

        for attr_name, attr_data in data.items():
            if attr_name == "__type": continue
            class_attr = getattr(clazz, attr_name)

            if isinstance(attr_data, dict) and class_attr.__class__.__name__ == attr_data.get("__type", None):
                Data.import_data(attr_data, class_attr)

            elif isinstance(attr_data, list):
                for element_data in attr_data:
                    if isinstance(element_data, dict) and element_data.get("__type", None):
                        element_clazz = getattr(clazz, attr_name + "_element_type")()
                        Data.import_data(element_data, element_clazz)
                        
                        class_attr.append(element_clazz)
            
            else:
                setattr(clazz, attr_name, attr_data)
        
    def __repr__(self):
        attrs = [(attr_name, getattr(self, attr_name)) for attr_name in self.to_save]
        inner = ' '.join("%s=%r" % t for t in attrs)
        return f'<{self.__class__.__name__} {inner}>'


class Saveable(Data):
    def __init__(self, path):
        super().__init__()
        self.path = path

    def save(self):
        self.create_needed_dirs()
        with open(self.path, "w") as f:
            json.dump(self.export_data(), f, indent=4)

    def load(self):
        self.create_needed_dirs()
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                Data.import_data(json.load(f), self)

    
    def create_needed_dirs(self):
        dirname = os.path.dirname(self.path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)