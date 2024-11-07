import unittest

from board_serializer import serialize_board, serialize_progress


class BoardSerializedTest(unittest.IsolatedAsyncioTestCase):

    def test_serialize_simple_board(self):
        board = [{'badge': 'f0', 'is_active': True, 'is_last_modified': True},
                 {'badge': 's0', 'is_active': None},
                 {'badge': 'c0', 'is_active': None}]
        self.assertEqual(serialize_board(board), 'f0am_s0_c0')

    def test_serialize_progress(self):
        serialized = serialize_progress({'c1': {'badge': 'c1',
                                                 'challenge': 'review_regularly_no_penalty',
                                                 'progress_pct': 1,
                                                 'remaining_time_secs': 56600},
                                         'c2': {'badge': 'c1',
                                                 'challenge': 'review_regularly_no_penalty',
                                                 'progress_pct': 1,
                                                 'remaining_time_secs': 56600},
                                         'f0': {'badge': 'f0',
                                                 'challenge': 'update_formula',
                                                 'progress_pct': 1,
                                                 'remaining_time_secs': 85400},
                                         's0': {'badge': 's0',
                                                 'challenge': 'review_regularly_no_penalty',
                                                 'progress_pct': 0,
                                                 'remaining_reviews': 3},
                                         's1': {'badge': 's1',
                                                 'challenge': 'review_regularly_no_penalty',
                                                 'progress_pct': 0,
                                                 'remaining_reviews': 6},
                                         's2': {'badge': 's2',
                                                 'challenge': 'review_regularly_no_penalty',
                                                 'progress_pct': 0,
                                                 'remaining_reviews': 9},
                                         't0': {'badge': 't0',
                                                 'challenge': 'play_time',
                                                 'progress_pct': 1,
                                                 'remaining_time_secs': 85400}})

        self.assertEqual(serialized, 'c1_56600_1--c2_56600_1--f0_85400_1--s0_3_0--s1_6_0--s2_9_0--t0_85400_1')

    def test_serialize_grumpy_cat(self):
        serialized = serialize_board([{'badge': 'f0', 'is_active': True},
                                             {'badge': 's0', 'is_active': None},
                                             {'badge': 'c0', 'is_active': True, 'is_last_modified': True}])

        self.assertEqual(serialized, 'f0a_s0_c0am')

    def test_serialize_kicking_out_grumpy_cat(self):
        serialized = serialize_board([{'badge': 'f0', 'is_active': True},
                                      {'badge': 's0', 'is_active': None},
                                      {'badge': 'c0',
                                       'is_active': False,
                                       'is_last_modified': True}])
        self.assertEqual(serialized, 'f0a_s0_c0m')