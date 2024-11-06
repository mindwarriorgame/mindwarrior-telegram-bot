import json
import unittest

from badges_manager import BadgesManager, generate_levels


class BadgesManagerTest(unittest.IsolatedAsyncioTestCase):

    def test_generate_levels(self):
        generate_levels()

    def test_start_game_starts_from_level_1(self):
        badges_manager = BadgesManager()
        badge = badges_manager.on_game_started(0, 2)
        self.assertEqual(badge, "f0")
        self.assertEqual(badges_manager.get_level(), 1)
        self.assertEqual(badges_manager.get_board(), [{'badge': 'f0', 'is_active': None, 'is_target': True},
                                                      {'badge': 's0', 'is_active': None},
                                                      {'badge': 'c0', 'is_active': None}])

        self.assertEqual(badges_manager.progress(1000, 2), {'c1': [{'badge': 'c1',
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
        self.assertEqual(badges_manager.is_level_completed(), False)
        self.assertEqual(badges_manager.serialize(), '{"badges_state": {"CatBadgeCounter": "pending_happy,57600", "TimeBadgeCounter": "86400", "StarBadgeCounter": "0", "FeatherBadgeCounter": "86400"}, "board": [{"badge": "f0", "is_active": null, "is_target": true}, {"badge": "s0", "is_active": null}, {"badge": "c0", "is_active": null}], "level": 1, "last_badge": "f0"}')


    def test_grumpy_cat_gets_in(self):
        badges_manager = BadgesManager('{"badges_state": {"CatBadgeCounter": "pending_happy,57600", "TimeBadgeCounter": "86400", "StarBadgeCounter": "0", "FeatherBadgeCounter": "86400"}, "board": [{"badge": "f0", "is_active": null, "is_target": true}, {"badge": "s0", "is_active": null}, {"badge": "c0", "is_active": null}], "level": 1, "last_badge": "f0"}')
        badge = badges_manager.on_penalty(61000, 2)
        self.assertEqual(badge, "c0")
        self.assertEqual(badges_manager.get_level(), 1)
        self.assertEqual(badges_manager.get_board(), [{'badge': 'f0', 'is_active': True},
                                                      {'badge': 's0', 'is_active': None},
                                                      {'badge': 'c0', 'is_active': None, 'is_target': True}])

        self.assertEqual(badges_manager.is_level_completed(), False)
        self.assertEqual(badges_manager.serialize(), '{"badges_state": {"CatBadgeCounter": "pending_happy,118600", "TimeBadgeCounter": "86400", "StarBadgeCounter": "0", "FeatherBadgeCounter": "86400"}, "board": [{"badge": "f0", "is_active": true}, {"badge": "s0", "is_active": null}, {"badge": "c0", "is_active": null, "is_target": true}], "level": 1, "last_badge": "c0"}')

    def test_kicking_out_grumpy_cat(self):
        badges_manager = BadgesManager('{"badges_state": {"CatBadgeCounter": "pending_happy,118600", "TimeBadgeCounter": "86400", "StarBadgeCounter": "0", "FeatherBadgeCounter": "86400"}, "board": [{"badge": "f0", "is_active": true}, {"badge": "s0", "is_active": null}, {"badge": "c0", "is_active": null, "is_target": true}], "level": 1, "last_badge": "c0"}')
        badge = badges_manager.on_review(200000, 2)
        self.assertEqual(badge, "c1")
        self.assertEqual(badges_manager.get_board(), [{'badge': 'f0', 'is_active': True},
                                                      {'badge': 's0', 'is_active': None},
                                                      {'badge': 'c0',
                                                       'is_active': True,
                                                       'is_target': True,
                                                       'projectile_override': 'c1'}])