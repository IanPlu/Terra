

def clamp(n, minimum, maximum):
    return max(minimum, min(n, maximum))


def add_tuples(a, b):
    return tuple(map(sum, zip(a, b)))
