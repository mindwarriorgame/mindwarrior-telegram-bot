import unittest

from badge_counters.feather_badge_counter import FeatherBadgeCounter


class TestFeatherBageCounter(unittest.IsolatedAsyncioTestCase):

    def test_way_to_c1(self):
        counter = FeatherBadgeCounter()

        result = counter.progress("f0", 0, None, 3, ["f0", "s0"])
        self.assertEqual(result, {'badge': 'f0',
                                    'challenge': 'update_formula',
                                    'remaining_time_secs': 108000,
                                    'progress_pct': 0})


        badge_advice = counter.on_game_started(0, None, 3, ["f0", "s0"])
        self.assertEqual(badge_advice, ('f0', '108000'))
        state = badge_advice[1]

        result = counter.progress("f0", 0, state, 3, ["f0", "s0"])
        self.assertEqual(result, {'badge': 'f0',
                                    'challenge': 'update_formula',
                                    'remaining_time_secs': 108000,
                                    'progress_pct': 0})

        result = counter.progress("f0", 3000, state, 3, ["f0", "s0"])
        self.assertEqual(result, {'badge': 'f0',
                                    'challenge': 'update_formula',
                                    'remaining_time_secs': 105000,
                                    'progress_pct': 2})

        badge_advice = counter.on_formula_updated(50000, state, 3, ["f0", "s0"])
        self.assertEqual(badge_advice, (None, '108000'))
        state = badge_advice[1]

        result = counter.progress("f0", 108000, state, 3, ["f0", "s0"])
        self.assertEqual(result, {'badge': 'f0',
                                    'challenge': 'update_formula',
                                    'remaining_time_secs': 0,
                                    'progress_pct': 100})

        badge_advice = counter.on_formula_updated(108001, state, 3, ["f0", "s0"])
        self.assertEqual(badge_advice, ('f0', '216001'))
        state = badge_advice[1]

        result = counter.progress("f0", 108001, state, 3, ["f0", "s0"])
        self.assertEqual(result, {'badge': 'f0',
                                    'challenge': 'update_formula',
                                    'remaining_time_secs': 108000,
                                    'progress_pct': 0})

    def test_not_firing_when_not_on_board(self):
        counter = FeatherBadgeCounter()
        result = counter.progress("f0", 0, None, 3, ["c0", "s0"])
        self.assertEqual(result, None)

        badge_advice = counter.on_game_started(0, None, 3, ["c0", "s0"])
        self.assertEqual(badge_advice, (None, '108000'))
        state = badge_advice[1]

        badge_advice = counter.on_formula_updated(109000, state, 3, ["c0", "s0"])
        self.assertEqual(badge_advice, (None, '108000'))
        state = badge_advice[1]

        result = counter.progress("f0", 109001, state, 3, ["c0", "s0"])
        self.assertEqual(result, None)