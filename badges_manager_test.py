
import unittest

from badges_manager import BadgesManager


class BadgesManagerTest(unittest.IsolatedAsyncioTestCase):

    def test_start_game_starts_from_level_0(self):
        badges_manager = BadgesManager(2, None)
        badge = badges_manager.on_game_started(0)
        self.assertEqual(badge, "f0")
        self.assertEqual(badges_manager.get_level(), 0)
        self.assertEqual(badges_manager.get_board(), [{'badge': 'f0', 'is_active': True, 'is_last_modified': True},
                                                      {'badge': 's0', 'is_active': None},
                                                      {'badge': 's1', 'is_active': None},
                                                      {'badge': 'c0', 'is_active': None}])

        self.assertEqual(badges_manager.progress(1000), {'c0': {'badge': 'c0',
                                                                'challenge': 'review',
                                                                'progress_pct': 100,
                                                                'remaining_reviews': 0},
                                                         's0': {'badge': 's0',
                                                                'challenge': 'review_regularly_no_penalty',
                                                                'progress_pct': 0,
                                                                'remaining_reviews': 5}})

        self.assertEqual(badges_manager.is_level_completed(), False)
        self.assertEqual(badges_manager.serialize(), '{"badges_state": {"CatBadgeCounter": "57600", "TimeBadgeCounter": "86400", "StarBadgeCounter": "0,5", "FeatherBadgeCounter": "86400"}, "board": [{"badge": "f0", "is_active": true, "is_last_modified": true}, {"badge": "s0", "is_active": null}, {"badge": "s1", "is_active": null}, {"badge": "c0", "is_active": null}], "level": 0, "c0_hp": 0, "c0_hp_next_delta": 3, "last_badge": "f0", "c0_active_time_penalty": 0, "c0_lock_started_at": 0}')


    def test_grumpy_cat_gets_in(self):
        badges_manager = BadgesManager(2, '{"badges_state": {"CatBadgeCounter": "57600", "TimeBadgeCounter": "86400", '
                                       '"StarBadgeCounter": "0,5", "FeatherBadgeCounter": "86400"}, "board": '
                                       '[{"badge": "f0", "is_active": true, "is_last_modified": true}, {"badge": "s0", '
                                       '"is_active": null}, {"badge": "c0", "is_active": null}], "level": 0, "last_badge": "f0"}'
                                       )
        badge = badges_manager.on_penalty(61000)
        self.assertEqual(badge, "c0")
        self.assertEqual(badges_manager.get_level(), 0)
        self.assertEqual(badges_manager.get_board(), [{'badge': 'f0', 'is_active': True},
                                                                             {'badge': 's0', 'is_active': None},
                                                                             {'badge': 'c0', 'is_active': True, 'is_last_modified': True}])

        self.assertEqual(badges_manager.is_level_completed(), False)
        self.assertEqual(badges_manager.serialize(), '{"badges_state": {"CatBadgeCounter": "118600", "TimeBadgeCounter": '
                                                     '"86400", "StarBadgeCounter": "0,5", "FeatherBadgeCounter": "86400"}, '
                                                     '"board": [{"badge": "f0", "is_active": true}, {"badge": "s0", "is_active": null}, '
                                                     '{"badge": "c0", "is_active": true, "is_last_modified": true}], "level": 0, '
                                                     '"last_badge": "c0", "c0_hp_next_delta": 1, "c0_hp": 15, '
                                                     '"c0_lock_started_at": 61000, "c0_active_time_penalty": 0}')

    def test_grumpy_spoils_everything(self):
        badges_manager = BadgesManager(2, '{"badges_state": {"CatBadgeCounter": "118600", "TimeBadgeCounter": "86400",'
                                       ' "StarBadgeCounter": "0,5", "FeatherBadgeCounter": "86400"},'
                                       ' "board": [{"badge": "f0", "is_active": true}, {"badge": "s0", "is_active": null}, '
                                       '{"badge": "c0", "is_active": true, "is_last_modified": true}], "level": 0, '
                                       '"last_badge": "c0"}'
                                       )
        badge = badges_manager.on_review(1000000)
        self.assertEqual(badge, None)
        self.assertEqual(badges_manager.count_active_grumpy_cats_on_board(), 1)
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 12)
        self.assertEqual(badges_manager.serialize(), '{"badges_state": {"CatBadgeCounter": "118600", "TimeBadgeCounter": "86400", '
                                                     '"StarBadgeCounter": "0,5", "FeatherBadgeCounter": "86400"}, '
                                                     '"board": [{"badge": "f0", "is_active": true}, {"badge": "s0", "is_active": null}, '
                                                     '{"badge": "c0", "is_active": true}], "level": 0, "last_badge": null, "c0_hp_next_delta": 3, '
                                                     '"c0_hp": 12, "c0_lock_started_at": 0, "c0_active_time_penalty": 0}')

    def test_kicking_out_grumpy_cat(self):
        badges_manager = BadgesManager(2, '{"badges_state": {"CatBadgeCounter": "157600", '
                                       '"TimeBadgeCounter": "86400", "StarBadgeCounter": "0,5", '
                                       '"FeatherBadgeCounter": "86400"}, "board": [{"badge": "f0", "is_active": true}, '
                                       '{"badge": "s0", "is_active": null}, {"badge": "c0", "is_active": true, '
                                       '"is_last_modified": true}], "level": 0, "last_badge": "c0", "c0_hp": 15, '
                                          '"c0_lock_started_at": 1000, "c0_active_time_penalty": 5000}')
        self.assertEqual(badges_manager.on_review(10), None)
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 12)
        self.assertEqual(badges_manager.on_review(11), None)
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 9)
        self.assertEqual(badges_manager.on_review(12), None)
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 6)
        self.assertEqual(badges_manager.on_review(13), None)
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 3)
        self.assertEqual(badges_manager.on_review(14), "c0_removed")
        self.assertEqual(badges_manager.get_board(), [{'badge': 'f0', 'is_active': True},
                                                                             {'badge': 's0', 'is_active': None},
                                                                             {'badge': 'c0',
                                                       'is_active': False,
                                                       'is_last_modified': True}])
        self.assertEqual(badges_manager.progress(1000), {'c0': {'badge': 'c0',
                                                                'challenge': 'review',
                                                                'progress_pct': 100,
                                                                'remaining_reviews': 0},
                                                         's0': {'badge': 's0',
                                                                'challenge': 'review_regularly_no_penalty',
                                                                'progress_pct': 0,
                                                                'remaining_reviews': 5}})

    def test_outside_of_board(self):
        badges_manager = BadgesManager(2, '{"badges_state": {}, "board": [{"badge": "s0", "is_active": null}, {"badge": "c0", "is_active": null}], "level": 0, "last_badge": "f0"}')
        badge = badges_manager.on_game_started(0)
        self.assertEqual(badge, None)
        self.assertEqual(badges_manager.get_level(), 0)
        self.assertEqual(badges_manager.get_last_badge(), None)
        self.assertEqual(badges_manager.get_board(), [{'badge': 's0', 'is_active': None},
                                                                             {'badge': 'c0', 'is_active': None}])

    def test_level_up(self):
        badges_manager = BadgesManager(2, '{"badges_state": {"CatBadgeCounter": "57600", "TimeBadgeCounter": "86400", '
                                       '"StarBadgeCounter": "4,5", "FeatherBadgeCounter": "86400"}, "board": '
                                       '[{"badge": "f0", "is_active": true, "is_last_modified": true}, {"badge": "s0", '
                                       '"is_active": null}, {"badge": "c0", "is_active": null}], "level": 0, "last_badge": "f0"}')
        badge = badges_manager.on_review(100000)
        self.assertEqual(badges_manager.is_level_completed(), True)
        self.assertEqual(badges_manager.get_next_level_board(), [{'badge': 's1'},
                                                                 {'badge': 't0'},
                                                                 {'badge': 'c0'},
                                                                 {'badge': 'c1'},
                                                                 {'badge': 'c0'}])
        badge = badges_manager.on_review(100001)
        self.assertEqual(badge, None) # first review, the level has started
        badge = badges_manager.on_review(1000001)
        self.assertEqual(badge, 'c1') # had it been same level, it would've returned None
        self.assertEqual(badges_manager.get_level(), 1)
        self.assertEqual(badges_manager.get_last_badge(), 'c1')
        self.assertEqual(badges_manager.get_board(), [{'badge': 's1', 'is_active': None},
                                                      {'badge': 't0', 'is_active': None},
                                                      {'badge': 'c0', 'is_active': None},
                                                      {'badge': 'c1', 'is_active': True, 'is_last_modified': True},
                                                      {'badge': 'c0', 'is_active': None}])
        self.assertEqual(badges_manager.is_level_completed(), False)

    def test_c0_can_block_two_cells(self):
        badges_manager = BadgesManager(2, '{"badges_state": {"CatBadgeCounter": "157600", '
                                          '"TimeBadgeCounter": "150"},"board": '
                                       '[{"badge": "t0", "is_active": false, "is_last_modified": true}, {"badge": "c0", '
                                       '"is_active": null}, {"badge": "c0", "is_active": null}], "level": 0, "last_badge": "f0"}')
        badge = badges_manager.on_penalty(50)
        self.assertEqual(badge, 'c0')
        self.assertEqual(badges_manager.progress(50), {'c0': {'badge': 'c0',
                                                              'challenge': 'review',
                                                              'progress_pct': 0,
                                                              'remaining_reviews': 15},
                                                       't0': {'badge': 't0',
                                                              'challenge': 'play_time',
                                                              'progress_pct': 99,
                                                              'remaining_time_secs': 100}})
        badge = badges_manager.on_penalty(60)
        self.assertEqual(badge, 'c0')
        self.assertEqual(badges_manager.count_active_grumpy_cats_on_board(), 2)
        self.assertEqual(badges_manager.get_board(), [{'badge': 't0', 'is_active': False},
                                                      {'badge': 'c0', 'is_active': True},
                                                      {'badge': 'c0', 'is_active': True, 'is_last_modified': True}])
        badge = badges_manager.on_penalty(70)
        self.assertEqual(badge, None)

        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 15)
        badges_manager.on_review(80)
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 14)
        self.assertEqual(badges_manager.progress(80), {'c0': {'badge': 'c0',
                                                              'challenge': 'review',
                                                              'progress_pct': 7,
                                                              'remaining_reviews': 14},
                                                       't0': {'badge': 't0',
                                                              'challenge': 'play_time',
                                                              'progress_pct': 99,
                                                              'remaining_time_secs': 100}})
        badges_manager.on_review(90)
        badges_manager.on_review(100)
        badges_manager.on_review(110)
        badges_manager.on_review(120)
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 2)
        self.assertEqual(badges_manager.on_review(0), 'c0_removed')
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 15)
        self.assertEqual(badges_manager.progress(120), {'c0': {'badge': 'c0',
                                                               'challenge': 'review',
                                                               'progress_pct': 0,
                                                               'remaining_reviews': 15},
                                                        't0': {'badge': 't0',
                                                               'challenge': 'play_time',
                                                               'progress_pct': 99,
                                                               'remaining_time_secs': 100}})
        self.assertEqual(badges_manager.get_board(), [{'badge': 't0', 'is_active': False},
                                                      {'badge': 'c0', 'is_active': False, 'is_last_modified': True},
                                                      {'badge': 'c0', 'is_active': True}])
        badges_manager.on_review(130)
        badges_manager.on_review(140)
        badges_manager.on_review(150)
        badges_manager.on_review(160)
        badges_manager.on_review(200)
        self.assertEqual(badges_manager.get_board(), [{'badge': 't0', 'is_active': False},
                                                      {'badge': 'c0', 'is_active': False},
                                                      {'badge': 'c0', 'is_active': False, 'is_last_modified': True}])
        self.assertEqual(badges_manager.progress(200), {'c0': {'badge': 'c0',
                                                               'challenge': 'review',
                                                               'progress_pct': 100,
                                                               'remaining_reviews': 0},
                                                        't0': {'badge': 't0',
                                                               'challenge': 'play_time',
                                                               'progress_pct': 99,
                                                               'remaining_time_secs': 100}})
        badges_manager.on_review(250)
        self.assertEqual(badges_manager.get_board(), [{'badge': 't0', 'is_active': False},
                                                      {'badge': 'c0', 'is_active': False},
                                                      {'badge': 'c0', 'is_active': False}])
        self.assertEqual(badges_manager.progress(250), {'c0': {'badge': 'c0',
                                                               'challenge': 'review',
                                                               'progress_pct': 100,
                                                               'remaining_reviews': 0},
                                                        't0': {'badge': 't0',
                                                               'challenge': 'play_time',
                                                               'progress_pct': 99,
                                                               'remaining_time_secs': 50}})
        self.assertEqual(badges_manager.on_review(301), 't0')
