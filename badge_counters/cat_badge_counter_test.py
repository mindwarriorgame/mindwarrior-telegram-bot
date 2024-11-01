import unittest

from badge_counters.cat_badge_counter import CatBadgeCounter


class TestGameManager(unittest.IsolatedAsyncioTestCase):

    def test_way_to_c1(self):
        counter = CatBadgeCounter()

        result = counter.progress("c1", 0, None)
        self.assertEqual(result, ([{'badge': 'c1',
                                    'challenge': 'review_regularly_no_penalty',
                                    'remaining_time_secs': 57600}],
                                  0))

        badge_advice = counter.on_review(10, None)
        self.assertEqual(badge_advice, (None, 'pending_superhappy,57610'))
        state = badge_advice[1]

        result = counter.progress("c1", 1000, state)
        self.assertEqual(result, ([{'badge': 'c1',
                                    'challenge': 'review_regularly_no_penalty',
                                    'remaining_time_secs': 56610}],
                                  1))

        badge_advice = counter.on_prompt(2000, state)
        self.assertEqual(badge_advice, (None, 'pending_happy,57610'))
        state = badge_advice[1]

        result = counter.progress("c1", 5000, state)
        self.assertEqual(result, ([{'badge': 'c1',
                                    'challenge': 'review_regularly_no_penalty',
                                    'remaining_time_secs': 52610}],
                                  8))

        result = counter.progress("c1", 500000, state)
        self.assertEqual(result, ([{'badge': 'c1',
                                    'challenge': 'review_regularly_no_penalty',
                                    'remaining_time_secs': 0}],
                                  100))

        badge_advice = counter.on_review(500000, state)
        self.assertEqual(badge_advice, ('c1', 'pending_superhappy,557600'))
        state = badge_advice[1]