from terra.event import MENU_MOVE, MENU_RANGED_ATTACK, MENU_BUILD_UNIT


# An order to be carried out by a piece.
class Order:
    def __init__(self, piece, name):
        self.piece = piece
        self.name = name


# An order to move to a specific tile
class MoveOrder(Order):
    # dx, dy: The destination x and y grid coordinates
    def __init__(self, piece, dx, dy):
        super().__init__(piece, MENU_MOVE)
        self.dx = dx
        self.dy = dy

    def __str__(self):
        return "Order: Move to ({}, {})".format(self.dx, self.dy)


# An order to conduct a ranged attack on a specific tile
class RangedAttackOrder(Order):
    # tx, ty: The targeted grid coordinates to attack
    def __init__(self, piece, tx, ty):
        super().__init__(piece, MENU_RANGED_ATTACK)
        self.tx = tx
        self.ty = ty

    def __str__(self):
        return "Order: Ranged attack tile ({}, {})".format(self.tx, self.ty)


# An order to build a piece on a specific tile
class BuildOrder(Order):
    def __init__(self, piece, tx, ty, team, new_unit_type):
        super().__init__(piece, MENU_BUILD_UNIT)
        self.tx = tx
        self.ty = ty
        self.team = team
        self.new_unit_type = new_unit_type

    def __str__(self):
        return "Order: Build a {} piece on tile ({}, {})".format(self.new_unit_type, self.tx, self.ty)
