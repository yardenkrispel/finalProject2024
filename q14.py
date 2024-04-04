# Q14
#The generator's purpose is to conserve memory space.
# In the context of Eager evaluation, all data is stored in memory beforehand.
# Conversely, in Lazy evaluation, we calculate each term only when needed, thereby
# avoiding pre-storing everything in memory.

def generate_values():
    print('Generating values...')
    yield 1
    yield 2
    yield 3


def not_generate_values():
    return [1, 2, 3]


def square(x):
    print(f'Squaring {x}')


    return x * x

print('Eager evaluation:')
values = list(generate_values())
squared_values = [square(x) for x in values]
print(squared_values)

print('\nLazy evaluation:')
squared_values = [square(x) for x in generate_values()]
print(squared_values)







