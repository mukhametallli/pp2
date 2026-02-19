class Person:
    species = "Human"   # Class attribute (shared by all instances of the class)

p1 = Person()
p2 = Person()

print(p1.species)
print(p2.species)
