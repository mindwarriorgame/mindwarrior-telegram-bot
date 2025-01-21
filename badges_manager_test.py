
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
        self.assertEqual(badges_manager.serialize(), '{"badges_state": {"CatBadgeCounter": "cumulative_counter_secs=0,counter_last_updated=0,update_reason=game_started", "TimeBadgeCounter": "86400", "StarBadgeCounter": "0,5", "FeatherBadgeCounter": "86400"}, "board": [{"badge": "f0", "is_active": true, "is_last_modified": true}, {"badge": "s0", "is_active": null}, {"badge": "s1", "is_active": null}, {"badge": "c0", "is_active": null}], "level": 0, "c0_hp": 0, "c0_hp_next_delta": 3, "last_badge": "f0", "last_badge_at": 0, "c0_active_time_penalty": 0, "c0_lock_started_at": 0}')


    def test_grumpy_cat_gets_in(self):
        badges_manager = BadgesManager(2, '{"badges_state": {"CatBadgeCounter": '
                                          '"cumulative_counter_secs=0,counter_last_updated=0,update_reason=game_started", '
                                          '"TimeBadgeCounter": "86400", "StarBadgeCounter": "0,5", "FeatherBadgeCounter": "86400"}, '
                                          '"board": [{"badge": "f0", "is_active": true, "is_last_modified": true}, '
                                          '{"badge": "s0", "is_active": null}, {"badge": "s1", "is_active": null}, '
                                          '{"badge": "c0", "is_active": null}], "level": 0, "c0_hp": 0, "c0_hp_next_delta": 3, "last_badge": "f0", "last_badge_at": 0, "c0_active_time_penalty": 0, "c0_lock_started_at": 0}'
                                       )
        badge = badges_manager.on_penalty(61000)
        self.assertEqual(badge, "c0")
        self.assertEqual(badges_manager.get_level(), 0)
        self.assertEqual(badges_manager.get_board(), [{'badge': 'f0', 'is_active': True},
                                                                             {'badge': 's0', 'is_active': None},
                                                                             {'badge': 's1', 'is_active': None},
                                                                             {'badge': 'c0', 'is_active': True, 'is_last_modified': True}])

        self.assertEqual(badges_manager.is_level_completed(), False)
        self.assertEqual(badges_manager.serialize(), '{"badges_state": {"CatBadgeCounter": "cumulative_counter_secs=0,counter_last_updated=61000,update_reason=penalty", "TimeBadgeCounter": "86400", "StarBadgeCounter": "0,5,skip_next", "FeatherBadgeCounter": "86400"}, "board": [{"badge": "f0", "is_active": true}, {"badge": "s0", "is_active": null}, {"badge": "s1", "is_active": null}, {"badge": "c0", "is_active": true, "is_last_modified": true}], "level": 0, "c0_hp": 15, "c0_hp_next_delta": 1, "last_badge": "c0", "last_badge_at": 61000, "c0_active_time_penalty": 0, "c0_lock_started_at": 61000}')

    def test_no_grumpy_cat_small_levels(self):
        badges_manager = BadgesManager(0, '{"badges_state": {"CatBadgeCounter": '
                                          '"cumulative_counter_secs=0,counter_last_updated=0,update_reason=game_started", '
                                          '"TimeBadgeCounter": "86400", "StarBadgeCounter": "0,5", "FeatherBadgeCounter": "86400"}, '
                                          '"board": [{"badge": "f0", "is_active": true, "is_last_modified": true}, '
                                          '{"badge": "s0", "is_active": null}, {"badge": "s1", "is_active": null}, '
                                          '{"badge": "c0", "is_active": null}, {"badge": "c1", "is_active": null}], "level": 0, "c0_hp": 0, "c0_hp_next_delta": 3, "last_badge": "f0", "last_badge_at": 0, "c0_active_time_penalty": 0, "c0_lock_started_at": 0}'
                                       )
        badge = badges_manager.on_penalty(61000)
        self.assertEqual(badge, None)
        self.assertEqual(badges_manager.serialize(), '{"badges_state": '
                                                     '{"CatBadgeCounter": '
                                                     '"cumulative_counter_secs=0,counter_last_updated=61000,update_reason=penalty", '
                                                     '"TimeBadgeCounter": "86400", "StarBadgeCounter": "0,5,skip_next", '
                                                     '"FeatherBadgeCounter": "86400"}, '
                                                     '"board": ['
                                                     '{"badge": "f0", "is_active": true}, '
                                                     '{"badge": "s0", "is_active": null}, '
                                                     '{"badge": "s1", "is_active": null}, '
                                                     '{"badge": "c0", "is_active": null}, '
                                                     '{"badge": "c1", "is_active": null}], '
                                                     '"level": 0, "c0_hp": 0, "c0_hp_next_delta": 1, "last_badge": null, "last_badge_at": null, "c0_active_time_penalty": 0, "c0_lock_started_at": 0}')
        badges_manager.on_review(100000)
        self.assertEqual(badges_manager.serialize(), '{"badges_state": '
                                                     '{"CatBadgeCounter": "cumulative_counter_secs=0,counter_last_updated=100000,update_reason=review", '
                                                     '"TimeBadgeCounter": "86400", "StarBadgeCounter": "0,5", '
                                                     '"FeatherBadgeCounter": "86400"}, '
                                                     '"board": ['
                                                     '{"badge": "f0", "is_active": true}, '
                                                     '{"badge": "s0", "is_active": null}, '
                                                     '{"badge": "s1", "is_active": null}, '
                                                     '{"badge": "c0", "is_active": null}, '
                                                     '{"badge": "c1", "is_active": null}], '
                                                     '"level": 0, "c0_hp": 0, "c0_hp_next_delta": 3, "last_badge": null, "last_badge_at": null, "c0_active_time_penalty": 0, "c0_lock_started_at": 0}')
        badges_manager.on_review(120000)
        self.assertEqual(badges_manager.serialize(), '{"badges_state": '
                                                     '{"CatBadgeCounter": "cumulative_counter_secs=20000,counter_last_updated=120000,update_reason=review", '
                                                     '"TimeBadgeCounter": "86400", '
                                                     '"StarBadgeCounter": "1,5", "FeatherBadgeCounter": "86400"}, '
                                                     '"board": [{"badge": "f0", "is_active": true}, '
                                                     '{"badge": "s0", "is_active": null}, '
                                                     '{"badge": "s1", "is_active": null}, '
                                                     '{"badge": "c0", "is_active": null}, '
                                                     '{"badge": "c1", "is_active": null}], '
                                                     '"level": 0, "c0_hp": 0, "c0_hp_next_delta": 3, "last_badge": null, "last_badge_at": null, "c0_active_time_penalty": 0, "c0_lock_started_at": 0}')

        pass

    def test_grumpy_spoils_everything(self):
        badges_state = ('{"CatBadgeCounter": '
            '"cumulative_counter_secs=0,counter_last_updated=61000,update_reason=penalty", '
            '"TimeBadgeCounter": "86400", "StarBadgeCounter": "0,5,skip_next", "FeatherBadgeCounter": "86400"}')

        badges_manager = BadgesManager(2, '{"badges_state": ' + badges_state + ', '
                                          '"board": [{"badge": "f0", "is_active": true}, {"badge": "s0", "is_active": null}, '
                                          '{"badge": "s1", "is_active": null}, {"badge": "c0", "is_active": true, "is_last_modified": true}], '
                                          '"level": 0, "c0_hp": 15, "c0_hp_next_delta": 1, "last_badge": "c0", "last_badge_at": 61000, '
                                          '"c0_active_time_penalty": 0, "c0_lock_started_at": 61000}'
                                       )
        badge = badges_manager.on_review(1000000)
        self.assertEqual(badge, None)
        self.assertEqual(badges_manager.count_active_grumpy_cats_on_board(), 1)
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 14)
        self.assertEqual(badges_manager.serialize(), '{"badges_state": ' + badges_state +
                                                     ', '
                                                     '"board": [{"badge": "f0", "is_active": true}, {"badge": "s0", "is_active": null}, '
                                                     '{"badge": "s1", "is_active": null}, {"badge": "c0", "is_active": true}],'
                                                     ' "level": 0, "c0_hp": 14, "c0_hp_next_delta": 3, "last_badge": null, "last_badge_at": 61000, '
                                                     '"c0_active_time_penalty": 0, "c0_lock_started_at": 61000}')

    def test_kicking_out_grumpy_cat(self):
        badges_state = ('{"CatBadgeCounter": '
                        '"cumulative_counter_secs=0,counter_last_updated=61000,update_reason=penalty", '
                        '"TimeBadgeCounter": "86400", "StarBadgeCounter": "0,5,skip_next", "FeatherBadgeCounter": "86400"}')
        badges_manager = BadgesManager(2, '{"badges_state": ' + badges_state +
                                       ', '
                                       '"board": [{"badge": "f0", "is_active": true}, {"badge": "s0", "is_active": null}, '
                                       '{"badge": "s1", "is_active": null}, {"badge": "c0", "is_active": true}],'
                                       ' "level": 0, "c0_hp": 14, "c0_hp_next_delta": 3, "last_badge": null, "last_badge_at": 61000, '
                                       '"c0_active_time_penalty": 0, "c0_lock_started_at": 61000}')
        self.assertEqual(badges_manager.on_review(10), None)
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 11)
        self.assertEqual(badges_manager.on_review(11), None)
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 8)
        self.assertEqual(badges_manager.on_review(12), None)
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 5)
        self.assertEqual(badges_manager.on_review(13), None)
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 2)
        self.assertEqual(badges_manager.on_review(14), "c0_removed")
        self.assertEqual(badges_manager.get_board(), [{'badge': 'f0', 'is_active': True},
                                                                             {'badge': 's0', 'is_active': None},
                                                                             {'badge': 's1', 'is_active': None},
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
        badges_manager = BadgesManager(2, '{"badges_state": {}, "board": '
                                       '[{"badge": "f0", "is_active": true, "is_last_modified": true}, {"badge": "s0", '
                                       '"is_active": null}, {"badge": "c0", "is_active": null}], "level": 0, "last_badge": "f0"}')
        for i in range(0, 4):
            print(i)
            badge = badges_manager.on_review(100000)
            self.assertEqual(badge, None)
            self.assertEqual(badges_manager.is_level_completed(), False)

        badge = badges_manager.on_review(100000)
        self.assertEqual(badge, "s0")
        self.assertEqual(badges_manager.is_level_completed(), True)

        self.assertEqual(badges_manager.get_next_level_board(), [{'badge': 's1'},
                                                                 {'badge': 't0'},
                                                                 {'badge': 'c0'},
                                                                 {'badge': 'c1'},
                                                                 {'badge': 'c0'}])
        badge = badges_manager.on_review(102600 - 1200)
        self.assertEqual(badges_manager.progress(102600 - 1200), {'c0': {'badge': 'c0',
                                                                         'challenge': 'review',
                                                                         'progress_pct': 100,
                                                                         'remaining_reviews': 0},
                                                                  'c1': {'badge': 'c1',
                                                                         'challenge': 'review_regularly_no_penalty',
                                                                         'progress_pct': 3,
                                                                         'remaining_time_secs': 56200},
                                                                  's1': {'badge': 's1',
                                                                         'challenge': 'review_regularly_no_penalty',
                                                                         'progress_pct': 10,
                                                                         'remaining_reviews': 9},
                                                                  't0': {'badge': 't0',
                                                                         'challenge': 'play_time',
                                                                         'progress_pct': 1,
                                                                         'remaining_time_secs': 85000}}) # must be less than 86400 to accomodate time passed since level was over
        self.assertEqual(badge, None) # first review, the level has started
        badge = badges_manager.on_review(1100001)
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
        badges_manager = BadgesManager(2, '{"badges_state": {},"board": '
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
                                                              'progress_pct': 0,
                                                              'remaining_time_secs': 86400}})
        badges_manager.on_review(600)
        badge = badges_manager.on_penalty(800)
        self.assertEqual(badge, 'c0')
        self.assertEqual(badges_manager.count_active_grumpy_cats_on_board(), 2)
        self.assertEqual(badges_manager.get_board(), [{'badge': 't0', 'is_active': False},
                                                      {'badge': 'c0', 'is_active': True},
                                                      {'badge': 'c0', 'is_active': True, 'is_last_modified': True}])
        badge = badges_manager.on_penalty(70)
        self.assertEqual(badge, None)

        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 14)
        badges_manager.on_review(800)
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 13)
        self.assertEqual(badges_manager.progress(800), {'c0': {'badge': 'c0',
                                                               'challenge': 'review',
                                                               'progress_pct': 14,
                                                               'remaining_reviews': 13},
                                                        't0': {'badge': 't0',
                                                               'challenge': 'play_time',
                                                               'progress_pct': 0,
                                                               'remaining_time_secs': 86400}})
        badges_manager.on_review(900)
        badges_manager.on_review(1000)
        badges_manager.on_review(1100)
        badges_manager.on_review(1200)
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 1)
        self.assertEqual(badges_manager.on_review(2000), 'c0_removed')
        self.assertEqual(badges_manager.get_grumpy_cat_healthpoints(), 15)
        self.assertEqual(badges_manager.progress(2000), {'c0': {'badge': 'c0',
                                                                'challenge': 'review',
                                                                'progress_pct': 0,
                                                                'remaining_reviews': 15},
                                                         't0': {'badge': 't0',
                                                                'challenge': 'play_time',
                                                                'progress_pct': 0,
                                                                'remaining_time_secs': 86400}})
        self.assertEqual(badges_manager.get_board(), [{'badge': 't0', 'is_active': False},
                                                      {'badge': 'c0', 'is_active': False, 'is_last_modified': True},
                                                      {'badge': 'c0', 'is_active': True}])
        badges_manager.on_review(2030)
        badges_manager.on_review(2040)
        badges_manager.on_review(2050)
        badges_manager.on_review(2060)
        badges_manager.on_review(2070)
        self.assertEqual(badges_manager.get_board(), [{'badge': 't0', 'is_active': False},
                                                      {'badge': 'c0', 'is_active': False},
                                                      {'badge': 'c0', 'is_active': False, 'is_last_modified': True}])
        self.assertEqual(badges_manager.progress(3000), {'c0': {'badge': 'c0',
                                                                'challenge': 'review',
                                                                'progress_pct': 100,
                                                                'remaining_reviews': 0},
                                                         't0': {'badge': 't0',
                                                                'challenge': 'play_time',
                                                                'progress_pct': 0,
                                                                'remaining_time_secs': 86400}})
        badges_manager.on_review(3500)
        self.assertEqual(badges_manager.get_board(), [{'badge': 't0', 'is_active': False},
                                                      {'badge': 'c0', 'is_active': False},
                                                      {'badge': 'c0', 'is_active': False}])
        self.assertEqual(badges_manager.progress(4750), {'c0': {'badge': 'c0',
                                                                'challenge': 'review',
                                                                'progress_pct': 100,
                                                                'remaining_reviews': 0},
                                                         't0': {'badge': 't0',
                                                                'challenge': 'play_time',
                                                                'progress_pct': 1,
                                                                'remaining_time_secs': 85150}})
        self.assertEqual(badges_manager.on_review(100000), 't0')

    def test_new_level_empty_progress(self):
        badges_manager = BadgesManager(2, '{"badges_state": {}, '
                                          '"board": [{"badge": "f0", "is_active": true, "is_last_modified": true}, '
                                          '{"badge": "s0", "is_active": true}, '
                                          '{"badge": "s1", "is_active": true}, '
                                          '{"badge": "c0", "is_active": false}], "level": 0, "c0_hp": 0, "c0_hp_next_delta": 3, "last_badge": "f0", "c0_active_time_penalty": 32951, "c0_lock_started_at": 116774}')
        self.assertEqual(badges_manager.new_level_empty_progress(), {'c1': {'badge': 'c1',
                                                                            'challenge': 'review_regularly_no_penalty',
                                                                            'progress_pct': 0,
                                                                            'remaining_time_secs': 57600},
                                                                     's1': {'badge': 's1',
                                                                            'challenge': 'review_regularly_no_penalty',
                                                                            'progress_pct': 0,
                                                                            'remaining_reviews': 10},
                                                                     't0': {'badge': 't0',
                                                                            'challenge': 'play_time',
                                                                            'progress_pct': 0,
                                                                            'remaining_time_secs': 86400}});
