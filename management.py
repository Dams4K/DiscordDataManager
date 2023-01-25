import os
import json

class Data:
    def export_data(self):
        data = {"__type": self.__class__.__name__}
        for attr_name in self.get_saveable_attrs():
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
    
    @staticmethod
    def import_data(data, clazz):
        """A static function used to import data
        
        Parameters
        ----------
            data: dict
                Data to import into the class

            clazz: object
                An instance of the class
        """
        if not isinstance(data, dict):
            return data

        for attr_name, attr_data in data.items():
            if attr_name == "__type": continue
            class_attr = getattr(clazz, attr_name)

            if isinstance(attr_data, dict) and class_attr.__class__.__name__ == attr_data.get("__type", None):
                Data.import_data(attr_data, class_attr)

            elif isinstance(attr_data, list):
                final_list = []
                for element_data in attr_data:
                    element_clazz = getattr(clazz, f"_{attr_name}_type", None)
                    final_list.append(Data.import_data(element_data, element_clazz))
                setattr(clazz, attr_name, final_list)
            
            else:
                setattr(clazz, attr_name, attr_data)
        
        return clazz
        
    def __repr__(self):
        attrs = [(attr_name, getattr(self, attr_name)) for attr_name in self.get_saveable_attrs()]
        inner = ' '.join("%s=%r" % t for t in attrs)
        return f'<{self.__class__.__name__} {inner}>'
    
    def get_saveable_attrs(self):
        return [attr for attr in self.__dict__ if not attr.startswith("_")]


class Saveable(Data):
    def __new__(cls, id, *args, **kwargs):
        if not hasattr(cls, f"instance_{id}"):
            setattr(cls, f"instance_{id}", super(Saveable, cls).__new__(cls))
        return getattr(cls, f"instance_{id}")

    def __init__(self, path, load_at_init = True):
        super().__init__()
        self._path = path
        self._tmp_backup_path = path + "_tmp_backup"
        if load_at_init:
            self.load()

    def create_needed_dirs(self):
        dirname = os.path.dirname(self._path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def save(self, tmp_backup=True):
        self.create_needed_dirs()
        
        if os.path.exists(self._path):
            os.rename(self._path, self._tmp_backup_path)

        with open(self._path, "w") as f:
            json.dump(self.export_data(), f, indent=4)
        
        if os.path.exists(self._tmp_backup_path):
            os.remove(self._tmp_backup_path)

    def load(self):
        self.create_needed_dirs()
        if os.path.exists(self._path):
            try:
                with open(self._path, "r") as f:
                    Data.import_data(json.load(f), self)
            except json.decoder.JSONDecodeError:
                if os.path.exists(self._tmp_backup_path):
                    os.rename(self._tmp_backup_path, self._path)
                    self.load()

    def double_decorator(func: callable):
        """A decorator decorator that is used to allow the decorator to be used as:

            .. code-block:: python3
                @decorator(...)
                #or
                @decorator
        
        Parameters
        ----------
            func: callable
                The function decorator
        
        Example
        -------

            .. code-block:: python3

            @double_decorator
            def dec_name(func: callable, a: int, b: int = 10):
                def decorator(*func_args, **func_kwargs):
                    ...
                    result = func(*func_args, **func_kwargs)
                    ...
                    return result
                return decorator

        """

        def decorator(*args, **kwargs):
            if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
                # called as @decorator
                return func(args[0])
            else:
                # called as @decorator(...)
                return lambda realf: func(realf, *args, **kwargs)
        return decorator

    @double_decorator
    def update(func: callable, load: bool = True, save: bool = True):
        """Update decorator that is used to automatically load and save the class

        Parameters
        ----------
            func: callable
                The function decorated, don't need to be filled
            load: Optional[bool]
                Enable loading
            save: Optional[bool]
                Enable saving
        
        Example
        -------

            .. code-block:: python3

            @Saveable.update
            def add_xp(self, amount: int):
                self.xp += amount
            
            @Saveable.update(load=False)
            def add_level(self, amount: int):
                self.level += amount
        """

        def decorator(*func_args, **func_kwargs):
            clazz = func_args[0]
            if load:
                clazz.load()

            result = func(*func_args, **func_kwargs)
            
            if save:
                clazz.save()
            return result
        return decorator