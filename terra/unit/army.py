from terra.engine.gameobject import GameObject
from terra.unit.colonist import Colonist
from terra.unit.trooper import Trooper
from terra.unit.ranger import Ranger
from terra.unit.ghost import Ghost
from terra.unit.unit import Team
from terra.event import *
from terra.unit.unitconflict import UnitConflict
from terra.unit.orders import MoveOrder


# Contains and manages all units from all teams
class Army(GameObject):
    def __init__(self, battle, game_map, roster=None):
        super().__init__()

        self.battle = battle
        self.game_map = game_map

        # Hold the units located on this map
        # Key pairs look like: (gx, gy): [unit1, unit2...]
        self.units = {}

        # Generate units from the provided Roster, if any
        if roster:
            for unit in roster:
                data = unit.split(' ')

                gx = int(data[0])
                gy = int(data[1])
                team = Team[data[2]]
                unit_type = data[3]

                if unit_type == "Colonist":
                    self.register_unit(Colonist(self, self.battle, self.game_map, team, gx, gy))
                elif unit_type == "Trooper":
                    self.register_unit(Trooper(self, self.battle, self.game_map, team, gx, gy))
                elif unit_type == "Ranger":
                    self.register_unit(Ranger(self, self.battle, self.game_map, team, gx, gy))
                elif unit_type == "Ghost":
                    self.register_unit(Ghost(self, self.battle, self.game_map, team, gx, gy))

    # Return a list of unit(s) at the specified grid location
    def get_units_at(self, gx, gy):
        units = self.units.get((gx, gy))
        if not units:
            return []
        else:
            return units

    # Return the unit for the specified team (None if no unit for that team is present)
    def get_unit_at(self, gx, gy, team):
        for unit in self.get_units_at(gx, gy):
            if unit.team == team:
                return unit
        return None

    # Return any enemy units at the location (not belonging to the provided team)
    def get_enemy_units_at(self, gx, gy, my_team):
        units = []
        for unit in self.get_units_at(gx, gy):
            if not unit.team == my_team:
                units.append(unit)
        return units

    # Return all units belonging to the specified team
    def get_all_units_for_team(self, team):
        team_units = []
        for coordinate, units in self.units.items():
            for unit in units:
                if unit.team == team:
                    team_units.append(unit)
        return team_units

    # Register a unit with the game map.
    def register_unit(self, unit):
        if not self.units.get((unit.gx, unit.gy)):
            self.units[(unit.gx, unit.gy)] = []
        self.units[(unit.gx, unit.gy)].append(unit)

    # Unregister a unit with the game map.
    def remove_unit(self, gx, gy, team):
        unit = self.get_unit_at(gx, gy, team)
        if unit:
            self.units[(gx, gy)].remove(unit)
            if len(self.units[(gx, gy)]) == 0:
                del self.units[(gx, gy)]

    # Move a unit on the game map
    def move_unit(self, gx, gy, team):
        unit = self.get_unit_at(gx, gy, team)
        if unit:
            self.register_unit(unit)
            self.remove_unit(gx, gy, team)

    # Get a list of all units, regardless of position or team
    def __get_all_units__(self):
        units = []
        for coordinate in self.units:
            for unit in self.units[coordinate]:
                units.append(unit)
        return units

    # Return true if all movement orders for the provided team are valid (no friendly units end up in the same tile)
    def validate_movement_orders(self, team):
        coordinates = []
        for unit in self.get_all_units_for_team(team):
            if unit.current_order:
                if isinstance(unit.current_order, MoveOrder):
                    coordinates.append((unit.current_order.dx, unit.current_order.dy))
            else:
                coordinates.append((unit.gx, unit.gy))

        # Return true if all the coordinates are unique-- no duplicates are removed
        return len(coordinates) == len(set(coordinates))

    # Check for overlapping enemy units, and resolve their combat
    def resolve_combat(self):
        # Find conflicting units (opposing team units occupying the same space
        conflicting_units = []
        for coordinate in self.units:
            if len(self.units.get(coordinate)) > 1:
                conflicting_units.append(self.units.get(coordinate))

        # Conflict resolution
        if len(conflicting_units) > 0:
            for unit_pair in conflicting_units:
                conflict = UnitConflict(unit_pair[0], unit_pair[1])
                conflict.resolve()

    def ranged_attack(self, gx, gy, origin_team, tx, ty):
        # Find the origin unit and the target unit
        origin_unit = self.get_unit_at(gx, gy, origin_team)
        target_units = self.get_enemy_units_at(tx, ty, origin_team)

        for unit in target_units:
            unit.hp -= origin_unit.ranged_attack

    def step(self, event):
        super().step(event)

        for unit in self.__get_all_units__():
            unit.step(event)

        if is_event_type(event, E_UNIT_MOVED):
            self.move_unit(event.gx, event.gy, event.team)
        elif is_event_type(event, E_UNIT_RANGED_ATTACK):
            self.ranged_attack(event.gx, event.gy, event.team, event.tx, event.ty)
        elif is_event_type(event, E_UNIT_DEAD):
            self.remove_unit(event.gx, event.gy, event.team)

        if is_event_type(event, START_PHASE_EXECUTE_COMBAT):
            self.resolve_combat()

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        for unit in self.__get_all_units__():
            unit.render(game_screen, ui_screen)
