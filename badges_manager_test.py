import json
import unittest

from badges_manager import BadgesManager


class BadgesManagerTest(unittest.IsolatedAsyncioTestCase):

    def test_on_start_game_shows_feather(self):
        mng = BadgesManager("")
        self.assertEqual(mng.on_game_started(), "feather")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'feather': 1},
                                                       'badges_state': {'CatBadgeCounter': 'pending_superhappy,0',
                                                                        'FeatherBadgeCounter': '0',
                                                                        'StarBadgeCounter': '0',
                                                                        'TimeBadgeCounter': '0'}})

    def test_on_review_shows_star(self):
        mng = BadgesManager('{"badges_counter": {"feather": 1}, "badges_state": {"CatBadgeCounter": "pending_happy,0", "FeatherBadgeCounter": "0", "StarBadgeCounter": "0", "TimeBadgeCounter": "0"}}')
        self.assertEqual(mng.on_review(0), "star-small")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'feather': 1, 'star-small': 1},
                                                       'badges_state': {'CatBadgeCounter': 'pending_happy,0',
                                                                        'FeatherBadgeCounter': '0',
                                                                        'StarBadgeCounter': '1',
                                                                        'TimeBadgeCounter': '0'}})

    def test_on_second_review_shows_med_star(self):
        mng = BadgesManager('{"badges_counter": {"feather": 1, "star-small": 1}, "badges_state": {"CatBadgeCounter": "pending_happy,0", "FeatherBadgeCounter": "0", "StarBadgeCounter": "1", "TimeBadgeCounter": "0"}}')
        self.assertEqual(mng.on_review(0), "star-med")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'feather': 1, 'star-med': 1, 'star-small': 1},
                                                       'badges_state': {'CatBadgeCounter': 'pending_happy,0',
                                                                        'FeatherBadgeCounter': '0',
                                                                        'StarBadgeCounter': '2',
                                                                        'TimeBadgeCounter': '0'}})

    def test_on_third_review_shows_top_star(self):
        mng = BadgesManager('{"badges_counter": {"feather": 1, "star-med": 1, "star-small": 1}, "badges_state": {"CatBadgeCounter": "pending_happy,0", "FeatherBadgeCounter": "0", "StarBadgeCounter": "2", "TimeBadgeCounter": "0"}}')
        self.assertEqual(mng.on_review(0), "star-top")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'feather': 1,
                                                                          'star-med': 1,
                                                                          'star-small': 1,
                                                                          'star-top': 1},
                                                       'badges_state': {'CatBadgeCounter': 'pending_happy,0',
                                                                        'FeatherBadgeCounter': '0',
                                                                        'StarBadgeCounter': '3',
                                                                        'TimeBadgeCounter': '0'}})

    def test_on_forth_review_shows_top_star(self):
        mng = BadgesManager('{"badges_counter": {"feather": 1, "star-med": 1, "star-small": 1, "star-top": 1}, "badges_state": {"CatBadgeCounter": "pending_happy,0", "FeatherBadgeCounter": "0", "StarBadgeCounter": "3", "TimeBadgeCounter": "0"}}')
        self.assertEqual(mng.on_review(0), "star-top")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'feather': 1,
                                                                          'star-med': 1,
                                                                          'star-small': 1,
                                                                          'star-top': 2},
                                                       'badges_state': {'CatBadgeCounter': 'pending_happy,0',
                                                                        'FeatherBadgeCounter': '0',
                                                                        'StarBadgeCounter': '4',
                                                                        'TimeBadgeCounter': '0'}})

    def test_on_review_after_penalty_drops_to_first_star(self):
        mng = BadgesManager('{"badges_counter": {"feather": 1, "star-med": 1, "star-small": 1, "star-top": 2}, "badges_state": {"CatBadgeCounter": "pending_happy,0", "FeatherBadgeCounter": "0", "StarBadgeCounter": "4", "TimeBadgeCounter": "0"}}')
        mng.on_penalty(0)
        self.assertEqual(mng.on_review(0), "star-small")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'cat-unhappy': 1,
                                                                          'feather': 1,
                                                                          'star-med': 1,
                                                                          'star-small': 2,
                                                                          'star-top': 2},
                                                       'badges_state': {'CatBadgeCounter': 'pending_superhappy,0',
                                                                        'FeatherBadgeCounter': '0',
                                                                        'StarBadgeCounter': '1',
                                                                        'TimeBadgeCounter': '0'}})

    def test_on_formula_update_gives_another_feather_every_24_hours(self):
        mng = BadgesManager("")
        self.assertEqual(mng.on_game_started(), "feather")
        self.assertEqual(mng.on_formula_updated(12 * 3600), None)
        self.assertEqual(mng.on_formula_updated(26 * 3600), "feather")
        self.assertEqual(mng.on_formula_updated(36 * 3600), None)
        self.assertEqual(mng.on_formula_updated(52 * 3600), "feather")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'feather': 3},
                                                       'badges_state': {'CatBadgeCounter': 'pending_superhappy,0',
                                                                        'FeatherBadgeCounter': '187200',
                                                                        'StarBadgeCounter': '0',
                                                                        'TimeBadgeCounter': '0'}})

    def test_time_badge_each_24_hours(self):
        mng = BadgesManager("")
        mng.on_review(0)
        mng.on_penalty(24*3600) # to suppress happy cat
        self.assertEqual(mng.on_review(27 * 3600), "time")
        self.assertEqual(mng.on_review(28 * 3600), "star-med")
        mng.on_penalty(53*3600) # to suppress happy cat
        self.assertEqual(mng.on_review(54 * 3600), "time")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'cat-unhappy': 2,
                                                                          'star-med': 1,
                                                                          'star-small': 1,
                                                                          'time': 2},
                                                       'badges_state': {'CatBadgeCounter': 'pending_superhappy,194400',
                                                                        'FeatherBadgeCounter': None,
                                                                        'StarBadgeCounter': '1',
                                                                        'TimeBadgeCounter': '194400'}})

    def test_unhappy_cat_on_penalty(self):
        mng = BadgesManager("")
        self.assertEqual(mng.on_penalty(0), "cat-unhappy")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'cat-unhappy': 1},
                                                       'badges_state': {'CatBadgeCounter': None,
                                                                        'FeatherBadgeCounter': None,
                                                                        'StarBadgeCounter': '0',
                                                                        'TimeBadgeCounter': None}})

    def test_happy_cat_on_review_without_penalties(self):
        mng = BadgesManager("")
        mng.on_review(0)
        mng.on_prompt(14 * 3600)
        self.assertEqual(mng.on_review(17 * 3600), "cat-happy")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'cat-happy': 1, 'star-small': 1},
                                                       'badges_state': {'CatBadgeCounter': 'pending_superhappy,61200',
                                                                        'FeatherBadgeCounter': None,
                                                                        'StarBadgeCounter': '2',
                                                                        'TimeBadgeCounter': '0'}})

    def test_happy_cat_resets_on_penalty(self):
        mng = BadgesManager("")
        mng.on_review(0)
        mng.on_penalty(6 * 3600)
        self.assertEqual(mng.on_review(17 * 3600), "star-small")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'cat-unhappy': 1, 'star-small': 2},
                                                       'badges_state': {'CatBadgeCounter': 'pending_superhappy,61200',
                                                                        'FeatherBadgeCounter': None,
                                                                        'StarBadgeCounter': '1',
                                                                        'TimeBadgeCounter': '0'}})

    def test_superhappy_no_prompt(self):
        mng = BadgesManager("")
        mng.on_review(0)
        self.assertEqual(mng.on_review(17 * 3600), "cat-superhappy")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'cat-superhappy': 1, 'star-small': 1},
                                                       'badges_state': {'CatBadgeCounter': 'pending_superhappy,61200',
                                                                        'FeatherBadgeCounter': None,
                                                                        'StarBadgeCounter': '2',
                                                                        'TimeBadgeCounter': '0'}})