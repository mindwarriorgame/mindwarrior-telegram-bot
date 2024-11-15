import unittest

from badge_counters.cat_badge_counter import CatBadgeCounter


class TestGameManager(unittest.IsolatedAsyncioTestCase):

    def test_way_to_c1(self):

        expectations = [
            {
                'progress_at': 0,
                'expected_progress_pct': 0,
                'expected_remaining_time_secs': 57600,
                'expected_challenge': 'review_regularly_no_penalty'
            },
            {
                'review_at': 0,
                'expected_badge': None,
            },
            {
                'progress_at': 0,
                'expected_progress_pct': 0,
                'expected_remaining_time_secs': 57600,
                'expected_challenge': 'review_regularly_no_penalty'
            },
            {
                'review_at': 1000,
                'expected_badge': None,
            },

            {
                'progress_at': 1000,
                'expected_progress_pct': 2,
                'expected_remaining_time_secs': 56600,
                'expected_challenge': 'review_regularly_no_penalty',
            },
            {
                'review_at': 5000,
                'expected_badge': None,
            },
            {
                'progress_at': 5000,
                'expected_progress_pct': 9,
                'expected_remaining_time_secs': 52600,
                'expected_challenge': 'review_regularly_no_penalty',
            },
            {
                'prompt_at': 5500,
                'expected_badge': None,
            },
            {
                'penalty_at': 60000,
                'expected_badge': 'c0',
            },
            {
                'progress_at': 61000,
                'expected_progress_pct': 9,
                'expected_remaining_time_secs': 52600,
                'expected_challenge': 'review_regularly_no_penalty',
            },
            {
                'progress_at': 200000,
                'expected_progress_pct': 9,
                'expected_remaining_time_secs': 52600,
                'expected_challenge': 'review_regularly_no_penalty',
            },
            {
                'review_at': 500000,
                'expected_badge': None,
            },
            {
                'review_at': 600000,
                'expected_badge': 'c1',
            },
            {
                'review_at': 601000,
                'expected_badge': None,
            },
            {
                'progress_at': 601000,
                'expected_progress_pct': 2,
                'expected_remaining_time_secs': 56600,
                'expected_challenge': 'review_regularly_no_penalty',
            },
        ]

        self._test_runner('c1', expectations, 2, ['c1', 'c2', 'c0', 't0'])

    def _test_runner(self, for_badge, expectations, difficulty, board_locked_items):
        counter = CatBadgeCounter()
        state = None
        for exp in expectations:
            print("----")
            print(f"Expectation: {exp}")
            if 'penalty_at' in exp:
                print('Penalty!')
                badge_advice = counter.on_penalty(exp['penalty_at'], state, difficulty, board_locked_items)
                self.assertEqual(badge_advice[0], exp['expected_badge'])
                state = badge_advice[1]
                print("State: ", state)
                continue
            if 'review_at' in exp:
                print('Review!')
                badge_advice = counter.on_review(exp['review_at'], state, difficulty, board_locked_items)
                self.assertEqual(badge_advice[0], exp['expected_badge'])
                state = badge_advice[1]
                print("State: ", state)
                continue
            if 'prompt_at' in exp:
                print('Prompt!')
                badge_advice = counter.on_prompt(exp['prompt_at'], state, difficulty, board_locked_items)
                self.assertEqual(badge_advice[0], exp['expected_badge'])
                state = badge_advice[1]
                print("State: ", state)
                continue

            result = counter.progress(for_badge, exp['progress_at'], state, difficulty, board_locked_items)
            print(f"Reality: {result}")
            self.assertEqual(result, {
                'badge': for_badge,
                'challenge': exp['expected_challenge'],
                'remaining_time_secs': exp['expected_remaining_time_secs'],
                'progress_pct': exp['expected_progress_pct']
            })
            print(f"State: {state}")


    def test_way_to_c2(self):
        expectations = [
            {
                'progress_at': 0,
                'expected_progress_pct': 0,
                'expected_remaining_time_secs': 72000,
                'expected_challenge': 'review_regularly_no_prompt'
            },
            {
                'review_at': 0,
                'expected_badge': None,
            },
            {
                'progress_at': 0,
                'expected_progress_pct': 0,
                'expected_remaining_time_secs': 72000,
                'expected_challenge': 'review_regularly_no_prompt'
            },
            {
                'review_at': 1000,
                'expected_badge': None,
            },
            {
                'progress_at': 1000,
                'expected_progress_pct': 2,
                'expected_remaining_time_secs': 71000,
                'expected_challenge': 'review_regularly_no_prompt',
            },
            {
                'review_at': 2000,
                'expected_badge': None,
            },
            {
                'progress_at': 2000,
                'expected_progress_pct': 3,
                'expected_remaining_time_secs': 70000,
                'expected_challenge': 'review_regularly_no_prompt',
            },
            {
                'prompt_at': 5500,
                'expected_badge': None,
            },
            {
                'progress_at': 7100,
                'expected_progress_pct': 3,
                'expected_remaining_time_secs': 70000,
                'expected_challenge': 'review_regularly_no_prompt',
            },
            {
                'review_at': 7200,
                'expected_badge': None,
            },
            {
                'progress_at': 7200,
                'expected_progress_pct': 3,
                'expected_remaining_time_secs': 70000,
                'expected_challenge': 'review_regularly_no_prompt',
            },
            {
                'penalty_at': 7400,
                'expected_badge': 'c0',
            },
            {
                'progress_at': 7400,
                'expected_progress_pct': 3,
                'expected_remaining_time_secs': 70000,
                'expected_challenge': 'review_regularly_no_prompt',
            },
            {
                'review_at': 100000,
                'expected_badge': None,
            },
            {
                'progress_at': 7400,
                'expected_progress_pct': 3,
                'expected_remaining_time_secs': 70000,
                'expected_challenge': 'review_regularly_no_prompt',
            },
            {
                'review_at': 180000,
                'expected_badge': 'c2',
            },
            {
                'progress_at': 180000,
                'expected_progress_pct': 0,
                'expected_remaining_time_secs': 72000,
                'expected_challenge': 'review_regularly_no_prompt',
            },
        ]
        self._test_runner('c2', expectations, 3, ['c2', 's0', 'c0', 't0'])