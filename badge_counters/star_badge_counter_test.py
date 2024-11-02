import unittest

from badge_counters.star_badge_counter import StarBadgeCounter


class TestStarBadgeCounter(unittest.IsolatedAsyncioTestCase):

    def test_way_to_s0(self):
        no_penalty_expectations_full_circle = [{ 'progress_reviews': 3, 'progress_pct': 0, 'received_badge': None },
                                               { 'progress_reviews': 2, 'progress_pct': 33, 'received_badge': None },
                                               { 'progress_reviews': 1, 'progress_pct': 66, 'received_badge': 's0' },
                                               { 'progress_reviews': 3, 'progress_pct': 0, 'received_badge': None },
                                               { 'progress_reviews': 2, 'progress_pct': 33, 'received_badge': None },
                                               { 'progress_reviews': 1, 'progress_pct': 66, 'received_badge': 's1' },
                                               { 'progress_reviews': 3, 'progress_pct': 0, 'received_badge': None },
                                               { 'progress_reviews': 2, 'progress_pct': 33, 'received_badge': None },
                                               { 'progress_reviews': 1, 'progress_pct': 66, 'received_badge': 's2' }]

        expectations = [
            { 'progress_reviews': 3, 'progress_pct': 0, 'received_badge': None },
            { 'progress_reviews': 2, 'progress_pct': 33, 'received_badge': None },
            { 'progress_reviews': 1, 'progress_pct': 66, 'received_badge': 's0' },
            { 'progress_reviews': 3, 'progress_pct': 0, 'received_badge': None },
            'penalty'
        ]

        self._test_runner('s0', expectations + no_penalty_expectations_full_circle + no_penalty_expectations_full_circle)

    def _test_runner(self, for_badge, expectations):
        counter = StarBadgeCounter()
        state = None
        for exp in expectations:
            print(f"Expectation: {exp}")
            if exp == 'penalty':
                print('Penalty!')
                badge_advice = counter.on_penalty(0, state, 2)
                state = badge_advice[1]
                continue
            result = counter.progress(for_badge, 0, state, 2)
            print(f"Reality: {result}")
            self.assertEqual(result, [{'badge': for_badge,
                                       'challenge': 'review_regularly_no_penalty',
                                       'remaining_reviews': exp['progress_reviews'],
                                       'progress_pct': exp['progress_pct']}])
            badge_advice = counter.on_review(0, state, 2)
            self.assertEqual(badge_advice[0], exp['received_badge'])
            state = badge_advice[1]
            print(f"State: {state}")


    def test_way_to_s1(self):
        no_penalty_expectations_full_circle = [{ 'progress_reviews': 6, 'progress_pct': 0, 'received_badge': None },
                                               { 'progress_reviews': 5, 'progress_pct': 16, 'received_badge': None },
                                               { 'progress_reviews': 4, 'progress_pct': 33, 'received_badge': 's0' },
                                               { 'progress_reviews': 3, 'progress_pct': 50, 'received_badge': None },
                                               { 'progress_reviews': 2, 'progress_pct': 66, 'received_badge': None },
                                               { 'progress_reviews': 1, 'progress_pct': 83, 'received_badge': 's1' },
                                               { 'progress_reviews': 3, 'progress_pct': 66, 'received_badge': None },
                                               { 'progress_reviews': 2, 'progress_pct': 77, 'received_badge': None },
                                               { 'progress_reviews': 1, 'progress_pct': 88, 'received_badge': 's2' },
                                               ]

        expectations = [
            { 'progress_reviews': 6, 'progress_pct': 0, 'received_badge': None },
            { 'progress_reviews': 5, 'progress_pct': 16, 'received_badge': None },
            { 'progress_reviews': 4, 'progress_pct': 33, 'received_badge': 's0' },
            { 'progress_reviews': 3, 'progress_pct': 50, 'received_badge': None },
            'penalty'
        ]

        self._test_runner('s1', expectations + no_penalty_expectations_full_circle + no_penalty_expectations_full_circle)

    def test_way_to_s2(self):
        no_penalty_expectations_full_circle = [{ 'progress_reviews': 9, 'progress_pct': 0, 'received_badge': None },
                                               { 'progress_reviews': 8, 'progress_pct': 11, 'received_badge': None },
                                               { 'progress_reviews': 7, 'progress_pct': 22, 'received_badge': 's0' },
                                               { 'progress_reviews': 6, 'progress_pct': 33, 'received_badge': None },
                                               { 'progress_reviews': 5, 'progress_pct': 44, 'received_badge': None },
                                               { 'progress_reviews': 4, 'progress_pct': 55, 'received_badge': 's1' },
                                               { 'progress_reviews': 3, 'progress_pct': 66, 'received_badge': None },
                                               { 'progress_reviews': 2, 'progress_pct': 77, 'received_badge': None },
                                               { 'progress_reviews': 1, 'progress_pct': 88, 'received_badge': 's2' }]

        expectations = [
            { 'progress_reviews': 9, 'progress_pct': 0, 'received_badge': None },
            { 'progress_reviews': 8, 'progress_pct': 11, 'received_badge': None },
            { 'progress_reviews': 7, 'progress_pct': 22, 'received_badge': 's0' },
            { 'progress_reviews': 6, 'progress_pct': 33, 'received_badge': None },
            'penalty'
        ]

        self._test_runner('s2', expectations + no_penalty_expectations_full_circle + no_penalty_expectations_full_circle)
