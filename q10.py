# Q10

from functools import reduce
custom_join = lambda temp_lst: reduce(lambda x,y: x + " " + y, temp_lst)
lst2 = ["apple", "banana", "cherry"]
print(custom_join(lst2))