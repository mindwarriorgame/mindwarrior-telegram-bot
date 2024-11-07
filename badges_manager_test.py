
import unittest

from badges_manager import BadgesManager, generate_levels


class BadgesManagerTest(unittest.IsolatedAsyncioTestCase):

    def test_generate_levels(self):
        generate_levels()

    def test_start_game_starts_from_level_1(self):
        badges_manager = BadgesManager()
        badge = badges_manager.on_game_started(0, 2)
        self.assertEqual(badge, "f0")
        self.assertEqual(badges_manager.get_level(), 0)
        self.assertEqual(badges_manager.get_board(), [{'badge': 'f0', 'is_active': True, 'is_last_modified': True},
                                                                             {'badge': 's0', 'is_active': None},
                                                                             {'badge': 'c0', 'is_active': None}])

        self.assertEqual(badges_manager.progress(1000, 2), {'s0': {'badge': 's0',
                                                                   'challenge': 'review_regularly_no_penalty',
                                                                   'progress_pct': 0,
                                                                   'remaining_reviews': 5}})

        self.assertEqual(badges_manager.is_level_completed(), False)
        self.assertEqual(badges_manager.serialize(), '{"badges_state": {"CatBadgeCounter": "57600", "TimeBadgeCounter": "86400", '
                                                     '"StarBadgeCounter": "0,5", "FeatherBadgeCounter": "86400"}, "board": '
                                                     '[{"badge": "f0", "is_active": true, "is_last_modified": true}, {"badge": "s0", '
                                                     '"is_active": null}, {"badge": "c0", "is_active": null}], "level": 0, "last_badge": "f0"}')


    def test_grumpy_cat_gets_in(self):
        badges_manager = BadgesManager('{"badges_state": {"CatBadgeCounter": "57600", "TimeBadgeCounter": "86400", '
                                       '"StarBadgeCounter": "0,5", "FeatherBadgeCounter": "86400"}, "board": '
                                       '[{"badge": "f0", "is_active": true, "is_last_modified": true}, {"badge": "s0", '
                                       '"is_active": null}, {"badge": "c0", "is_active": null}], "level": 0, "last_badge": "f0"}'
                                       )
        badge = badges_manager.on_penalty(61000, 2)
        self.assertEqual(badge, "c0")
        self.assertEqual(badges_manager.get_level(), 0)
        self.assertEqual(badges_manager.get_board(), [{'badge': 'f0', 'is_active': True},
                                                                             {'badge': 's0', 'is_active': None},
                                                                             {'badge': 'c0', 'is_active': True, 'is_last_modified': True}])

        self.assertEqual(badges_manager.is_level_completed(), False)
        self.assertEqual(badges_manager.serialize(), '{"badges_state": {"CatBadgeCounter": "118600", "TimeBadgeCounter": "86400",'
                                                     ' "StarBadgeCounter": "0,5", "FeatherBadgeCounter": "86400"},'
                                                     ' "board": [{"badge": "f0", "is_active": true}, {"badge": "s0", "is_active": null}, '
                                                     '{"badge": "c0", "is_active": true, "is_last_modified": true}], "level": 0, '
                                                     '"last_badge": "c0"}')

    def test_grumpy_spoils_everything(self):
        badges_manager = BadgesManager('{"badges_state": {"CatBadgeCounter": "118600", "TimeBadgeCounter": "86400",'
                                       ' "StarBadgeCounter": "0,5", "FeatherBadgeCounter": "86400"},'
                                       ' "board": [{"badge": "f0", "is_active": true}, {"badge": "s0", "is_active": null}, '
                                       '{"badge": "c0", "is_active": true, "is_last_modified": true}], "level": 0, '
                                       '"last_badge": "c0"}'
                                       )
        badge = badges_manager.on_review(100000, 2)
        self.assertEqual(badge, None)
        self.assertEqual(badges_manager.serialize(), '{"badges_state": {"CatBadgeCounter": "157600", '
                                                     '"TimeBadgeCounter": "86400", "StarBadgeCounter": "0,5", '
                                                     '"FeatherBadgeCounter": "86400"}, "board": [{"badge": "f0", "is_active": true}, '
                                                     '{"badge": "s0", "is_active": null}, {"badge": "c0", "is_active": true, '
                                                     '"is_last_modified": true}], "level": 0, "last_badge": "c0"}')

    def test_kicking_out_grumpy_cat(self):
        badges_manager = BadgesManager('{"badges_state": {"CatBadgeCounter": "157600", '
                                       '"TimeBadgeCounter": "86400", "StarBadgeCounter": "0,5", '
                                       '"FeatherBadgeCounter": "86400"}, "board": [{"badge": "f0", "is_active": true}, '
                                       '{"badge": "s0", "is_active": null}, {"badge": "c0", "is_active": true, '
                                       '"is_last_modified": true}], "level": 0, "last_badge": "c0"}')
        badges_manager.kick_off_grump_cat()
        self.assertEqual(badges_manager.get_board(), [{'badge': 'f0', 'is_active': True},
                                                                             {'badge': 's0', 'is_active': None},
                                                                             {'badge': 'c0',
                                                       'is_active': False,
                                                       'is_last_modified': True}])

    def test_outside_of_board(self):
        badges_manager = BadgesManager('{"badges_state": {}, "board": [{"badge": "s0", "is_active": null}, {"badge": "c0", "is_active": null}], "level": 0, "last_badge": "f0"}')
        badge = badges_manager.on_game_started(0, 2)
        self.assertEqual(badge, None)
        self.assertEqual(badges_manager.get_level(), 0)
        self.assertEqual(badges_manager.get_last_badge(), 'f0')
        self.assertEqual(badges_manager.get_board(), [{'badge': 's0', 'is_active': None},
                                                                             {'badge': 'c0', 'is_active': None}])

    def test_level_up(self):
        badges_manager = BadgesManager('{"badges_state": {"CatBadgeCounter": "57600", "TimeBadgeCounter": "86400", '
                                       '"StarBadgeCounter": "4,5", "FeatherBadgeCounter": "86400"}, "board": '
                                       '[{"badge": "f0", "is_active": true, "is_last_modified": true}, {"badge": "s0", '
                                       '"is_active": null}, {"badge": "c0", "is_active": null}], "level": 0, "last_badge": "f0"}')
        badge = badges_manager.on_review(100000, 2)
        self.assertEqual(badges_manager.is_level_completed(), True)
        self.assertEqual(badges_manager.get_next_level_board(), [{'badge': 's1'}, {'badge': 't0'}, {'badge': 'c0'}, {'badge': 'c0'}])
        badge = badges_manager.on_review(100001, 2)
        self.assertEqual(badge, None) # first review, the level has started
        badge = badges_manager.on_review(1000001, 2)
        self.assertEqual(badge, 't0') # had it been same level, it would've returned None
        self.assertEqual(badges_manager.get_level(), 1)
        self.assertEqual(badges_manager.get_last_badge(), 't0')
        self.assertEqual(badges_manager.get_board(), [{'badge': 's1', 'is_active': None},
                                                      {'badge': 't0', 'is_active': True, 'is_last_modified': True},
                                                      {'badge': 'c0', 'is_active': None},
                                                      {'badge': 'c0', 'is_active': None}])
        self.assertEqual(badges_manager.is_level_completed(), False)