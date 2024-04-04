# Q12
from functools import reduce

nums = [1, 2, 3, 4, 5, 6]

print(reduce(lambda x, y: x + y, map(lambda num: num ** 2, filter(lambda num: num % 2 == 0, nums))))

