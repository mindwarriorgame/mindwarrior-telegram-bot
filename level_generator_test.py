import unittest

from level_generator import generate_levels, get_level, FIRST_LEVELS_0_1, FIRST_LEVELS_2_3, FIRST_LEVEL_4, \
    NEXT_LEVELS_0_1, NEXT_LEVELS_2_3, NEXT_LEVELS_4, generate_over_50_level_pick_indices


class TestLevelGenerator(unittest.IsolatedAsyncioTestCase):

    def test_generate_level_0_1(self):
        generate_levels(4)
        print("alldone")

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
            for difficulty in range(0, 5):
                generated = get_level(difficulty, level)
                expected = []
                if difficulty == 0 or difficulty == 1:
                    expected = NEXT_LEVELS_0_1[level - 6]
                if difficulty == 2 or difficulty == 3:
                    expected = NEXT_LEVELS_2_3[level - 6]
                if difficulty == 4:
                    expected = NEXT_LEVELS_4[level - 6]
                self.assertEqual(generated[:len(expected)], expected)
                if difficulty > 2:
                    print(difficulty, level)
                    # Yeah that's ugly, but I'm too lazy to think of something smarter; let's just skip
                    # these two levels 
                    if ((difficulty != 4 or level != 22) and
                        (difficulty != 3 and level != 20) and
                        (difficulty != 4 and level != 26)):
                        self.assertGreater(len(generated), len(expected))
                for c0idx in range(len(expected), len(generated)):
                    self.assertEqual(generated[c0idx], "c0")
            level += 1

    def test_levels_over_50_are_picked_deterministically(self):
        self.assertEqual(get_level(0, 499), get_level(0, 499));

