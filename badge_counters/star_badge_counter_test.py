import unittest

from badge_counters.star_badge_counter import StarBadgeCounter


class TestStarBadgeCounter(unittest.IsolatedAsyncioTestCase):

    def test_way_to_s0(self):
        expectations = [
            { 'progress_reviews': 3, 'progress_pct': 0, 'received_badge': None },
            { 'progress_reviews': 2, 'progress_pct': 33, 'received_badge': None },
            'penalty',
            { 'progress_reviews': 1, 'progress_pct': 66, 'received_badge': None },
            { 'progress_reviews': 1, 'progress_pct': 66, 'received_badge': 's0' },
            { 'no_progress': True, 'received_badge': None },
        ]
        for cnt in range(0, 100):
            expectations += [{ 'no_progress': True, 'received_badge': None }]

        self._test_runner('s0', expectations,["s0", "f0"])

    def _test_runner(self, for_badge, expectations, board_badges):
        counter = StarBadgeCounter()
        state = None
        for exp in expectations:
            print("---")
            print(board_badges)
            print(f"Expectation: {exp}")
            if exp == 'penalty':
                print('Penalty!')
                badge_advice = counter.on_penalty(0, state, 1, board_badges)
                state = badge_advice[1]
                print("State: ", state)
                continue
            result = counter.progress(for_badge, 0, state, 1, board_badges)
            print(f"Reality: {result}")
            if 'no_progress' in exp:
                self.assertEqual(result, None)
            else:
                self.assertEqual(result, {'badge': for_badge,
                                           'challenge': 'review_regularly_no_penalty',
                                           'remaining_reviews': exp['progress_reviews'],
                                           'progress_pct': exp['progress_pct']})
            badge_advice = counter.on_review(0, state, 1, board_badges)
            self.assertEqual(badge_advice[0], exp['received_badge'])
            if badge_advice[0] is not None:
                board_badges.remove(badge_advice[0])
            state = badge_advice[1]
            print(f"State: {state}")


    def test_way_to_s1(self):
        expectations = [
            { 'progress_reviews': 6, 'progress_pct': 0, 'received_badge': None },
            { 'progress_reviews': 5, 'progress_pct': 16, 'received_badge': None },
            { 'progress_reviews': 4, 'progress_pct': 33, 'received_badge': None },
            { 'progress_reviews': 3, 'progress_pct': 50, 'received_badge': None },
            'penalty',
            { 'progress_reviews': 2, 'progress_pct': 66, 'received_badge': None },
            { 'progress_reviews': 2, 'progress_pct': 66, 'received_badge': None },
            { 'progress_reviews': 1, 'progress_pct': 83, 'received_badge': 's1' },
            { 'no_progress': True, 'received_badge': None },
        ]
        for cnt in range(0, 100):
            expectations += [{ 'no_progress': True, 'received_badge': None }]

        self._test_runner('s1', expectations,["s1", "f0"])

    def test_way_to_s2(self):
        expectations = [
            { 'progress_reviews': 9, 'progress_pct': 0, 'received_badge': None },
            { 'progress_reviews': 8, 'progress_pct': 11, 'received_badge': None },
            { 'progress_reviews': 7, 'progress_pct': 22, 'received_badge': None },
            { 'progress_reviews': 6, 'progress_pct': 33, 'received_badge': None },
            'penalty',
            { 'progress_reviews': 5, 'progress_pct': 44, 'received_badge': None },
            { 'progress_reviews': 5, 'progress_pct': 44, 'received_badge': None },
            { 'progress_reviews': 4, 'progress_pct': 55, 'received_badge': None },
            { 'progress_reviews': 3, 'progress_pct': 66, 'received_badge': None },
            { 'progress_reviews': 2, 'progress_pct': 77, 'received_badge': None },
            { 'progress_reviews': 1, 'progress_pct': 88, 'received_badge': 's2' },
            { 'no_progress': True, 'received_badge': None },
        ]
        for cnt in range(0, 100):
            expectations += [{ 'no_progress': True, 'received_badge': None }]

        self._test_runner('s2', expectations,["s2", "f0"])

    def test_two_stars(self):
        expectations = [
            { 'progress_reviews': 3, 'progress_pct': 0, 'received_badge': None },
            { 'progress_reviews': 2, 'progress_pct': 33, 'received_badge': None },
            { 'progress_reviews': 1, 'progress_pct': 66, 'received_badge': 's0' },

            { 'progress_reviews': 3, 'progress_pct': 0, 'received_badge': None },
            { 'progress_reviews': 2, 'progress_pct': 33, 'received_badge': None },
            { 'progress_reviews': 1, 'progress_pct': 66, 'received_badge': 's0' },

            { 'no_progress': True, 'received_badge': None },
        ]
        for cnt in range(0, 100):
            expectations += [{ 'no_progress': True, 'received_badge': None }]

        self._test_runner('s0', expectations,["s0", "s0", "t0", "f0"])

    def test_all_stars(self):
        counter = StarBadgeCounter()
        _, state = counter.on_game_started(0, None, 1, ["s0", "s1", "s2", "t0", "f0"])

        self.assertEqual(counter.progress("s0", 0, state, 1, ["s0", "s1", "s2", "t0", "f0"]), {
            'badge': 's0',
            'challenge': 'review_regularly_no_penalty',
            'remaining_reviews': 3,
            'progress_pct': 0
        })