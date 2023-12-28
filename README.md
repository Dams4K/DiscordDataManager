# Okay so, wtf is this?

I'm a little weird, and sometimes I like to reinvent the wheel. So this is essentially something to save data. No, I don't want to use sqlite for my discord bots, so here we save using json.

> [!CAUTION]
> I'm not perfect, so i do not guarantee this code. It's working for me, but maybe one day i'll find a big issue with this workflow.

But for now, it's working pretty well :)

Sorry for my bad English, I don't feel like spending time checking if it's grammatically correct ahha. And no one will ever read this sooo, i'm safe

## How to use this

Create a class you want to save, child of Saveable
```python
from ddm import Saveable

class Class2Save(Saveable):
    def __init__(self):
        self.a = 0
        self.b = "hello guys"

        super().__init__("my/super/path/to/thefile.json")
```

Now, if you want to load your class, just call the method `load` with your class instance. To save, use the method `save`:

```python
myinstance = Class2Save()

myinstance.load()
myinstance.a = 15
myinstance.save()
```

okay but it's annoying to do load and save everytime manually, so you can create a setter to the variables of the class, and you need to add the decorator `@Saveable.update()`:

```python
class Class2Save(Saveable):
    ...

    @Saveable.update()
    def set_a(self, value):
        self.a = value
    
    @Saveable.update()
    def set_b(self, value):
        self.b = value
```

Everything is taken care of by the decorator. No manual loading of saving. Pretty neat hu?

```python
myinstance = Class2Save()
myinstance.set_a(15) # Same result as before, but more compact
```

## But hey, what if i have 2 instances of my class ?

Yeah, if you're asking that question, i think you've found an issue. For those who don't get it, imagine you have this:

```python
myi1 = Class2Save()
myi2 = Class2Save()
```

what if you do 
```python
myi1.set_a(15)
myi2.set_b("uuuuu")
```
You'll have the file updated to have `a = 15`, but just after, you save again with `b = "uuuuu"` overwritting `a`. But no, because everytime you call a method with the decorator `@Saveable.update()`, the file is loaded before updating the variable. (If you don't want to load the file everytime a modification is made, you can add the argument `load=False` to the decorator: `Saveable.update(load=False)`)

> \- "But what happens if the decorator loads the file just before rewriting it? There will always be a loss!"
>
> *Some random programmer reading this readme file*

To which I reply, "That's not my problem, as I said. It's not guaranteed."

Joking aside, in reality you can't create multiple instances of a class that inherits from `Saveable`. `myi1` is literally the same as `myi2`. So when you do `myi1.a = 15`, `myi2.a` will also become `15`. This way, no problems should arise.

> \- " But what if i want to use the same class for my members :'(<br>
> I need different instances because my members are different too :'''( "
>
> *A sad programmer reading this readme file*

Yeah, that sucks.

Do you know something? I've been facing this problem for a while now, and I don't have a solution. Have a great day!

Okay, maybe I lied. In your init, add in the arguments the id of your member:

```python
def init(self, member_id):
    ...
```

Everything will be okay and will work well :)

## Will it work well with asynchronous functions?

Yes.

## And what about slots?

Yes.

## And what if i make changes to the python class?

YEAH, that sucks too.

If you just add variables, there's no problem. If you delete variables, all you'll have is useless data saved in the json file.

**BUT** what if you want to rename a variable, and conserve the data? EEEEEEEE

```python
class Classe2Save(Saveable):
    ...

    @staticmethod
    def convert_version(data: dict) -> dict:
        return data
```
So there is this method in the class `Saveable`. All it does, is returning the arg `data`. This method is called when the data is loaded as a dict by json, just before it's used to load the class with the correct values.

So by overriding the method `convert_version` you can convert data from an old class to a new class. Every class that inherit from `Data` (the parent of `Saveable`) has the variable `__dversion`. By default it's set a 1 and i always saved into the json file. So by using it, you can detect if you are loading an outdated file:

```python
class Class2Save(Saveable):
    __dversion = 2
    ...

    @staticmethod
    def convert_version(data: dict) -> dict:
        if data.get("__dversion") == 1:
            data["__dversion"] = 2
            data["a"] = str(data["a"]) # Now variable a will be a string
        
        return data
```

## Hey you dumbass, what if i stop the program when it's saving a class?

OH NO, MY ONLY WEAKNESS