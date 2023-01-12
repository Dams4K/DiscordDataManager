from primary_class import *

class Item(Data):
    def __init__(self, name = "no name", description = "no description", price = 0):
        super().__init__()
        self.name = name
        self.description = description
        self.price = price


class Inventory(Data):
    def __init__(self):
        super().__init__()
        self.items = []
        self._items_element_type = Item
    
    @Data.update
    def add_item(self, item: Item):
        # self.items.append(item)
        print("sqsd")

class MemberData(Saveable):
    def __init__(self, member_id):
        super().__init__(f"tests/members/{member_id}.json")

        self.level = 0
        self.xp = 0
        self.inventory = Inventory()
    

member_data = MemberData(1)
item = Item("Book", description="A wonderful book")
member_data.inventory.add_item(item)