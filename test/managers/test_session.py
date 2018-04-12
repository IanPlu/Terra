import unittest

import pygame
from memory_profiler import profile

from terra.managers.session import Session
from terra.resources.assets import load_assets


class SessionTest(unittest.TestCase):
    # Verify that memory is properly cleaned up on changing sessions
    @profile
    def test_memory_usage(self):
        pygame.init()
        load_assets()

        Session.set_up_local_game("bristle_plains.map")
        Session.set_up_level_editor("cross_strait.map")
        Session.set_up_local_game("cycle_island.map")
        Session.set_up_level_editor("goldrush.map")
        Session.set_up_local_game("deep_wood.map")

        for _ in range(30):
            Session.set_up_local_game("bristle_plains.map")

        pass
