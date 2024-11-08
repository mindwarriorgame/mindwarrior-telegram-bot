
import unittest

from badges_manager import BadgesManager, generate_levels


class BadgesManagerTest(unittest.IsolatedAsyncioTestCase):

    def test_generate_levels(self):
        generate_levels()

    def test_start_game_starts_from_level_1(self):
        badges_manager = BadgesManager(2, None)
        badge = badges_manager.on_game_started(0)
        self.assertEqual(badge, "f0")
        self.assertEqual(badges_manager.get_level(), 0)
        self.assertEqual(badges_manager.get_board(), [{'badge': 'f0', 'is_active': True, 'is_last_modified': True},
                                                                             {'badge': 's0', 'is_active': None},
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
        self.assertEqual(badges_manager.serialize(), '{"badges_state": {"CatBadgeCounter": "57600", "TimeBadgeCounter": "86400", "StarBadgeCounter": "0,5", "FeatherBadgeCounter": "86400"}, "board": [{"badge": "f0", "is_active": true, "is_last_modified": true}, {"badge": "s0", "is_active": null}, {"badge": "c0", "is_active": null}], "level": 0, "c0_hp": 0, "c0_hp_next_delta": 3, "last_badge": "f0"}')


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
        self.assertEqual(badges_manager.serialize(), '{"badges_state": {"CatBadgeCounter": "118600", "TimeBadgeCounter": "86400", "StarBadgeCounter": "0,5", "FeatherBadgeCounter": "86400"}, "board": [{"badge": "f0", "is_active": true}, {"badge": "s0", "is_active": null}, {"badge": "c0", "is_active": true, "is_last_modified": true}], "level": 0, "last_badge": "c0", '
                                                     '"c0_hp_next_delta": 1, "c0_hp": 15}')

    def test_grumpy_spoils_everything(self):
        badges_manager = BadgesManager(2, '{"badges_state": {"CatBadgeCounter": "118600", "TimeBadgeCounter": "86400",'
                                       ' "StarBadgeCounter": "0,5", "FeatherBadgeCounter": "86400"},'
                                       ' "board": [{"badge": "f0", "is_active": true}, {"badge": "s0", "is_active": null}, '
                                       '{"badge": "c0", "is_active": true, "is_last_modified": true}], "level": 0, '
                                       '"last_badge": "c0"}'
                                       )
        badge = badges_manager.on_review(100000)
        self.assertEqual(badge, None)
        self.assertEqual(badges_manager.count_active_grumpy_cats_on_board(), 1)
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 12)
        self.assertEqual(badges_manager.serialize(), '{"badges_state": {"CatBadgeCounter": "157600", "TimeBadgeCounter": "86400", "StarBadgeCounter": "0,5", "FeatherBadgeCounter": "86400"}, "board": [{"badge": "f0", "is_active": true}, {"badge": "s0", "is_active": null}, {"badge": "c0", "is_active": true, "is_last_modified": true}], "level": 0, "last_badge": "c0", "c0_hp_next_delta": 3, "c0_hp": 12}')

    def test_kicking_out_grumpy_cat(self):
        badges_manager = BadgesManager(2, '{"badges_state": {"CatBadgeCounter": "157600", '
                                       '"TimeBadgeCounter": "86400", "StarBadgeCounter": "0,5", '
                                       '"FeatherBadgeCounter": "86400"}, "board": [{"badge": "f0", "is_active": true}, '
                                       '{"badge": "s0", "is_active": null}, {"badge": "c0", "is_active": true, '
                                       '"is_last_modified": true}], "level": 0, "last_badge": "c0", "c0_hp": 15}')
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
        self.assertEqual(badges_manager.get_last_badge(), 'f0')
        self.assertEqual(badges_manager.get_board(), [{'badge': 's0', 'is_active': None},
                                                                             {'badge': 'c0', 'is_active': None}])

    def test_level_up(self):
        badges_manager = BadgesManager(2, '{"badges_state": {"CatBadgeCounter": "57600", "TimeBadgeCounter": "86400", '
                                       '"StarBadgeCounter": "4,5", "FeatherBadgeCounter": "86400"}, "board": '
                                       '[{"badge": "f0", "is_active": true, "is_last_modified": true}, {"badge": "s0", '
                                       '"is_active": null}, {"badge": "c0", "is_active": null}], "level": 0, "last_badge": "f0"}')
        badge = badges_manager.on_review(100000)
        self.assertEqual(badges_manager.is_level_completed(), True)
        self.assertEqual(badges_manager.get_next_level_board(), [{'badge': 's1'}, {'badge': 't0'}, {'badge': 'c0'}, {'badge': 'c0'}])
        badge = badges_manager.on_review(100001)
        self.assertEqual(badge, None) # first review, the level has started
        badge = badges_manager.on_review(1000001)
        self.assertEqual(badge, 't0') # had it been same level, it would've returned None
        self.assertEqual(badges_manager.get_level(), 1)
        self.assertEqual(badges_manager.get_last_badge(), 't0')
        self.assertEqual(badges_manager.get_board(), [{'badge': 's1', 'is_active': None},
                                                      {'badge': 't0', 'is_active': True, 'is_last_modified': True},
                                                      {'badge': 'c0', 'is_active': None},
                                                      {'badge': 'c0', 'is_active': None}])
        self.assertEqual(badges_manager.is_level_completed(), False)

    def test_c0_can_block_two_cells(self):
        badges_manager = BadgesManager(2, '{"board": '
                                       '[{"badge": "f0", "is_active": false, "is_last_modified": true}, {"badge": "c0", '
                                       '"is_active": null}, {"badge": "c0", "is_active": null}], "level": 0, "last_badge": "f0"}')
        badge = badges_manager.on_penalty(0)
        self.assertEqual(badge, 'c0')
        self.assertEqual(badges_manager.progress(1000), {'c0': {'badge': 'c0',
                                                                'challenge': 'review',
                                                                'progress_pct': 0,
                                                                'remaining_reviews': 15},
                                                         'f0': {'badge': 'f0',
                                                                'challenge': 'update_formula',
                                                                'progress_pct': 0,
                                                                'remaining_time_secs': 86400}})
        badge = badges_manager.on_penalty(0)
        self.assertEqual(badge, 'c0')
        self.assertEqual(badges_manager.count_active_grumpy_cats_on_board(), 2)
        self.assertEqual(badges_manager.get_board(), [{'badge': 'f0', 'is_active': False},
                                                      {'badge': 'c0', 'is_active': True},
                                                      {'badge': 'c0', 'is_active': True, 'is_last_modified': True}])
        badge = badges_manager.on_penalty(0)
        self.assertEqual(badge, None)

        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 15)
        badges_manager.on_review(0)
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 14)
        self.assertEqual(badges_manager.progress(1000), {'c0': {'badge': 'c0',
                                                                'challenge': 'review',
                                                                'progress_pct': 7,
                                                                'remaining_reviews': 14},
                                                         'f0': {'badge': 'f0',
                                                                'challenge': 'update_formula',
                                                                'progress_pct': 0,
                                                                'remaining_time_secs': 86400}})
        badges_manager.on_review(0)
        badges_manager.on_review(0)
        badges_manager.on_review(0)
        badges_manager.on_review(0)
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 2)
        self.assertEqual(badges_manager.on_review(0), 'c0_removed')
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 15)
        self.assertEqual(badges_manager.progress(1000), {'c0': {'badge': 'c0',
                                                                'challenge': 'review',
                                                                'progress_pct': 0,
                                                                'remaining_reviews': 15},
                                                         'f0': {'badge': 'f0',
                                                                'challenge': 'update_formula',
                                                                'progress_pct': 0,
                                                                'remaining_time_secs': 86400}})
