from primary_class import *

class Item(Data):
    def __init__(self, name = "no name", description = "no description", price = 0):
        super().__init__()
        self.name = name
        self.description = description
        self.price = price

        self.to_save = [
            "name",
            "description",
            "price"
        ]

class Inventory(Data):
    def __init__(self):
        super().__init__()
        self.items = []
        self.items_element_type = Item
        self.to_save = [
            "items"
        ]
    
    def add_item(self, item: Item):
        self.items.append(item)

class MemberData(Saveable):
    def __init__(self, member_id):
        super().__init__(f"tests/members/{member_id}.json")

        self.level = 0
        self.xp = 0
        self.inventory = Inventory()

        self.to_save = [
            "level",
            "xp",
            "inventory"
        ]
    

member_data = MemberData(1)
apple = Item("Apple")
member_data.inventory.add_item(apple)
# print(member_data.inventory.items)
# member_data.xp += 100
# # print(member_data.export_data())
# member_data.save()


# del member_data

member_data_loaded = MemberData(1)
member_data_loaded.load()
print(member_data_loaded)