import unittest

from badge_counters.cat_badge_counter import CatBadgeCounter


class TestGameManager(unittest.IsolatedAsyncioTestCase):

    def test_way_to_c1(self):

        expectations = [
            {
                'progress_at': 0,
                'expected_progress_pct': 0,
                'expected_remaining_time_secs': 57600,
                'expected_challenge': 'review_regularly_no_penalty',
            },
            {
                'review_at': 10,
                'expected_badge': None,
            },

            {
                'progress_at': 1000,
                'expected_progress_pct': 1,
                'expected_remaining_time_secs': 56610,
                'expected_challenge': 'review_regularly_no_penalty',
            },
            {
                'review_at': 2000,
                'expected_badge': None,
            },
            {
                'progress_at': 5000,
                'expected_progress_pct': 8,
                'expected_remaining_time_secs': 52610,
                'expected_challenge': 'review_regularly_no_penalty',
            },
            {
                'penalty_at': 60000,
                'expected_badge': 'c0',
            },
            {
                'progress_at': 61000,
                'expected_progress_pct': 1,
                'expected_remaining_time_secs': 56600,
                'expected_challenge': 'review_regularly_no_penalty',
            },
            {
                'progress_at': 200000,
                'expected_progress_pct': 100,
                'expected_remaining_time_secs': 0,
                'expected_challenge': 'review_regularly_no_penalty',
            },
            {
                'review_at': 500000,
                'expected_badge': 'c1',
            },
            {
                'review_at': 557600,
                'expected_badge': None,
            },
        ]

        self._test_runner('c1', expectations, 2)

    def _test_runner(self, for_badge, expectations, difficulty):
        counter = CatBadgeCounter()
        state = None
        for exp in expectations:
            print(f"Expectation: {exp}")
            if 'penalty_at' in exp:
                print('Penalty!')
                badge_advice = counter.on_penalty(exp['penalty_at'], state, difficulty)
                self.assertEqual(badge_advice[0], exp['expected_badge'])
                state = badge_advice[1]
                continue
            if 'review_at' in exp:
                print('Review!')
                badge_advice = counter.on_review(exp['review_at'], state, difficulty)
                self.assertEqual(badge_advice[0], exp['expected_badge'])
                state = badge_advice[1]
                continue
            if 'prompt_at' in exp:
                print('Prompt!')
                badge_advice = counter.on_prompt(exp['prompt_at'], state, difficulty)
                self.assertEqual(badge_advice[0], exp['expected_badge'])
                state = badge_advice[1]
                continue
            if 'expected_challenges' in exp:
                result = counter.progress(for_badge, exp['progress_at'], state, difficulty)
                print(f"Reality: {result}")
                for i, challenge in enumerate(exp['expected_challenges']):
                    self.assertEqual(result[i]['badge'], challenge['badge'])
                    self.assertEqual(result[i]['challenge'], challenge['challenge'])
                    self.assertEqual(result[i]['remaining_time_secs'], challenge['remaining_time_secs'])
                    self.assertEqual(result[i]['progress_pct'], challenge['progress_pct'])
                continue

            result = counter.progress(for_badge, exp['progress_at'], state, difficulty)
            print(f"Reality: {result}")
            self.assertEqual(result, [{
                'badge': for_badge,
                'challenge': exp['expected_challenge'],
                'remaining_time_secs': exp['expected_remaining_time_secs'],
                'progress_pct': exp['expected_progress_pct']
            }])
            print(f"State: {state}")


    def test_way_to_c2(self):
        expectations = [
            {
                'progress_at': 0,
                'expected_challenges': [ {
                    'badge': 'c1',
                    'progress_pct': 0,
                    'remaining_time_secs': 72000,
                    'challenge': 'review_regularly_no_penalty',
                }, {
                    'badge': 'c2',
                    'progress_pct': 0,
                    'remaining_time_secs': 72000,
                    'challenge': 'review_regularly_no_prompt',
                }],
            },
            {
                'review_at': 10,
                'expected_badge': None,
            },
            {
                'progress_at': 3000,
                'expected_challenges': [ {
                    'badge': 'c1',
                    'progress_pct': 4,
                    'remaining_time_secs': 69010,
                    'challenge': 'review_regularly_no_penalty',
                }, {
                    'badge': 'c2',
                    'progress_pct': 0,
                    'remaining_time_secs': 72000,
                    'challenge': 'review_regularly_no_prompt',
                }],
            },
            {
                'review_at': 73000,
                'expected_badge': 'c1',
            },
            {
                'progress_at': 73000,
                'expected_challenges': [ {
                    'badge': 'c1',
                    'progress_pct': 100,
                    'remaining_time_secs': 0,
                    'challenge': 'review_regularly_no_penalty',
                }, {
                    'badge': 'c2',
                    'progress_pct': 0,
                    'remaining_time_secs': 72000,
                    'challenge': 'review_regularly_no_prompt',
                }],
            },
            {
                'prompt_at': 75000,
                'expected_badge': None,
            },
            {
                'progress_at': 75000,
                'expected_challenges': [ {
                    'badge': 'c1',
                    'progress_pct': 2,
                    'remaining_time_secs': 70000,
                    'challenge': 'review_regularly_no_penalty',
                }, {
                    'badge': 'c2',
                    'progress_pct': 0,
                    'remaining_time_secs': 72000,
                    'challenge': 'review_regularly_no_prompt',
                }],
            },
            {
                'review_at': 150000,
                'expected_badge': 'c1',
            },
            {
                'review_at': 222001,
                'expected_badge': 'c2',
            }
        ]
        self._test_runner('c2', expectations, 3)