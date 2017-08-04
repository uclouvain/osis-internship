def difference(first_list, second_list):
    return [item for item in first_list if item not in second_list]

def flatten(list_of_lists):
    return [y for x in list_of_lists for y in x]
