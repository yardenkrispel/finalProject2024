from functools import reduce

calculate_for_all_sublists = lambda list_of_lists: map(
 lambda sublist: reduce(lambda num, x: num + (lambda y: y ** 2)(x), filter(lambda z: z % 2 == 0, sublist), 0),
 list_of_lists)

list_of_lists = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [2, 4, 6]]
result = list(calculate_for_all_sublists(list_of_lists))
print(result)
