from functools import reduce

total_palindromes = lambda lists: reduce(lambda acc, lst: acc + len(list(filter(lambda x: x == x[::-1], lst))), lists,
                                         0)

# Use the functions
lists = [['a', 'n'], ['x', '2', 'ab'], ['refer', 'deed', 'noon']]
total_count = total_palindromes(lists)

print(total_count)