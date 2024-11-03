import unittest

from badge_counters.feather_badge_counter import FeatherBadgeCounter
from badge_counters.time_badge_counter import TimeBadgeCounter


class TestTimeBadgeCounter(unittest.IsolatedAsyncioTestCase):

    def test_way_to_c1(self):
        counter = TimeBadgeCounter()

        state = None

        result = counter.progress("t0", 0, state, 2)
        self.assertEqual(result, [{'badge': 't0',
                                   'challenge': 'play_time',
                                   'remaining_time_secs': 86400,
                                   'progress_pct': 0}])


        badge_advice = counter.on_game_started(2000, None, 3)
        self.assertEqual(badge_advice, (None, '110000'))
        state = badge_advice[1]

        result = counter.progress("t0", 3000, state, 3)
        self.assertEqual(result, [{'badge': 't0',
                                   'challenge': 'play_time',
                                   'remaining_time_secs': 107000,
                                   'progress_pct': 0}])

        result = counter.progress("t0", 5000, state, 3)
        self.assertEqual(result, [{'badge': 't0',
                                   'challenge': 'play_time',
                                   'remaining_time_secs': 105000,
                                   'progress_pct': 2}])


        badge_advice = counter.on_review(10000, state, 3)
        self.assertEqual(badge_advice, (None, '110000'))
        state = badge_advice[1]

        badge_advice = counter.on_review(200000, state, 3)
        self.assertEqual(badge_advice, ('t0', '308000'))
        state = badge_advice[1]

        result = counter.progress("t0", 200000, state, 3)
        self.assertEqual(result, [{'badge': 't0',
                                   'challenge': 'play_time',
                                   'remaining_time_secs': 108000,
                                   'progress_pct': 0}])