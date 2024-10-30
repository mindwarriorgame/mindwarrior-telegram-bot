import json
import unittest

from badges_manager import BadgesManager


class BadgesManagerTest(unittest.IsolatedAsyncioTestCase):

    def test_on_start_game_shows_f0(self):
        mng = BadgesManager("")
        self.assertEqual(mng.on_game_started(0), "f0")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'f0': 1},
                                                       'badges_state': {'CatBadgeCounter': 'pending_superhappy,0',
                                                                        'FeatherBadgeCounter': '0',
                                                                        'StarBadgeCounter': '0',
                                                                        'TimeBadgeCounter': '0'}})

    def test_on_review_shows_star(self):
        mng = BadgesManager('{"badges_counter": {"f0": 1}, "badges_state": {"CatBadgeCounter": "pending_happy,0", "FeatherBadgeCounter": "0", "StarBadgeCounter": "2", "TimeBadgeCounter": "0"}}')
        self.assertEqual(mng.on_review(0), "s0")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'f0': 1, 's0': 1},
                                                       'badges_state': {'CatBadgeCounter': 'pending_happy,0',
                                                                        'FeatherBadgeCounter': '0',
                                                                        'StarBadgeCounter': '3',
                                                                        'TimeBadgeCounter': '0'}})

    def test_on_second_review_shows_med_star(self):
        mng = BadgesManager('{"badges_counter": {"f0": 1, "s0": 1}, "badges_state": {"CatBadgeCounter": "pending_happy,0", "FeatherBadgeCounter": "0", "StarBadgeCounter": "5", "TimeBadgeCounter": "0"}}')
        self.assertEqual(mng.on_review(0), "s1")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'f0': 1, 's1': 1, 's0': 1},
                                                       'badges_state': {'CatBadgeCounter': 'pending_happy,0',
                                                                        'FeatherBadgeCounter': '0',
                                                                        'StarBadgeCounter': '6',
                                                                        'TimeBadgeCounter': '0'}})

    def test_on_third_review_shows_top_star(self):
        mng = BadgesManager('{"badges_counter": {"f0": 1, "s1": 1, "s0": 1}, "badges_state": {"CatBadgeCounter": "pending_happy,0", "FeatherBadgeCounter": "0", "StarBadgeCounter": "17", "TimeBadgeCounter": "0"}}')
        self.assertEqual(mng.on_review(0), "s2")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'f0': 1,
                                                                          's1': 1,
                                                                          's0': 1,
                                                                          's2': 1},
                                                       'badges_state': {'CatBadgeCounter': 'pending_happy,0',
                                                                        'FeatherBadgeCounter': '0',
                                                                        'StarBadgeCounter': '18',
                                                                        'TimeBadgeCounter': '0'}})

    def test_on_forth_review_shows_top_star(self):
        mng = BadgesManager('{"badges_counter": {"f0": 1, "s1": 1, "s0": 1, "s2": 1}, "badges_state": {"CatBadgeCounter": "pending_happy,0", "FeatherBadgeCounter": "0", "StarBadgeCounter": "17", "TimeBadgeCounter": "0"}}')
        self.assertEqual(mng.on_review(0), "s2")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'f0': 1,
                                                                          's1': 1,
                                                                          's0': 1,
                                                                          's2': 2},
                                                       'badges_state': {'CatBadgeCounter': 'pending_happy,0',
                                                                        'FeatherBadgeCounter': '0',
                                                                        'StarBadgeCounter': '18',
                                                                        'TimeBadgeCounter': '0'}})

    def test_on_review_after_penalty_drops_to_first_star(self):
        mng = BadgesManager('{"badges_counter": {"f0": 1, "s1": 1, "s0": 1, "s2": 2}, "badges_state": {"CatBadgeCounter": "pending_happy,0", "FeatherBadgeCounter": "0", "StarBadgeCounter": "5", "TimeBadgeCounter": "0"}}')
        mng.on_penalty(0)
        self.assertEqual(mng.on_review(0), None)
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'c0': 1,
                                                                          'f0': 1,
                                                                          's1': 1,
                                                                          's0': 1,
                                                                          's2': 2},
                                                       'badges_state': {'CatBadgeCounter': 'pending_superhappy,0',
                                                                        'FeatherBadgeCounter': '0',
                                                                        'StarBadgeCounter': '1',
                                                                        'TimeBadgeCounter': '0'}})

    def test_on_formula_update_gives_another_f0_every_24_hours(self):
        mng = BadgesManager("")
        self.assertEqual(mng.on_game_started(0), "f0")
        self.assertEqual(mng.on_formula_updated(12 * 3600), None)
        self.assertEqual(mng.on_formula_updated(26 * 3600), "f0")
        self.assertEqual(mng.on_formula_updated(36 * 3600), None)
        self.assertEqual(mng.on_formula_updated(52 * 3600), "f0")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'f0': 3},
                                                       'badges_state': {'CatBadgeCounter': 'pending_superhappy,0',
                                                                        'FeatherBadgeCounter': '187200',
                                                                        'StarBadgeCounter': '0',
                                                                        'TimeBadgeCounter': '0'}})

    def test_time_badge_each_24_hours(self):
        mng = BadgesManager("")
        mng.on_review(0)
        mng.on_penalty(24*3600) # to suppress happy cat
        self.assertEqual(mng.on_review(27 * 3600), "t0")
        self.assertEqual(mng.on_review(28 * 3600), None)
        self.assertEqual(mng.on_review(29 * 3600), None)
        self.assertEqual(mng.on_review(30 * 3600), "s0")
        mng.on_penalty(53*3600) # to suppress happy cat
        self.assertEqual(mng.on_review(54 * 3600), "time")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'c0': 2, 's0': 1, 't0': 2},
                                                       'badges_state': {'CatBadgeCounter': 'pending_superhappy,194400',
                                                                        'FeatherBadgeCounter': None,
                                                                        'StarBadgeCounter': '0',
                                                                        'TimeBadgeCounter': '194400'}})

    def test_unhappy_cat_on_penalty(self):
        mng = BadgesManager("")
        self.assertEqual(mng.on_penalty(0), "c0")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'c0': 1},
                                                       'badges_state': {'CatBadgeCounter': None,
                                                                        'FeatherBadgeCounter': None,
                                                                        'StarBadgeCounter': '0',
                                                                        'TimeBadgeCounter': None}})

    def test_happy_cat_on_review_without_penalties(self):
        mng = BadgesManager("")
        mng.on_review(0)
        mng.on_prompt(14 * 3600)
        self.assertEqual(mng.on_review(17 * 3600), "c1")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'c1': 1},
                                                       'badges_state': {'CatBadgeCounter': 'pending_superhappy,61200',
                                                                        'FeatherBadgeCounter': None,
                                                                        'StarBadgeCounter': '1',
                                                                        'TimeBadgeCounter': '0'}})

    def test_happy_cat_resets_on_penalty(self):
        mng = BadgesManager("")
        mng.on_review(0)
        mng.on_penalty(6 * 3600)
        self.assertEqual(mng.on_review(17 * 3600), None)
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'c0': 1},
                                                       'badges_state': {'CatBadgeCounter': 'pending_superhappy,61200',
                                                                        'FeatherBadgeCounter': None,
                                                                        'StarBadgeCounter': '1',
                                                                        'TimeBadgeCounter': '0'}})

    def test_superhappy_no_prompt(self):
        mng = BadgesManager("")
        mng.on_review(0)
        self.assertEqual(mng.on_review(17 * 3600), "c2")
        self.assertEqual(json.loads(mng.serialize()), {'badges_counter': {'c2': 1},
                                                       'badges_state': {'CatBadgeCounter': 'pending_superhappy,61200',
                                                                        'FeatherBadgeCounter': None,
                                                                        'StarBadgeCounter': '1',
                                                                        'TimeBadgeCounter': '0'}})