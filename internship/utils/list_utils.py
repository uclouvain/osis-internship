def difference(first_list, second_list):
    second_set = set(second_list)
    return [item for item in first_list if item not in second_set]
