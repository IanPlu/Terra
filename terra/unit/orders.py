

# An order to be carried out by a unit.
class Order:
    def __init__(self, unit, name):
        self.unit = unit
        self.name = name


# An order to move to a specific tile
class MoveOrder(Order):
    # dx, dy: The destination x and y grid coordinates
    def __init__(self, unit, name, dx, dy):
        super().__init__(unit, name)
        self.dx = dx
        self.dy = dy


# An order to conduct a ranged attack on a specific tile
class RangedAttackOrder(Order):
    # tx, ty: The targeted grid coordinates to attack
    def __init__(self, unit, name, tx, ty):
        super().__init__(unit, name)
        self.tx = tx
        self.ty = ty
