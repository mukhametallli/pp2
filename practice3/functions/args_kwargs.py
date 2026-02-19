def show_args(*args): # Function with *args (variable number of positional arguments)
    print(args)

show_args(1, 2, 3)


def show_kwargs(**kwargs):  # Function with **kwargs (variable number of keyword arguments)
    print(kwargs)

show_kwargs(name="Anel", age=18)
