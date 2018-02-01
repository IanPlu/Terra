

# Safely get a value from a list at the provided index, returning None if not found
def safe_get_from_list(list, index):
    try:
        return list[index]
    except IndexError:
        return None
