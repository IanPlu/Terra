

# Return the value n, bounded to the min and max.
def clamp(n, minimum, maximum):
    return max(minimum, min(n, maximum))


# Return the value n, but if it exceeds the max or falls below the limit, return the other bound
def wrap(n, minimum, maximum):
    if n > maximum:
        return minimum
    elif n < minimum:
        return maximum
    else:
        return n


def add_tuples(a, b):
    return tuple(map(sum, zip(a, b)))
