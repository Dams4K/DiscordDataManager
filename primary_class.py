import os
import json

class Saveable:
    def __init__(self, path):
        self.to_save = []

    def retrieve_data(self):
        return {attr_name: getattr(self, attr_name) for attr_name in self.to_save}

    def save(self):
        pass
    def load(self):
        pass

    
    def create_dirs(self):
        dirname = os.path.dirname(self.file_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)