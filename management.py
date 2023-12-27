import inspect
import json
import os
from itertools import chain

class Data():
    __slots__ = ()
    __dversion = 1
    BYPASS_UNKNOWN_VARIABLES = False

    def export_data(self):
        """A method used to export a class that inherite of Data, all its attributs

        Returns
        -------
            dict
        """
        data = {"__dversion": self.__dversion}
        for attr_name in self.get_saveable_attrs():
            attr = getattr(self, attr_name)
            if isinstance(attr, Data):
                attr = attr.export_data()

            elif isinstance(attr, list):
                final_list = []
                for i in range(len(attr)):
                    attr_element = attr[i]
                    if isinstance(attr_element, Data):
                        attr_element = attr_element.export_data()
                    
                    final_list.append(attr_element)
                attr = final_list
            
            elif isinstance(attr, dict):
                final_dict = {}
                for sub_attr_key, sub_attr_value in attr.items():
                    if isinstance(sub_attr_value, Data):
                        sub_attr_value = sub_attr_value.export_data()
                    
                    final_dict[sub_attr_key] = sub_attr_value
                attr = final_dict
            

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
        if not isinstance(clazz, Data):
            return data

        dv0 = data.get("__dversion", 1)
        data = clazz.convert_version(data)
        dv1 = data.get("__dversion", 1)

        for attr_name, attr_data in data.items():
            if not hasattr(clazz, attr_name):
                if getattr(clazz, "BYPASS_UNKNOWN_VARIABLES", False):
                    setattr(clazz, attr_name, None)
                else:
                    continue
            
            class_attr = getattr(clazz, attr_name)

            if isinstance(attr_data, list):
                if not isinstance(class_attr, list):
                    print(f"Unable load '{attr_name}' attribue, format differs between data file and class. The data attribute should be {type(class_attr)} but is {type(attr_data)}")
                    continue

                final_list = []
                for element_data in attr_data:
                    element_clazz = getattr(clazz, f"_{attr_name}_type", None)
                    final_list.append(Data.import_data(element_data, element_clazz))
                setattr(clazz, attr_name, final_list)
            
            elif isinstance(attr_data, dict):
                if isinstance(class_attr, Data):
                    # attr_data is an exported class
                    setattr(clazz, attr_name, Data.import_data(attr_data, class_attr))
                else:
                    # Normal python dict
                    final_dict = {}
                    for key, value in attr_data.items():
                        value_clazz = getattr(clazz, f"_{attr_name}_type", None)
                        final_dict[key] = Data.import_data(value, value_clazz)
                    setattr(clazz, attr_name, final_dict)

            else:
                setattr(clazz, attr_name, attr_data)
        
        if isinstance(clazz, Saveable) and dv0 != dv1:
            clazz.save()

        return clazz
    
    @staticmethod
    def convert_version(data):
        """Convert old version dataset to the new version dataset
        
        Parameters
        ----------
            data: list | dict

        Returns
        -------
            list | dict
        """
        return data

    def __repr__(self):
        attrs = [(attr_name, getattr(self, attr_name)) for attr_name in self.get_saveable_attrs()]
        inner = ' '.join("%s=%r" % t for t in attrs)
        return f'<{self.__class__.__name__} {inner}>'
    
    def get_saveable_attrs(self):
        attrs = []
        if not getattr(self, "__slots__", None) is None:
            slots = chain.from_iterable(getattr(cls, '__slots__', []) for cls in self.__class__.__mro__)
            attrs.extend([attr for attr in slots if not attr.startswith("_")])
        if not getattr(self, "__dict__", None) is None:
            attrs.extend([attr for attr in self.__dict__ if not attr.startswith("_")])
        
        return attrs


class Saveable(Data):
    __slots__ = ("_path", "_tmp_backup_path")

    def __new__(cls, *args, **kwargs):
        inst_id = "-".join([str(arg) for arg in args])
        if not hasattr(cls, f"instance_{inst_id}"):
            setattr(cls, f"instance_{inst_id}", super(Saveable, cls).__new__(cls))
        return getattr(cls, f"instance_{inst_id}")

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
        
        if os.path.exists(self._tmp_backup_path) and os.path.exists(self._path):
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

    @property
    def file_exist(self):
        return os.path.exists(self._path)

    def delete(self):
        if self.file_exist:
            os.remove(self._path)

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

        if inspect.iscoroutinefunction(func):
            async def decorator(*func_args, **func_kwargs):
                clazz = func_args[0]
                if load:
                    clazz.load()

                result = await func(*func_args, **func_kwargs)
                
                if save:
                    clazz.save()
                return result
        else:
            def decorator(*func_args, **func_kwargs):
                clazz = func_args[0]
                if load:
                    clazz.load()

                result = func(*func_args, **func_kwargs)
                
                if save:
                    clazz.save()
                return result
            
        return decorator