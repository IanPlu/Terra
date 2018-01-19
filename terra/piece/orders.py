

# An order to be carried out by a piece.
class Order:
    def __init__(self, piece, name):
        self.piece = piece
        self.name = name


# An order to move to a specific tile
class MoveOrder(Order):
    # dx, dy: The destination x and y grid coordinates
    def __init__(self, piece, name, dx, dy):
        super().__init__(piece, name)
        self.dx = dx
        self.dy = dy

    def __str__(self):
        return "Order: Move to ({}, {})".format(self.dx, self.dy)


# An order to conduct a ranged attack on a specific tile
class RangedAttackOrder(Order):
    # tx, ty: The targeted grid coordinates to attack
    def __init__(self, piece, name, tx, ty):
        super().__init__(piece, name)
        self.tx = tx
        self.ty = ty

    def __str__(self):
        return "Order: Ranged attack tile ({}, {})".format(self.tx, self.ty)
