class Animal:
    def __init__(self, name): # Initialize the name attribute
        self.name = name

class Dog(Animal):
    def __init__(self, name):
        super().__init__(name)  # Call the constructor of Animal to set the name

d = Dog("Rex")
print(d.name)
