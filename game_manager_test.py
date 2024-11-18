import datetime
import os
import unittest

import time_machine
import time

from autopause_manager import AutopauseManager
from badges_manager import BadgesManager
from counter import Counter
from game_manager import GameManager
from users_orm import UsersOrm

MENU_COMMANDS = [['review', '💫️review Formula'],
                 ['pause', '⏸️ pause the game'],
                 ['sleep', '💤 sleep scheduler'],
                 ['formula', '️🧪update Formula'],
                 ['stats', '📊 game progress'],
                 ['difficulty', '💪change difficulty'],
                 ['data', '💾 view your raw data'],
                 ['feedback', '📢 send feedback']]


class TestGameManager(unittest.IsolatedAsyncioTestCase):

    users_orm: UsersOrm

    def setUp(self):
        try:
            os.unlink('test.db')
        except FileNotFoundError:
            pass
        self.users_orm = UsersOrm('test.db')
        self.game_manager = GameManager('test.db', 'prod', 'http://frontend')
        self.maxDiff = None

    def tearDown(self):
        self.users_orm.__del__()
        try:
            os.unlink('test.db')
        except FileNotFoundError:
            pass

    @time_machine.travel("2022-04-21", tick=False)
    def test_on_start_game_starts(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_data_provided(1, 'start_game;next_review:10:00,,11:00,,12:00,,13:00,,14:00')

        self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula" 💫',
                                              'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                             {'text': 'View achievements 🏆',
                                              'url': 'http://frontend?lang=en&env=prod&new_badge=f0&level=1&b1=f0am_s0_c0&bp1=c0_0_100--s0_3_0&ts=1650463200'}],
                                 'image': None,
                                 'menu_commands': [],
                                 'message': 'The game has started 🏁\n'
                                            '\n'
                                            "🏆 You've got a new achievement!\n"
                                            'Press "View achievements" button below.\n'
                                            '\n'
                                            '💪<a '
                                            'href="https://mindwarriorgame.org/faq.en.html#difficulty">Difficulty '
                                            'level</a>: Easy\n'
                                            '\n'
                                            'Review your <i>Formula</i> before 11:00\n'
                                            '\n'
                                            ' ‣ /difficulty - change the difficulty',
                                 'to_chat_id': 1}])

        user = self.users_orm.get_user_by_id(1)

        self.assertIsNone(user['paused_counter_state'])
        self.assertIsNotNone(user['active_game_counter_state'])

        counter = Counter(user['active_game_counter_state'])
        self.assertTrue(counter.is_active())

        self.assertEqual(user['difficulty'], 1)
        self.assertEqual(user['next_prompt_time'], datetime.datetime(2022, 4, 21, 2, 45).astimezone(datetime.timezone.utc))
        self.assertEqual(user['next_prompt_type'], 'reminder')

        self.assertIsNotNone(user['review_counter_state'])
        counter = Counter(user['review_counter_state'])
        self.assertTrue(counter.is_active())
        badges = BadgesManager(user['difficulty'], user['badges_serialized'])
        self.assertEqual(badges.get_last_badge(), "f0")
        self.assertEqual(counter.get_total_seconds(), 0)

    def test_on_invalid_input_renders_prompt(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_data_provided(1, "not valid message")
        self.assertEqual(data, [{'buttons': [{'text': 'Write "Formula" and start playing! 🏁',
                                              'url': 'http://frontend?env=prod&lang_code=en&new_game=1&next_review_prompt_minutes=360,180,90,60,45&shared_key_uuid=' + user["shared_key_uuid"]}],
                                 'image': None,
                                 'menu_commands': [],
                                 'message': 'Please press the button below to enter your <i>Formula</i> and '
                                            'start the game.',
                                 'to_chat_id': 1}])
    @time_machine.travel("2022-04-21", tick=False)
    def test_not_generating_prompt_if_game_was_started(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        self.users_orm.upsert_user(user)

        self.game_manager.on_data_provided(1, 'start_game;next_review:10:00,,11:00,,12:00,,13:00,,14:00')
        data = self.game_manager.on_data_provided(1, "not valid message")
        self.assertEqual(data, [{'buttons': [],
                                 'image': None,
                                 'menu_commands': [],
                                 'message': 'Invalid data',
                                 'to_chat_id': 1}])


    @time_machine.travel("2022-04-21", tick=False)
    def test_process_tick_sends_reminders(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        user['difficulty'] = 0
        self.users_orm.upsert_user(user)
        self.game_manager.on_data_provided(1, "start_game;next_review:10:00,,11:00,,12:00,,13:00,,14:00")
        user = self.users_orm.get_user_by_id(1)
        with time_machine.travel("2022-04-21 05:50", tick=False):
            data = self.game_manager.process_tick()
            self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula" 💫',
                                                  'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                                 {'text': 'View achievements 🏆',
                                                  'url': 'http://frontend?lang=en&env=prod&level=1&b1=f0a_s0_c0&bp1=c0_0_100--s0_3_0&ts=1650484200'}],
                                     'image': None,
                                     'menu_commands': [],
                                     'message': "Don't forget to review your <i>Formula</i>! ⏰\n"
                                                '\n'
                                                'The due time is in 15 minutes, hurry up!\n'
                                                '\n'
                                                ' ‣ /pause - pause the game\n'
                                                ' ‣ /sleep - configure sleep scheduler',
                                     'to_chat_id': 1}])
            user = self.users_orm.get_user_by_id(1)
            self.assertEqual(user['next_prompt_time'], datetime.datetime(2022, 4, 21, 6, 5).astimezone(datetime.timezone.utc))
            self.assertEqual(user['next_prompt_type'], 'penalty')

    def test_on_start_command(self):
        data = self.game_manager.on_review_command(1)
        self.assertEqual(data, {'buttons': [],
                                'image': None,
                                'menu_commands': [],
                                'message': '/en - English\n'
                                           '\n'
                                           '/de - Deutsch\n'
                                           '\n'
                                           '/es - Español\n'
                                           '\n'
                                           '/fr - Français\n'
                                           '\n'
                                           '/ru - Русский\n'
                                           '\n',
                                'to_chat_id': 1})


    @time_machine.travel("2022-04-21", tick=False)
    def test_process_tick_brings_grumpy_cat(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        user['difficulty'] = 0
        self.users_orm.upsert_user(user)
        self.game_manager.on_data_provided(1, "start_game;next_review:10:00,,11:00,,12:00,,13:00,,14:00")

        user = self.users_orm.get_user_by_id(1)
        with time_machine.travel("2022-04-21 05:50", tick=False):
            data = self.game_manager.process_tick()
            self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula" 💫',
                                                  'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                                 {'text': 'View achievements 🏆',
                                                  'url': 'http://frontend?lang=en&env=prod&level=1&b1=f0a_s0_c0&bp1=c0_0_100--s0_3_0&ts=1650484200'}],
                                     'image': None,
                                     'menu_commands': [],
                                     'message': "Don't forget to review your <i>Formula</i>! ⏰\n"
                                                '\n'
                                                'The due time is in 15 minutes, hurry up!\n'
                                                '\n'
                                                ' ‣ /pause - pause the game\n'
                                                ' ‣ /sleep - configure sleep scheduler',
                                     'to_chat_id': 1}])
            with time_machine.travel("2022-04-21 06:10", tick=False):
                data = self.game_manager.process_tick()
                self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula" 💫',
                                                      'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                                     {'text': 'View achievements 🏆',
                                                      'url': 'http://frontend?lang=en&env=prod&new_badge=c0&level=1&b1=f0a_s0_c0am&bp1=c0_5_0--s0_3_0&ts=1650485400'}],
                                         'image': None,
                                         'menu_commands': [],
                                         'message': 'You forgot to review your <i>Formula</i> 🟥\n'
                                                    '\n'
                                                    '😾 Oops! A grumpy cat sneaked in!\n'
                                                    'Press "View achievements" button below.\n'
                                                    '\n'
                                                    ' ‣ /pause - pause the game\n'
                                                    ' ‣ /sleep - configure sleep scheduler',
                                         'to_chat_id': 1}])
                user = self.users_orm.get_user_by_id(1)
                self.assertEqual(user['next_prompt_time'], datetime.datetime(2022, 4, 21, 11, 55).astimezone(datetime.timezone.utc))
                self.assertEqual(user['next_prompt_type'], 'reminder')
                badges = BadgesManager(user['difficulty'], user['badges_serialized'])
                self.assertEqual(badges.get_last_badge(), "c0")

    @time_machine.travel("2022-04-21", tick=False)
    def test_process_tick_grumpy_cat_blocking(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        user['difficulty'] = 0
        self.users_orm.upsert_user(user)

        self.game_manager.on_data_provided(1, "start_game;next_review:10:00,,11:00,,12:00,,13:00,,14:00")

        user = self.users_orm.get_user_by_id(1)
        badges = BadgesManager(user['difficulty'], user['badges_serialized'])
        badges.on_penalty(0)
        user['badges_serialized'] = badges.serialize()
        self.users_orm.upsert_user(user)

        with time_machine.travel("2022-04-21 05:50", tick=False):
            data = self.game_manager.process_tick()
            self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula" 💫',
                                                  'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                                 {'text': 'View achievements 🏆',
                                                  'url': 'http://frontend?lang=en&env=prod&level=1&b1=f0a_s0_c0a&bp1=c0_5_0--s0_3_0&ts=1650484200'}],
                                     'image': None,
                                     'menu_commands': [],
                                     'message': "Don't forget to review your <i>Formula</i>! ⏰\n"
                                                '\n'
                                                'The due time is in 15 minutes, hurry up!\n'
                                                '\n'
                                                ' ‣ /pause - pause the game\n'
                                                ' ‣ /sleep - configure sleep scheduler',
                                     'to_chat_id': 1}])
            with time_machine.travel("2022-04-21 06:10", tick=False):
                data = self.game_manager.process_tick()
                self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula" 💫',
                                                      'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                                     {'text': 'View achievements 🏆',
                                                      'url': 'http://frontend?lang=en&env=prod&level=1&b1=f0a_s0_c0a&bp1=c0_5_0--s0_3_0&ts=1650485400'}],
                                         'image': None,
                                         'menu_commands': [],
                                         'message': 'You forgot to review your <i>Formula</i> 🟥\n'
                                                    '\n'
                                                    '⛔🏆😾 A grumpy cat is blocking new achievements!\n'
                                                    '\n'
                                                    ' ‣ /pause - pause the game\n'
                                                    ' ‣ /sleep - configure sleep scheduler',
                                         'to_chat_id': 1}])
                user = self.users_orm.get_user_by_id(1)
                self.assertEqual(user['next_prompt_time'], datetime.datetime(2022, 4, 21, 11, 55).astimezone(datetime.timezone.utc))
                self.assertEqual(user['next_prompt_type'], 'reminder')


    @time_machine.travel("2022-04-21", tick=False)
    def test_on_review_first_time(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(65)
        user['review_counter_state'] = counter.serialize()
        user['difficulty']  = 4
        user['lang_code'] = 'en'
        user['review_counter_state'] = counter.serialize()
        user['active_game_counter_state'] = counter.serialize()
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_review_command(1)
        self.assertEqual(data, {'buttons': [{'text': 'Improve yourself 💪',
                                             'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                            {'text': 'Improve the world 🙌',
                                             'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'}],
                                'image': None,
                                'menu_commands': MENU_COMMANDS,
                                'message': 'Review your <i> Formula</i> 💫\n'
                                           '\n'
                                           '<a '
                                           "href='https://mindwarriorgame.org/faq.en#name.betterworld'>Press "
                                           'any button below</a> to review your <i>Formula</i>.',
                                'to_chat_id': 1})

    @time_machine.travel("2022-04-21", tick=False)
    def test_on_review_next_time(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(65)
        user['review_counter_state'] = counter.serialize()
        user['difficulty']  = 4
        user['lang_code'] = 'en'
        user['review_counter_state'] = counter.serialize()
        counter.move_time_back(25)
        user['active_game_counter_state'] = counter.serialize()
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_review_command(1)
        self.assertEqual(data, {'buttons': [{'text': 'Improve yourself 💪',
                                             'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                            {'text': 'Improve the world 🙌',
                                             'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'}],
                                'image': None,
                                'menu_commands': MENU_COMMANDS,
                                'message': 'Time since the last review: 0d 1h 5m\n'
                                           'Review your <i> Formula</i> 💫\n'
                                           '\n'
                                           '<a '
                                           "href='https://mindwarriorgame.org/faq.en#name.betterworld'>Press "
                                           'any button below</a> to review your <i>Formula</i>.',
                                'to_chat_id': 1})

    @time_machine.travel("2022-04-21", tick=False)
    def test_on_start_game_reset_existing_game(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(1)
        user['paused_counter_state'] = counter.serialize()
        user['difficulty']  = 4
        user['lang_code'] = 'en'
        user['review_counter_state'] = counter.serialize()
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_data_provided(1, 'start_game;next_review:10:00,,11:00,,12:00,,13:00,,14:00')

        self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula" 💫',
                                              'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                             {'text': 'View achievements 🏆',
                                              'url': 'http://frontend?lang=en&env=prod&new_badge=f0&level=1&b1=f0am_s0_s1_s2_c0&bp1=c0_0_100--s0_7_0&ts=1650463200'}],
                                 'image': None,
                                 'menu_commands': [],
                                 'message': 'The game has started 🏁\n'
                                            '\n'
                                            "🏆 You've got a new achievement!\n"
                                            'Press "View achievements" button below.\n'
                                            '\n'
                                            '💪<a '
                                            'href="https://mindwarriorgame.org/faq.en.html#difficulty">Difficulty '
                                            'level</a>: Expert\n'
                                            '\n'
                                            'Review your <i>Formula</i> before 14:00\n'
                                            '\n'
                                            ' ‣ /difficulty - change the difficulty',
                                 'to_chat_id': 1}])

        user = self.users_orm.get_user_by_id(1)
        self.assertIsNone(user['paused_counter_state'])
        self.assertIsNotNone(user['active_game_counter_state'])
        counter = Counter(user['active_game_counter_state'])
        self.assertTrue(counter.is_active())
        self.assertLess(abs(counter.get_total_seconds()), 0.001)
        self.assertEqual(user['difficulty'], 4)
        self.assertEqual(user['next_prompt_time'], datetime.datetime(2022, 4, 21, 0, 45).astimezone(datetime.timezone.utc))
        counter = Counter(user['review_counter_state'])
        self.assertEqual(counter.is_active(), True)
        self.assertEqual(counter.get_total_seconds(), 0)

        data = self.game_manager.on_data_provided(1, 'reviewed_at:' + str(int(time.time())) + ';next_review:12:13 am,,12:14 am,,12:15 am,,12:16 am,,12:17 am')
        self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula" 💫',
                                              'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                             {'text': 'View achievements 🏆',
                                              'url': 'http://frontend?lang=en&env=prod&level=1&b1=f0a_s0_s1_s2_c0&bp1=c0_0_100--s0_6_14&ts=1650463200'}],
                                 'image': None,
                                 'menu_commands': MENU_COMMANDS,
                                 'message': '<i>Formula</i> has been reviewed 🎉\n'
                                            '\n'
                                            'Next review before 12:17 am\n'
                                            '\n'
                                            ' ‣ /pause - pause the game\n'
                                            ' ‣ /sleep - configure sleep scheduler',
                                 'to_chat_id': 1}])


    @time_machine.travel("2022-04-22")
    def test_set_difficulty_renders_start_button(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_data_provided(1, 'set_difficulty:1')[0]

        self.assertEqual(data['to_chat_id'], 1)
        self.assertEqual(data['message'].index('stranger') >= 0, True)
        self.assertEqual(data['buttons'], [{'text': 'Write "Formula" and start playing! 🏁',
                                            'url': 'http://frontend?env=prod&lang_code=en&new_game=1&next_review_prompt_minutes=360,180,90,60,45&shared_key_uuid=' + user['shared_key_uuid']}])

    @time_machine.travel("2022-04-22", tick=False)
    def test_set_difficulty_updates_resets_scores(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(15)
        user['paused_counter_state'] = counter.serialize()
        user['badges_serialized'] = 'blah'
        user['difficulty']  = 2
        user['active_game_counter_state'] = counter.serialize()
        user['lang_code'] = 'en'
        user['review_counter_state'] = counter.serialize()
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_data_provided(1, 'set_difficulty:3;next_review:05:29,,02:29,,00:59,,00:29,,00:14')[0]

        self.assertEqual(data, {'buttons': [{'text': 'Review your "Formula" 💫',
                                             'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'}],
                                'image': None,
                                'menu_commands': [],
                                'message': 'The game is resumed.\n'
                                           'The difficulty level has been changed 💪\n'
                                           'The game was restarted due to the change of the difficulty '
                                           'level.\n'
                                           '\n'
                                           '<b>Medium -> Hard</b>\n'
                                           '\n'
                                           '🏆 Level: 1\n'
                                           '⏳ Play time: 0d 0h 0m\n'
                                           '\n'
                                           'Next review before 00:29\n',
                                'to_chat_id': 1})
        user = self.users_orm.get_user_by_id(1)
        self.assertEqual(user['difficulty'], 3)
        self.assertIsNone(user['paused_counter_state'])
        self.assertEqual(user['next_prompt_time'], datetime.datetime(2022, 4, 22, 1, 0).astimezone(datetime.timezone.utc))
        self.assertEqual(user['next_prompt_type'], 'penalty')

        counter = Counter(user['active_game_counter_state'])
        self.assertTrue(counter.is_active())
        self.assertEqual(counter.get_total_seconds(), 0)

        self.assertIsNotNone(user['active_game_counter_state'])
        counter = Counter(user['active_game_counter_state'])
        self.assertTrue(counter.is_active())
        self.assertEqual(counter.get_total_seconds(), 0)

        self.assertIsNone(user['counters_history_serialized'])
        self.assertEqual(user['badges_serialized'], '')

    @time_machine.travel("2022-04-22", tick=False)
    def test_set_difficulty_sets_next_reminder_for_low_levels(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(15)
        user['paused_counter_state'] = counter.serialize()
        user['difficulty']  = 2
        user['active_game_counter_state'] = counter.serialize()
        user['lang_code'] = 'en'
        user['review_counter_state'] = counter.serialize()
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_data_provided(1, 'set_difficulty:1;next_review:05:29,,02:29,,00:59,,00:29,,00:14')[0]

        self.assertEqual(data, {'buttons': [{'text': 'Review your "Formula" 💫',
                                             'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'}],
                                'image': None,
                                'menu_commands': [],
                                'message': 'The game is resumed.\n'
                                           'The difficulty level has been changed 💪\n'
                                           'The game was restarted due to the change of the difficulty '
                                           'level.\n'
                                           '\n'
                                           '<b>Medium -> Easy</b>\n'
                                           '\n'
                                           '🏆 Level: 1\n'
                                           '⏳ Play time: 0d 0h 0m\n'
                                           '\n'
                                           'Next review before 02:29\n',
                                'to_chat_id': 1})
        user = self.users_orm.get_user_by_id(1)
        self.assertEqual(user['difficulty'], 1)
        self.assertIsNone(user['paused_counter_state'])
        self.assertEqual(user['next_prompt_time'], datetime.datetime(2022, 4, 22, 2, 45).astimezone(datetime.timezone.utc))
        self.assertEqual(user['next_prompt_type'], 'reminder')


    @time_machine.travel("2022-04-22", tick=False)
    def test_set_difficulty_updates_difficulty_sets_next_prompt_type_correctly_for_high_levels(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(15)
        user['paused_counter_state'] = counter.serialize()
        user['difficulty']  = 2
        user['active_game_counter_state'] = counter.serialize()
        user['lang_code'] = 'en'
        user['review_counter_state'] = counter.serialize()
        self.users_orm.upsert_user(user)

        self.game_manager.on_data_provided(1, 'set_difficulty:4;next_review:05:29,,02:29,,00:59,,00:29,,00:14')[0]

        user = self.users_orm.get_user_by_id(1)
        self.assertEqual(user['next_prompt_time'], datetime.datetime(2022, 4, 22, 0, 45).astimezone(datetime.timezone.utc))
        self.assertEqual(user['next_prompt_type'], 'penalty')


    @time_machine.travel("2022-04-22", tick=False)
    def test_on_stats_no_graph(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(15)
        user['paused_counter_state'] = counter.serialize()
        user['difficulty']  = 2
        user['active_game_counter_state'] = counter.serialize()
        user['next_prompt_time'] = datetime.datetime(2022, 4, 22, 1, 45).astimezone(datetime.timezone.utc)
        user['lang_code'] = 'en'
        user['review_counter_state'] = counter.serialize()
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_stats_command(1)
        self.assertEqual(data, {'buttons': [{'text': 'View achievements 🏆',
                                             'url': 'http://frontend?lang=en&env=prod&level=1&b1=f0_s0_s1_c0&bp1=c0_0_100--s0_5_0--f0_86400_0&ts=1650549600'}],
                                'image': None,
                                'menu_commands': [],
                                'message': '🏆 Level : 1\n'
                                           '⌛ Active play time: 0d 0h 15m\n'
                                           '💪 <a '
                                           'href="https://mindwarriorgame.org/faq.en.html#difficulty">Difficulty</a>: '
                                           'Medium (3/5)\n'
                                           '⏸️ <a '
                                           'href="https://mindwarriorgame.org/faq.en.html#pause">Paused?</a> '
                                           '🟢\n'
                                           '❄️ <a '
                                           'href="https://mindwarriorgame.org/faq.en.html#difficulty:~:text=will%20be%20rewarded%20(-,%22cool%2Ddown%22%20rule,-).">Cool-down</a> '
                                           'time before next reward: 0m 0s\n'
                                           '⏰ Time before next <a '
                                           'href="https://mindwarriorgame.org/faq.en.html#forgot">reminder</a>: '
                                           '1h 45m',
                                'to_chat_id': 1})

    @time_machine.travel("2022-04-22", tick=False)
    def test_on_stats_unpaused(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(15)
        user['paused_counter_state'] = None
        user['active_game_counter_state'] = counter.serialize()
        user['next_prompt_time'] = datetime.datetime(2022, 4, 22, 1, 45).astimezone(datetime.timezone.utc)
        user['lang_code'] = 'en'
        user['review_counter_state'] = counter.serialize()
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_stats_command(1)
        self.assertIn("⚪", data['message'])


    def test_difficulty_command_renders_set_difficulty_buttons(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_difficulty_command(1)

        self.assertEqual(data, {'buttons': [{'text': 'Beginner (6h)',
                                             'url': 'http://frontend?env=prod&lang_code=en&set_difficulty=0&next_review_prompt_minutes=360,180,90,60,45'},
                                            {'text': 'Easy (3h) - current level',
                                             'url': 'http://frontend?env=prod&lang_code=en&set_difficulty=1&next_review_prompt_minutes=360,180,90,60,45'},
                                            {'text': 'Medium (1h 30m)',
                                             'url': 'http://frontend?env=prod&lang_code=en&set_difficulty=2&next_review_prompt_minutes=360,180,90,60,45'},
                                            {'text': 'Hard (1h)',
                                             'url': 'http://frontend?env=prod&lang_code=en&set_difficulty=3&next_review_prompt_minutes=360,180,90,60,45'},
                                            {'text': 'Expert (45m)',
                                             'url': 'http://frontend?env=prod&lang_code=en&set_difficulty=4&next_review_prompt_minutes=360,180,90,60,45'}],
                                'image': None,
                                'menu_commands': [],
                                'message': 'Change the difficulty level💪\n'
                                           '\n'
                                           'Select a new <a '
                                           'href="https://mindwarriorgame.org/faq.en.html#difficulty">difficulty '
                                           'level</a> using the buttons below.\n'
                                           '\n'
                                           '<b>⚠️This will reset your game progress!</b>\n',
                                'to_chat_id': 1})

    def test_on_pause_renders_start_button(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_pause_command(1)

        self.assertEqual(data['to_chat_id'], 1)
        self.assertGreater(data['message'].index(', stranger!'), 0)
        self.assertEqual(data['buttons'], [{'text': 'Write "Formula" and start playing! 🏁',
                                            'url': 'http://frontend?env=prod&lang_code=en&new_game=1&next_review_prompt_minutes=360,180,90,60,45&shared_key_uuid=' + user['shared_key_uuid']}])

    def test_on_pause_puts_counter_to_pause(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        self.users_orm.upsert_user(user)
        self.game_manager.on_data_provided(1, 'start_game;next_review:10:00,,11:00,,12:00')

        data = self.game_manager.on_pause_command(1)

        user = self.users_orm.get_user_by_id(1)

        self.assertIsNotNone(user['paused_counter_state'])
        counter = Counter(user['paused_counter_state'])
        self.assertTrue(counter.is_active())
        self.assertGreater(counter.get_total_seconds(), 0)

        self.assertIsNotNone(user['active_game_counter_state'])
        counter = Counter(user['active_game_counter_state'])
        self.assertFalse(counter.is_active())
        self.assertGreater(counter.get_total_seconds(), 0)

        self.assertIsNotNone(user['review_counter_state'])
        counter = Counter(user['review_counter_state'])
        self.assertFalse(counter.is_active())
        self.assertGreater(counter.get_total_seconds(), 0)

        self.assertEqual(data, {'buttons': [{'text': 'Review your "Formula" 💫',
                                             'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'}],
                                'image': None,
                                'menu_commands': [],
                                'message': 'The game is paused ⏸️\n'
                                           '\n'
                                           'You will not be receiving reminders about your <i>Formula</i>, '
                                           'and the active play time counter <a '
                                           'href="https://mindwarriorgame.org/faq.en#pause">are frozen</a>.\n'
                                           '\n'
                                           'To resume the game, simply review your <i>Formula</i> using the '
                                           'button below.',
                                'to_chat_id': 1})

    @time_machine.travel("2022-04-21", tick=False)
    def test_on_formula_reviewed_resumed(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(15)
        user['paused_counter_state'] = counter.serialize()
        user['difficulty']  = 2
        counter.move_time_back(10)
        user['active_game_counter_state'] = counter.serialize()
        user['review_counter_state'] = counter.serialize()
        user['lang_code'] = 'en'
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_data_provided(1, 'reviewed_at:' + str(int(time.time())) + ';next_review:12:15 am,,12:16 am,,12:17 am')

        self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula" 💫',
                                              'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                             {'text': 'View achievements 🏆',
                                              'url': 'http://frontend?lang=en&env=prod&level=1&b1=f0_s0_s1_c0&bp1=c0_0_100--s0_4_20--f0_86400_0&ts=1650463200'}],
                                 'image': None,
                                 'menu_commands': MENU_COMMANDS,
                                 'message': 'The game is resumed.\n'
                                            '<i>Formula</i> has been reviewed 🎉\n'
                                            '\n'
                                            'Next review before 12:17 am\n'
                                            '\n'
                                            ' ‣ /pause - pause the game\n'
                                            ' ‣ /sleep - configure sleep scheduler',
                                 'to_chat_id': 1}])
        user = self.users_orm.get_user_by_id(1)
        self.assertEqual(user['counters_history_serialized'], '['
                                                              '{"counter_name": "paused", "counter_stopped_duration_secs": 900, "event_datetime": {"_isoformat": "2022-04-20T14:00:00+00:00"}}, '
                                                              '{"counter_name": "review", "counter_stopped_duration_secs": 1500, "event_datetime": {"_isoformat": "2022-04-20T14:00:00+00:00"}}]')
        badges = BadgesManager(user['difficulty'], user['badges_serialized'])
        self.assertEqual(badges.is_level_completed(), False)
        self.assertEqual(user['next_prompt_type'], 'reminder')
        self.assertEqual(user['next_prompt_time'], datetime.datetime(2022, 4, 21, 1, 15).astimezone(datetime.timezone.utc))


    @time_machine.travel("2022-04-21", tick=False)
    def test_on_formula_reviewed_adds_badges(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(15)
        user['paused_counter_state'] = counter.serialize()
        user['difficulty']  = 0
        counter.move_time_back(10)
        user['active_game_counter_state'] = counter.serialize()
        user['review_counter_state'] = counter.serialize()
        user['lang_code'] = 'en'
        user['next_prompt_type'] = 'reminder'
        badges = BadgesManager(user['difficulty'], user['badges_serialized'])
        badges.on_review(0)
        badges.on_review(0)
        user['badges_serialized'] = badges.serialize()
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_data_provided(1, 'reviewed_at:' + str(int(time.time())) + ';next_review:12:15 am,,12:16 am,,12:17 am')

        self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula" 💫',
                                              'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                             {'text': 'View achievements 🏆',
                                              'url': 'http://frontend?lang=en&env=prod&new_badge=s0&level=1&b1=f0_s0am_c0&bp1=c0_0_100--f0_41700_3&ts=1650463200'}],
                                 'image': None,
                                 'menu_commands': MENU_COMMANDS,
                                 'message': 'The game is resumed.\n'
                                            '<i>Formula</i> has been reviewed 🎉\n'
                                            '\n'
                                            "🏆 You've got a new achievement!\n"
                                            'Press "View achievements" button below.\n'
                                            '\n'
                                            'Next review before 12:15 am\n'
                                            '\n'
                                            ' ‣ /pause - pause the game\n'
                                            ' ‣ /sleep - configure sleep scheduler',
                                 'to_chat_id': 1}])

    @time_machine.travel("2022-04-21", tick=False)
    def test_not_rendering_sleep_prompt_if_autopause_enabled(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(15)
        user['difficulty']  = 0
        user['active_game_counter_state'] = counter.serialize()
        user['review_counter_state'] = counter.serialize()
        user['lang_code'] = 'en'
        user['next_prompt_type'] = 'reminder'
        autopause_manager = AutopauseManager(user['autopause_config_serialized'])
        autopause_manager.update(True, 'Asia/Tokyo', 12 * 3600, '00:05', '00:15')
        user['autopause_config_serialized'] = autopause_manager.serialize()
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_data_provided(1, 'reviewed_at:' + str(int(time.time())) + ';next_review:12:15 am,,12:16 am,,12:17 am')

        self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula" 💫',
                                              'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                             {'text': 'View achievements 🏆',
                                              'url': 'http://frontend?lang=en&env=prod&level=1&b1=f0_s0_c0&bp1=c0_0_100--s0_2_33--f0_43200_0&ts=1650463200'}],
                                 'image': None,
                                 'menu_commands': MENU_COMMANDS,
                                 'message': '<i>Formula</i> has been reviewed 🎉\n'
                                            '\n'
                                            'Next review before 12:15 am\n'
                                            '\n'
                                            ' ‣ /pause - pause the game',
                                 'to_chat_id': 1}])

    @time_machine.travel("2022-04-21", tick=False)
    def test_on_formula_reviewed_not_showing_grumpy_cat(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(15)
        user['paused_counter_state'] = counter.serialize()
        user['difficulty']  = 0
        counter.move_time_back(10)
        user['active_game_counter_state'] = counter.serialize()
        user['review_counter_state'] = counter.serialize()
        user['lang_code'] = 'en'
        user['next_prompt_type'] = 'reminder'
        badges = BadgesManager(user['difficulty'], user['badges_serialized'])
        badges.on_penalty(0)
        user['badges_serialized'] = badges.serialize()
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_data_provided(1, 'reviewed_at:' + str(int(time.time())) + ';next_review:12:15 am,,12:16 am,,12:17 am')

        self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula" 💫',
                                              'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                             {'text': 'View achievements 🏆',
                                              'url': 'http://frontend?lang=en&env=prod&level=1&b1=f0_s0_c0a&bp1=c0_4_20--s0_3_0--f0_43200_0&ts=1650463200'}],
                                 'image': None,
                                 'menu_commands': MENU_COMMANDS,
                                 'message': 'The game is resumed.\n'
                                            '<i>Formula</i> has been reviewed 🎉\n'
                                            '\n'
                                            '🧹😾 Kicking out the grumpy cat...\n'
                                            '\n'
                                            'Next review before 12:15 am\n'
                                            '\n'
                                            ' ‣ /pause - pause the game\n'
                                            ' ‣ /sleep - configure sleep scheduler',
                                 'to_chat_id': 1}])

    @time_machine.travel("2022-04-21", tick=False)
    def test_on_data_reviewed_records_counter_histories_correctly_calculates_next_prompt_for_high_levels_without_prompts(self):
        user = self.users_orm.get_user_by_id(1)
        user['paused_counter_state'] = None
        user['difficulty']  = 3
        counter = Counter("")
        counter.resume()
        counter.move_time_back(25)
        user['active_game_counter_state'] = counter.serialize()
        user['review_counter_state'] = counter.serialize()
        user['lang_code'] = 'en'
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_data_provided(1, 'reviewed_at:' + str(int(time.time())) + ';next_review:12:15 am,,12:16 am,,12:17 am,,12:18 am,,12:19 am')

        self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula" 💫',
                                              'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                             {'text': 'View achievements 🏆',
                                              'url': 'http://frontend?lang=en&env=prod&level=1&b1=f0_s0_s1_c0&bp1=c0_0_100--s0_4_20--f0_108000_0&ts=1650463200'}],
                                 'image': None,
                                 'menu_commands': MENU_COMMANDS,
                                 'message': '<i>Formula</i> has been reviewed 🎉\n'
                                            '\n'
                                            'Next review before 12:18 am\n'
                                            '\n'
                                            ' ‣ /pause - pause the game\n'
                                            ' ‣ /sleep - configure sleep scheduler',
                                 'to_chat_id': 1}])
        user = self.users_orm.get_user_by_id(1)
        self.assertEqual(user['counters_history_serialized'], '[{"counter_name": "review", "counter_stopped_duration_secs": 1500, "event_datetime": {"_isoformat": "2022-04-20T14:00:00+00:00"}}]')
        self.assertEqual(user['next_prompt_type'], 'penalty')
        self.assertEqual(user['next_prompt_time'], datetime.datetime(2022, 4, 21, 1, 0).astimezone(datetime.timezone.utc))

    @time_machine.travel("2022-04-21", tick=False)
    def test_on_formula_reviewed_cooldown_rule(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(15)
        user['paused_counter_state'] = counter.serialize()
        user['difficulty']  = 2
        counter.move_time_back(10)
        user['active_game_counter_state'] = counter.serialize()
        user['review_counter_state'] = counter.serialize()
        user['lang_code'] = 'en'
        self.users_orm.upsert_user(user)

        self.game_manager.on_data_provided(1, 'reviewed_at:' + str(int(time.time())) + ';next_review:12:15 am,,12:16 am,,12:17 am')
        data = self.game_manager.on_data_provided(1, 'reviewed_at:' + str(int(time.time())) + ';next_review:12:15 am,,12:16 am,,12:17 am')

        self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula" 💫',
                                              'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'}],
                                 'image': None,
                                 'menu_commands': MENU_COMMANDS,
                                 'message': '<i>Formula</i> has been reviewed 🎉\n'
                                            '\n'
                                            '❄️ Early reviews are not rewarded.\n'
                                            '\n'
                                            'Next review before 12:17 am\n'
                                            '\n'
                                            ' ‣ /pause - pause the game\n'
                                            ' ‣ /sleep - configure sleep scheduler',
                                 'to_chat_id': 1}])

    def test_formula_command_renders_set_letter_button(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        user['shared_key_uuid'] = '84504531-c5bf-4cf4-9e88-5c1180870ee2'
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_formula_command(1)

        self.assertEqual(data, {'buttons': [{'text': 'Update your Formula 🧪',
                                             'url': 'http://frontend?env=prod&lang_code=en&formula=1&shared_key_uuid=84504531-c5bf-4cf4-9e88-5c1180870ee2'}],
                                'image': None,
                                'menu_commands': [],
                                'message': 'Update your <i>Formula</i> 🧪\n'
                                           '\n'
                                           'Use the button below to update your <i><a '
                                           'href="https://mindwarriorgame.org/faq.en.html#formula">Formula</a></i>.',
                                'to_chat_id': 1})


    @time_machine.travel("2022-04-21", tick=False)
    def test_data_command(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        user['shared_key_uuid'] = 'abc'
        self.users_orm.upsert_user(user)
        self.game_manager.on_data_provided(1, 'start_game;next_review:10:00,,11:00,,12:00')
        self.game_manager.on_pause_command(1)

        data = self.game_manager.on_data_command(1)
        self.assertIn('tmp_user_data', data[0]['image'])
        os.remove(data[0]['image'])
        data[0]['image'] = 'fname'
        self.assertEqual(data, [{'buttons': [{'text': 'View localStorage data 🔎',
                                              'url': 'http://frontend?env=prod&lang_code=en&view_localstorage=1'},
                                             {'text': 'DELETE ALL DATA ❌',
                                              'url': 'http://frontend?env=prod&lang_code=en&delete_data=1'}],
                                 'image': 'fname',
                                 'menu_commands': [['review', '💫️review Formula'],
                                                   ['pause', '⏸️ pause the game'],
                                                   ['sleep', '💤 sleep scheduler'],
                                                   ['formula', '️🧪update Formula'],
                                                   ['stats', '📊 game progress'],
                                                   ['difficulty', '💪change difficulty'],
                                                   ['data', '💾 view your raw data'],
                                                   ['feedback', '📢 send feedback']],
                                 'message': '<a href="https://mindwarriorgame.org/privacy-policy.en">We '
                                            'respect your privacy</a> and want to treat your data as '
                                            'transparent as possible. Below you can find all your data that '
                                            'the game stores on its server:\n'
                                            '\n'
                                            '<code> - shared_key_uuid: abc\n'
                                            '\n'
                                            ' - user_id: 1\n'
                                            '\n'
                                            ' - lang_code: en\n'
                                            '\n'
                                            ' - difficulty: 1\n'
                                            '\n'
                                            ' - review_counter_state: {"is_active": false, '
                                            '"total_seconds_intermediate": 0.0, "last_total_seconds_updated": '
                                            '{"_isoformat": "2022-04-20T14:00:00+00:00"}}\n'
                                            '\n'
                                            ' - next_prompt_time: 2022-04-20 16:45:00+00:00\n'
                                            '\n'
                                            ' - active_game_counter_state: {"is_active": false, '
                                            '"total_seconds_intermediate": 0.0, "last_total_seconds_updated": '
                                            '{"_isoformat": "2022-04-20T14:00:00+00:00"}}\n'
                                            '\n'
                                            ' - paused_counter_state: {"is_active": true, '
                                            '"total_seconds_intermediate": 0.0, "last_total_seconds_updated": '
                                            '{"_isoformat": "2022-04-20T14:00:00+00:00"}}\n'
                                            '\n'
                                            ' - counters_history_serialized: None\n'
                                            '\n'
                                            ' - next_prompt_type: reminder\n'
                                            '\n'
                                            ' - badges_serialized: {"badges_state": {"CatBadgeCounter": '
                                            '"cumulative_counter_secs=0,counter_last_updated=0,update_reason=game_started", '
                                            '"TimeBadgeCounter": "64800", "StarBadgeCounter": "0,3", '
                                            '"FeatherBadgeCounter": "64800"}, "board": [{"badge": "f0", '
                                            '"is_active": true, "is_la...\n'
                                            '\n'
                                            ' - next_autopause_event_time: None\n'
                                            '\n'
                                            ' - autopause_config_serialized: None</code>',
                                 'to_chat_id': 1}])

    @time_machine.travel("2023-04-20", tick=False)
    def test_expel_grumpy_cats(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        self.users_orm.upsert_user(user)
        self.game_manager.on_data_provided(1, 'start_game;next_review:10:00,,11:00,,12:00')
        user = self.users_orm.get_user_by_id(1)
        user['badges_serialized'] = ('{"board": ['
                                     '{"badge": "c0", "is_active": null}, '
                                     '{"badge": "c0", "is_active": null}, '
                                     '{"badge": "c1", "is_active": null}]}')
        achievement_urls = [
            'http://frontend?lang=en&env=prod&new_badge=c0&level=1&b1=c0am_c0_c1&bp1=c1_43200_0--c0_10_0&ts=1681912800',
            'http://frontend?lang=en&env=prod&new_badge=c0&level=1&b1=c0a_c0am_c1&bp1=c1_43200_0--c0_10_0&ts=1681912800'
        ]

        for penaltyIdx in range(0, 2):
            user['next_prompt_type'] = 'penalty'
            user['next_prompt_time'] = datetime.datetime(2022, 4, 19, 1, 0).astimezone(datetime.timezone.utc)
            self.users_orm.upsert_user(user)
            data = self.game_manager.process_tick()

            self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula" 💫',
                                                  'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                                 {'text': 'View achievements 🏆',
                                                  'url': achievement_urls[penaltyIdx]}],
                                     'image': None,
                                     'menu_commands': [],
                                     'message': 'You forgot to review your <i>Formula</i> 🟥\n'
                                                '\n'
                                                '😾 Oops! A grumpy cat sneaked in!\n'
                                                'Press "View achievements" button below.\n'
                                                '\n'
                                                ' ‣ /pause - pause the game\n'
                                                ' ‣ /sleep - configure sleep scheduler',
                                     'to_chat_id': 1}])
            user = self.users_orm.get_user_by_id(1)
            badge_manager = BadgesManager(user['difficulty'], user['badges_serialized'])
            self.assertEqual(badge_manager.count_active_grumpy_cats_on_board(), penaltyIdx + 1)


        achievement_urls = [
            'http://frontend?lang=en&env=prod&level=1&b1=c0a_c0a_c1&bp1=c1_43200_0--c0_9_10&ts=1681912800',
            'http://frontend?lang=en&env=prod&level=1&b1=c0a_c0a_c1&bp1=c1_43200_0--c0_6_40&ts=1681912800',
            'http://frontend?lang=en&env=prod&level=1&b1=c0a_c0a_c1&bp1=c1_43200_0--c0_3_70&ts=1681912800',
        ]
        for reviewIdx in range(0, 3):
            print(reviewIdx)
            user = self.users_orm.get_user_by_id(1)
            counter = Counter(user["review_counter_state"])
            counter.move_time_back(10)
            user['review_counter_state'] = counter.serialize()
            self.users_orm.upsert_user(user)
            data = self.game_manager.on_data_provided(1, 'reviewed_at:' + str(int(time.time())) + ';next_review:12:15 am,,12:16 am,,12:17 am')

            self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula" 💫',
                                                  'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                                 {'text': 'View achievements 🏆',
                                                  'url': achievement_urls[reviewIdx]}],
                                     'image': None,
                                     'menu_commands': MENU_COMMANDS,
                                     'message': '<i>Formula</i> has been reviewed 🎉\n'
                                                '\n'
                                                '🧹😾 Kicking out the grumpy cat...\n'
                                                '\n'
                                                'Next review before 12:16 am\n'
                                                '\n'
                                                ' ‣ /pause - pause the game\n'
                                                ' ‣ /sleep - configure sleep scheduler',
                                     'to_chat_id': 1}])

        user = self.users_orm.get_user_by_id(1)
        counter = Counter(user["review_counter_state"])
        counter.move_time_back(10)
        user['review_counter_state'] = counter.serialize()
        self.users_orm.upsert_user(user)
        data = self.game_manager.on_data_provided(1, 'reviewed_at:' + str(int(time.time())) + ';next_review:12:15 am,,12:16 am,,12:17 am')

        self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula" 💫',
                                              'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                             {'text': 'View achievements 🏆',
                                              'url': 'http://frontend?lang=en&env=prod&new_badge=c0_removed&level=1&b1=c0m_c0a_c1&bp1=c1_43200_0--c0_10_0&ts=1681912800'}],
                                 'image': None,
                                 'menu_commands': MENU_COMMANDS,
                                 'message': '<i>Formula</i> has been reviewed 🎉\n'
                                            '\n'
                                            '🧹 The grumpy cat has been kicked out!\n'
                                            '😾 Grumpy cats remaining: 1\n'
                                            '\n'
                                            'Next review before 12:16 am\n'
                                            '\n'
                                            ' ‣ /pause - pause the game\n'
                                            ' ‣ /sleep - configure sleep scheduler',
                                 'to_chat_id': 1}])

        achievement_urls = [
            'http://frontend?lang=en&env=prod&level=1&b1=c0_c0a_c1&bp1=c1_43200_0--c0_7_30&ts=1681912800',
            'http://frontend?lang=en&env=prod&level=1&b1=c0_c0a_c1&bp1=c1_43200_0--c0_4_60&ts=1681912800',
            'http://frontend?lang=en&env=prod&level=1&b1=c0_c0a_c1&bp1=c1_43200_0--c0_1_90&ts=1681912800',
        ]
        for reviewIdx in range(0, 3):
            print(reviewIdx)
            user = self.users_orm.get_user_by_id(1)
            counter = Counter(user["review_counter_state"])
            counter.move_time_back(10)
            user['review_counter_state'] = counter.serialize()
            self.users_orm.upsert_user(user)
            data = self.game_manager.on_data_provided(1, 'reviewed_at:' + str(int(time.time())) + ';next_review:12:15 am,,12:16 am,,12:17 am')

            self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula" 💫',
                                                  'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                                 {'text': 'View achievements 🏆',
                                                  'url': achievement_urls[reviewIdx]}],
                                     'image': None,
                                     'menu_commands': MENU_COMMANDS,
                                     'message': '<i>Formula</i> has been reviewed 🎉\n'
                                                '\n'
                                                '🧹😾 Kicking out the grumpy cat...\n'
                                                '\n'
                                                'Next review before 12:16 am\n'
                                                '\n'
                                                ' ‣ /pause - pause the game\n'
                                                ' ‣ /sleep - configure sleep scheduler',
                                     'to_chat_id': 1}])

        user = self.users_orm.get_user_by_id(1)
        counter = Counter(user["review_counter_state"])
        counter.move_time_back(10)
        user['review_counter_state'] = counter.serialize()
        self.users_orm.upsert_user(user)
        data = self.game_manager.on_data_provided(1, 'reviewed_at:' + str(int(time.time())) + ';next_review:12:15 am,,12:16 am,,12:17 am')

        self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula" 💫',
                                              'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'},
                                             {'text': 'View achievements 🏆',
                                              'url': 'http://frontend?lang=en&env=prod&new_badge=c0_removed&level=1&b1=c0_c0m_c1&bp1=c1_43200_0--c0_0_100&ts=1681912800'}],
                                 'image': None,
                                 'menu_commands': MENU_COMMANDS,
                                 'message': '<i>Formula</i> has been reviewed 🎉\n'
                                            '\n'
                                            '🧹 The grumpy cat has been kicked out!\n'
                                            '🏆 Achievements are unlocked!\n'
                                            '\n'
                                            'Next review before 12:16 am\n'
                                            '\n'
                                            ' ‣ /pause - pause the game\n'
                                            ' ‣ /sleep - configure sleep scheduler',
                                 'to_chat_id': 1}])


    def test_render_screens(self):
        for screenIdx in range(0, 20):
            self.game_manager.on_data_provided(1, 'render_screen_' + str(screenIdx))

    @time_machine.travel("2023-04-20", tick=False)
    def test_sleep_command_no_autosleep(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        self.users_orm.upsert_user(user)
        self.game_manager.on_data_provided(1, 'start_game;next_review:10:00,,11:00,,12:00')
        self.assertEqual(self.game_manager.on_sleep_command(1), {'buttons': [{'text': 'Configure sleep scheduler 💤',
                                                                              'url': 'http://frontend?env=prod&lang_code=en&sleep=1&enabled=false&bed_time=22:00&wakeup_time=06:00'}],
                                                                 'image': None,
                                                                 'menu_commands': [],
                                                                 'message': 'Configure sleep scheduler 💤\n'
                                                                            '\n'
                                                                            'Press the button below to set up your sleep time. The game will '
                                                                            'be automatically paused for this period, daily.\n'
                                                                            '\n'
                                                                            'Enabled? ⚪️\n'
                                                                            'Sleep time: N/A - N/A\n',
                                                                 'to_chat_id': 1})

    @time_machine.travel("2023-04-20", tick=False)
    def test_sleep_command_with_autosleep(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        autopause_manager = AutopauseManager(user['autopause_config_serialized'])
        autopause_manager.update(True, 'Asia/Tokyo', 12 * 3600, '22:30', '06:00')
        user['autopause_config_serialized'] = autopause_manager.serialize()
        self.users_orm.upsert_user(user)
        self.game_manager.on_data_provided(1, 'start_game;next_review:10:00,,11:00,,12:00')
        self.assertEqual(self.game_manager.on_sleep_command(1), {'buttons': [{'text': 'Configure sleep scheduler 💤',
                                                                              'url': 'http://frontend?env=prod&lang_code=en&sleep=1&enabled=true&bed_time=22:30&wakeup_time=06:00'}],
                                                                 'image': None,
                                                                 'menu_commands': [],
                                                                 'message': 'Configure sleep scheduler 💤\n'
                                                                            '\n'
                                                                            'Press the button below to set up your sleep time. The game will '
                                                                            'be automatically paused for this period, daily.\n'
                                                                            '\n'
                                                                            'Enabled? 🟢\n'
                                                                            'Sleep time: 22:30 - 06:00\n',
                                                                 'to_chat_id': 1})

    @time_machine.travel("2023-04-20 22:00", tick=False)
    def test_autosleep_round_robin(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        self.users_orm.upsert_user(user)
        self.game_manager.on_data_provided(1, 'start_game;next_review:10:00,,11:00,,12:00')
        data = self.game_manager.on_data_provided(1, 'sleep_config:True,,Australia/Sydney,,12345,,22:30,,06:00')
        self.assertEqual(data, [{'buttons': [],
                                 'image': None,
                                 'menu_commands': [],
                                 'message': 'Sleep scheduler has been updated 💤\n'
                                            '\n'
                                            'Enabled? 🟢\n'
                                            'Sleep time: 22:30 - 06:00\n',
                                 'to_chat_id': 1}])

        data = self.game_manager.process_tick()
        self.assertEqual(data, [])

        with time_machine.travel("2023-04-20 22:31", tick=False):
            data = self.game_manager.process_tick()
            self.assertEqual(data, [{'buttons': [],
                                     'image': None,
                                     'menu_commands': [],
                                     'message': 'Time to sleep 💤\n'
                                                '\n'
                                                'The game is automatically paused until 06:00. Sweet dreams! 🌙\n'
                                                '\n'
                                                ' ‣ /sleep - configure sleep scheduler',
                                     'to_chat_id': 1}])
            user = self.users_orm.get_user_by_id(1)
            self.assertIsNotNone(user['paused_counter_state'])

        with time_machine.travel("2023-04-21 05:59", tick=False):
            data = self.game_manager.process_tick()
            self.assertEqual(data, [])

        with time_machine.travel("2023-04-21 06:01", tick=False):
            data = self.game_manager.process_tick()
            self.assertEqual(data, [{'buttons': [],
                                     'image': None,
                                     'menu_commands': [],
                                     'message': 'Good morning! ☀️\n'
                                                '\n'
                                                'The game is resumed. Have a great day! 🌞\n'
                                                '\n'
                                                ' ‣ /sleep - configure sleep scheduler',
                                     'to_chat_id': 1}])
            user = self.users_orm.get_user_by_id(1)
            self.assertIsNone(user['paused_counter_state'])

        with time_machine.travel("2023-04-21 08:01", tick=False):
            user = self.users_orm.get_user_by_id(1)
            self.assertIsNone(user['paused_counter_state'])

            self.game_manager.on_data_provided(1, 'reviewed_at:' + str(int(time.time())) + ';next_review:12:15 am,,12:16 am,,12:17 am')

            data = self.game_manager.process_tick()
            self.assertEqual(data, [])

        with time_machine.travel("2023-04-21 22:00", tick=False):
            user = self.users_orm.get_user_by_id(1)
            self.assertIsNone(user['paused_counter_state'])

            self.game_manager.on_data_provided(1, 'reviewed_at:' + str(int(time.time())) + ';next_review:12:15 am,,12:16 am,,12:17 am')

            data = self.game_manager.process_tick()
            self.assertEqual(data, [])

        with time_machine.travel("2023-04-21 22:31", tick=False):
            user = self.users_orm.get_user_by_id(1)
            self.assertIsNone(user['paused_counter_state'])

            data = self.game_manager.process_tick()
            self.assertEqual(data, [{'buttons': [],
                                      'image': None,
                                      'menu_commands': [],
                                      'message': 'Time to sleep 💤\n'
                                                 '\n'
                                                 'The game is automatically paused until 06:00. Sweet dreams! 🌙\n'
                                                 '\n'
                                                 ' ‣ /sleep - configure sleep scheduler',
                                      'to_chat_id': 1}])

    @time_machine.travel("2023-04-20 22:00", tick=False)
    def test_autosleep_disable(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        self.users_orm.upsert_user(user)
        self.game_manager.on_data_provided(1, 'start_game;next_review:10:00,,11:00,,12:00')

        self.game_manager.on_data_provided(1, 'sleep_config:True,,Australia/Sydney,,12345,,22:30,,06:00')
        user = self.users_orm.get_user_by_id(1)
        self.assertEqual(user['next_autopause_event_time'], datetime.datetime(2023, 4, 20, 22, 30, 1).astimezone(datetime.timezone.utc))

        data = self.game_manager.on_data_provided(1, 'sleep_config:False,,Australia/Sydney,,12345,,20:30,,05:00')
        user = self.users_orm.get_user_by_id(1)
        self.assertEqual(user['next_autopause_event_time'], None)

        self.assertEqual(data, [{'buttons': [],
                                 'image': None,
                                 'menu_commands': [],
                                 'message': 'Sleep scheduler has been updated 💤\n'
                                            '\n'
                                            'Enabled? ⚪️\n'
                                            'Sleep time: N/A - N/A\n',
                                 'to_chat_id': 1}])
