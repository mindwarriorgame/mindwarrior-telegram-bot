import unittest

from badge_counters.cat_badge_counter import CatBadgeCounter


class TestGameManager(unittest.IsolatedAsyncioTestCase):

    def test_way_to_c1(self):
        counter = CatBadgeCounter()

        result = counter.progress("c1", 0, None, 2)
        self.assertEqual(result, [{'badge': 'c1',
                                    'challenge': 'review_regularly_no_penalty',
                                    'remaining_time_secs': 57600, 'progress_pct': 0}])

        badge_advice = counter.on_review(10, None, 2)
        self.assertEqual(badge_advice, (None, 'pending_happy,57610'))
        state = badge_advice[1]

        result = counter.progress("c1", 1000, state, 2)
        self.assertEqual(result, [{'badge': 'c1',
                                    'challenge': 'review_regularly_no_penalty',
                                    'remaining_time_secs': 56610, 'progress_pct': 1}],
                                  )

        badge_advice = counter.on_prompt(2000, state, 2)
        self.assertEqual(badge_advice, (None, 'pending_happy,57610'))
        state = badge_advice[1]

        result = counter.progress("c1", 5000, state, 2)
        self.assertEqual(result, [{'badge': 'c1',
                                    'challenge': 'review_regularly_no_penalty',
                                    'remaining_time_secs': 52610, 'progress_pct': 8}])

        badge_advice = counter.on_penalty(60000, state, 2)
        self.assertEqual(badge_advice, ('c0', 'pending_happy,117600'))
        state = badge_advice[1]

        result = counter.progress("c1", 61000, state, 2)
        self.assertEqual(result, [{'badge': 'c1',
                                    'challenge': 'review_regularly_no_penalty',
                                    'remaining_time_secs': 56600, 'progress_pct': 1}])

        result = counter.progress("c1", 200000, state, 2)
        self.assertEqual(result, [{'badge': 'c1',
                                    'challenge': 'review_regularly_no_penalty',
                                    'remaining_time_secs': 0, 'progress_pct': 100}])

        badge_advice = counter.on_review(500000, state, 2)
        self.assertEqual(badge_advice, ('c1', 'pending_superhappy,557600'))
        state = badge_advice[1]


    def test_way_to_c2(self):
        counter = CatBadgeCounter()

        result = counter.progress("c2", 0, None, 3)
        self.assertEqual(result, [{'badge': 'c1',
                                    'challenge': 'review_regularly_no_penalty',
                                    'remaining_time_secs': 72000,
                                    'progress_pct': 0},
                                   {'badge': 'c2',
                                    'challenge': 'review_regularly_no_prompt',
                                    'remaining_time_secs': 72000,
                                    'progress_pct': 0}])

        badge_advice = counter.on_review(10, None, 3)
        self.assertEqual(badge_advice, (None, 'pending_happy,72010'))
        state = badge_advice[1]

        result = counter.progress("c2", 3000, state, 3)
        self.assertEqual(result, [{'badge': 'c1',
                                    'challenge': 'review_regularly_no_penalty',
                                    'remaining_time_secs': 69010,
                                    'progress_pct': 4},
                                   {'badge': 'c2',
                                    'challenge': 'review_regularly_no_prompt',
                                    'remaining_time_secs': 72000,
                                    'progress_pct': 0}])

        badge_advice = counter.on_review(73000, state, 3)
        self.assertEqual(badge_advice, ('c1', 'pending_superhappy,145000'))
        state = badge_advice[1]

        result = counter.progress("c2", 73000, state, 3)
        self.assertEqual(result, [{
                                    'badge': 'c1',
                                    'challenge': 'review_regularly_no_penalty',
                                    'remaining_time_secs': 0,
                                    'progress_pct': 100
                                }, {'badge': 'c2',
                                    'challenge': 'review_regularly_no_prompt',
                                    'remaining_time_secs': 72000,
                                    'progress_pct': 0}])

        badge_advice = counter.on_prompt(75000, state, 3)
        self.assertEqual(badge_advice, (None, 'pending_happy,145000'))
        state = badge_advice[1]

        result = counter.progress("c2", 75000, state, 3)
        self.assertEqual(result, [{'badge': 'c1',
                                    'challenge': 'review_regularly_no_penalty',
                                    'remaining_time_secs': 70000,
                                    'progress_pct': 2},
                                   {'badge': 'c2',
                                    'challenge': 'review_regularly_no_prompt',
                                    'remaining_time_secs': 72000,
                                    'progress_pct': 0}])

        badge_advice = counter.on_review(150000, state, 3)
        self.assertEqual(badge_advice, ('c1', 'pending_superhappy,222000'))
        state = badge_advice[1]


        badge_advice = counter.on_review(222001, state, 3)
        self.assertEqual(badge_advice, ('c2', 'pending_superhappy,294001'))
        state = badge_advice[1]