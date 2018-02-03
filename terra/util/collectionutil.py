

# Safely get a value from a list at the provided index, returning None if not found
def safe_get_from_list(l, i):
    try:
        return l[i]
    except IndexError:
        return None
