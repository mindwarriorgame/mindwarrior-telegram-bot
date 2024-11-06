import unittest

from board_serializer import serialize_board, serialize_progress


class BoardSerializedTest(unittest.IsolatedAsyncioTestCase):

    def test_serialize_simple_board(self):
        board = [{'badge': 'f0', 'is_active': None, 'is_target': True},
                 {'badge': 's0', 'is_active': None},
                 {'badge': 'c0', 'is_active': None}]
        self.assertEqual(serialize_board(board), 'f0t_s0_c0')

    def test_serialize_progress(self):
        serialized = serialize_progress({'c1': [{'badge': 'c1',
                                                 'challenge': 'review_regularly_no_penalty',
                                                 'progress_pct': 1,
                                                 'remaining_time_secs': 56600}],
                                         'c2': [{'badge': 'c1',
                                                 'challenge': 'review_regularly_no_penalty',
                                                 'progress_pct': 1,
                                                 'remaining_time_secs': 56600},
                                                {'badge': 'c2',
                                                 'challenge': 'review_regularly_no_prompt',
                                                 'progress_pct': 0,
                                                 'remaining_time_secs': 57600}],
                                         'f0': [{'badge': 'f0',
                                                 'challenge': 'update_formula',
                                                 'progress_pct': 1,
                                                 'remaining_time_secs': 85400}],
                                         's0': [{'badge': 's0',
                                                 'challenge': 'review_regularly_no_penalty',
                                                 'progress_pct': 0,
                                                 'remaining_reviews': 3}],
                                         's1': [{'badge': 's1',
                                                 'challenge': 'review_regularly_no_penalty',
                                                 'progress_pct': 0,
                                                 'remaining_reviews': 6}],
                                         's2': [{'badge': 's2',
                                                 'challenge': 'review_regularly_no_penalty',
                                                 'progress_pct': 0,
                                                 'remaining_reviews': 9}],
                                         't0': [{'badge': 't0',
                                                 'challenge': 'play_time',
                                                 'progress_pct': 1,
                                                 'remaining_time_secs': 85400}]})

        self.assertEqual(serialized, 'c1_1_56600_1--c2_2_56600_1_57600_0--f0_1_85400_1--s0_1_3_0--s1_1_6_0--s2_1_9_0--t0_1_85400_1')

    def test_serialize_grumpy_cat(self):
        serialized = serialize_board([{'badge': 'f0', 'is_active': True},
                                             {'badge': 's0', 'is_active': None},
                                             {'badge': 'c0', 'is_active': None, 'is_target': True}])

        self.assertEqual(serialized, 'f0a_s0_c0t')

    def test_serialize_kicking_out_grumpy_cat(self):
        serialized = serialize_board([{'badge': 'f0', 'is_active': True},
                                      {'badge': 's0', 'is_active': None},
                                      {'badge': 'c0',
                                       'is_active': True,
                                       'is_target': True,
                                       'projectile_override': 'c1'}])
        self.assertEqual(serialized, 'f0a_s0_c0at')