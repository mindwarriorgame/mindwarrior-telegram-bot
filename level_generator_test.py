import unittest

from level_generator import generate_levels, get_level, FIRST_LEVELS_0_1, FIRST_LEVELS_2_3, FIRST_LEVEL_4, \
    NEXT_LEVELS_0_1, NEXT_LEVELS_2_3, NEXT_LEVELS_4, generate_over_50_level_pick_indices


class TestLevelGenerator(unittest.IsolatedAsyncioTestCase):

    def test_generate_level_0_1(self):
        generate_levels(4)

    def test_generate_over_50_level_pick_indices(self):
        generate_over_50_level_pick_indices()

    def test_first_levels_pick_precanned_values(self):
        level = 0
        while level < 6:
            self.assertEqual(get_level(0, level), FIRST_LEVELS_0_1[level])
            self.assertEqual(get_level(1, level), FIRST_LEVELS_0_1[level])
            self.assertEqual(get_level(2, level), FIRST_LEVELS_2_3[level])
            self.assertEqual(get_level(3, level), FIRST_LEVELS_2_3[level])
            self.assertEqual(get_level(4, level), FIRST_LEVEL_4[level])
            level += 1

    def test_next_levels_pick_generated_values(self):
        level = 6
        while level < 50:
            self.assertEqual(get_level(0, level), NEXT_LEVELS_0_1[level - 6])
            self.assertEqual(get_level(1, level), NEXT_LEVELS_0_1[level - 6])
            self.assertEqual(get_level(2, level), NEXT_LEVELS_2_3[level - 6])
            self.assertEqual(get_level(3, level), NEXT_LEVELS_2_3[level - 6])
            self.assertEqual(get_level(4, level), NEXT_LEVELS_4[level - 6])
            level += 1

    def test_levels_over_50_are_picked_randomly(self):
        for _ in range(0, 1000):
            self.assertTrue(get_level(0, 50) in NEXT_LEVELS_0_1)
            self.assertTrue(get_level(0, 55) in NEXT_LEVELS_0_1)
            self.assertTrue(get_level(1, 50) in NEXT_LEVELS_0_1)
            self.assertTrue(get_level(1, 55) in NEXT_LEVELS_0_1)
            self.assertTrue(get_level(2, 50) in NEXT_LEVELS_2_3)
            self.assertTrue(get_level(2, 55) in NEXT_LEVELS_2_3)
            self.assertTrue(get_level(3, 50) in NEXT_LEVELS_2_3)
            self.assertTrue(get_level(3, 55) in NEXT_LEVELS_2_3)
            self.assertTrue(get_level(4, 50) in NEXT_LEVELS_4)
            self.assertTrue(get_level(4, 55) in NEXT_LEVELS_4)

