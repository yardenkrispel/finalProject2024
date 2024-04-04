# Q11

from functools import reduce

calculate_square = lambda y: y ** 2
is_even = lambda z: z % 2 == 0
sum_square = lambda num, x: num + calculate_square(x)
cumulative_sum_of_squares = lambda sublist: reduce(sum_square, filter(is_even, sublist), 0)  # 0 is the first num
calculate_for_all_sublists = lambda list_of_lists: map(cumulative_sum_of_squares, list_of_lists)

list_of_lists = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [2, 4, 6]]
result = list(calculate_for_all_sublists(list_of_lists))
print(result)
