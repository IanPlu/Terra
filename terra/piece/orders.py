from terra.economy.upgradetype import UpgradeType
from terra.menu.option import Option
from terra.piece.piecetype import PieceType
from terra.strings import piece_name_strings, LANGUAGE


# An order to be carried out by a piece.
class Order:
    def __init__(self, name):
        self.name = name

    # Return a string representation of this order.
    def serialize(self):
        return "[null_]"


# An order to move to a specific tile
class MoveOrder(Order):
    # dx, dy: The destination x and y grid coordinates
    def __init__(self, dx, dy):
        super().__init__(Option.MENU_MOVE)
        self.dx = dx
        self.dy = dy

    def __str__(self):
        return "Order: Move to ({}, {})".format(self.dx, self.dy)

    def serialize(self):
        return "[Move_]{},{}".format(self.dx, self.dy)


# An order to conduct a ranged attack on a specific tile
class RangedAttackOrder(Order):
    # tx, ty: The targeted grid coordinates to attack
    def __init__(self, tx, ty):
        super().__init__(Option.MENU_RANGED_ATTACK)
        self.tx = tx
        self.ty = ty

    def __str__(self):
        return "Order: Ranged attack tile ({}, {})".format(self.tx, self.ty)

    def serialize(self):
        return "[Range]{},{}".format(self.tx, self.ty)


# An order to build a piece on a specific tile
class BuildOrder(Order):
    def __init__(self, tx, ty, new_piece_type):
        super().__init__(Option.MENU_BUILD_PIECE)
        self.tx = tx
        self.ty = ty
        self.new_piece_type = new_piece_type

    def __str__(self):
        return "Order: Build a {} on tile ({}, {})".format(
            piece_name_strings[LANGUAGE][self.new_piece_type], self.tx, self.ty)

    def serialize(self):
        return "[Build]{},{},{}".format(self.tx, self.ty, self.new_piece_type.name)


# An order to purchase an upgrade for the team
class UpgradeOrder(Order):
    def __init__(self, new_upgrade_type):
        super().__init__(Option.MENU_PURCHASE_UPGRADE)
        self.new_upgrade_type = new_upgrade_type

    def __str__(self):
        return "Order: purchase upgrade {}".format(self.new_upgrade_type)

    def serialize(self):
        return "[Upgrd]{}".format(self.new_upgrade_type.name)


# An order to modify an adjacent tile
class TerraformOrder(Order):
    def __init__(self, tx, ty, raising=True):
        super().__init__(Option.MENU_RAISE_TILE)
        self.tx = tx
        self.ty = ty
        self.raising = raising

    def __str__(self):
        return "Order: {} terrain on tile ({}, {})".format("raise" if self.raising else "lower", self.tx, self.ty)

    def serialize(self):
        return "[Terra]{},{},{}".format(self.tx, self.ty, self.raising)


# An order for the building to demolish itself.
class DemolishOrder(Order):
    def __init__(self):
        super().__init__(Option.MENU_DEMOLISH_SELF)

    def __str__(self):
        return "Order: Demolish self".format()

    def serialize(self):
        return "[Demol]".format()


# An order for the piece to heal itself slightly.
class HealOrder(Order):
    def __init__(self):
        super().__init__(Option.MENU_HEAL_SELF)

    def __str__(self):
        return "Order: Heal self".format()

    def serialize(self):
        return "[HealS]".format()


# Deserialize an order from a serialized string
def deserialize_order(order):
    prefix = order[:7]
    fields = order[7:].split(',')
    if prefix == "[Move_]":
        return MoveOrder(int(fields[0]), int(fields[1]))
    elif prefix == "[Range]":
        return RangedAttackOrder(int(fields[0]), int(fields[1]))
    elif prefix == "[Build]":
        return BuildOrder(int(fields[0]), int(fields[1]), PieceType[fields[2]])
    elif prefix == "[Upgrd]":
        return UpgradeOrder(UpgradeType[fields[0]])
    elif prefix == "[Terra]":
        return TerraformOrder(int(fields[0]), int(fields[1]), bool(fields[2]))
    elif prefix == "[Demol]":
        return DemolishOrder()
    elif prefix == "[HealS]":
        return HealOrder()
    else:
        return None
