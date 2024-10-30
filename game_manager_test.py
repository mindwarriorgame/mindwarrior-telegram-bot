import datetime
import os
import unittest

import time_machine
import time

from counter import Counter
from game_manager import GameManager
from users_orm import UsersOrm


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

        self.assertEqual(data, [{'buttons': [],
                                 'image': './badge-images/f0.jpg',
                                 'menu_commands': [],
                                 'message': "You've got a new achievement! 🌟",
                                 'to_chat_id': 1},
                                {'buttons': [{'text': 'Review your "Formula"',
                                              'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'}],
                                 'image': None,
                                 'menu_commands': [],
                                 'message': 'The game has started 🏁\n'
                                            '\n'
                                            '💪<a '
                                            'href="https://mindwarriorgame.org/faq.en.html#difficulty">Difficulty '
                                            'level</a>: Easy\n'
                                            '\n'
                                            'Review your <i>Formula</i> before 11:00\n'
                                            '\n'
                                            '/difficulty - change the difficulty\n'
                                            '/pause - pause the gameㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ',
                                 'to_chat_id': 1}])

        user = self.users_orm.get_user_by_id(1)

        self.assertIsNone(user['paused_counter_state'])

        self.assertIsNotNone(user['active_game_counter_state'])
        counter = Counter(user['active_game_counter_state'])
        self.assertTrue(counter.is_active())

        self.assertEqual(user['difficulty'], 1)
        self.assertEqual(user['rewards'], 0)
        self.assertEqual(user['last_reward_time'], None)
        self.assertEqual(user['next_prompt_time'], datetime.datetime(2022, 4, 21, 2, 45).astimezone(datetime.timezone.utc))
        self.assertEqual(user['next_prompt_type'], 'reminder')

        self.assertIsNotNone(user['review_counter_state'])
        counter = Counter(user['review_counter_state'])
        self.assertTrue(counter.is_active())

        self.assertEqual(counter.get_total_seconds(), 0)



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
            self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula"',
                                                  'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'}],
                                     'image': None,
                                     'menu_commands': [],
                                     'message': "Don't forget to review your <i>Formula</i>! ⏰\n"
                                                '\n'
                                                'The due time is in 15 minutes, hurry up!',
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
    def test_process_tick_forgot_to_review(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        user['difficulty'] = 0
        self.users_orm.upsert_user(user)
        self.game_manager.on_data_provided(1, "start_game;next_review:10:00,,11:00,,12:00,,13:00,,14:00")
        user = self.users_orm.get_user_by_id(1)
        with time_machine.travel("2022-04-21 05:50", tick=False):
            self.game_manager.process_tick()
            with time_machine.travel("2022-04-21 06:10", tick=False):
                data = self.game_manager.process_tick()
                self.assertEqual(data, [{'buttons': [],
                                         'image': './badge-images/c0.jpg',
                                         'menu_commands': [],
                                         'message': '',
                                         'to_chat_id': 1},
                                        {'buttons': [{'text': 'Review your "Formula"',
                                                      'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'}],
                                         'image': None,
                                         'menu_commands': [],
                                         'message': 'You forgot to review your <i>Formula</i> 🟥ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ '
                                                    'ㅤ ㅤ ㅤ ㅤ ',
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
        user['rewards'] = 5
        user['last_reward_time'] = datetime.datetime(2022, 4, 20)
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
                                'menu_commands': [],
                                'message': 'Review your <i> Formula</i> 💫\n'
                                           '\n'
                                           'Press any button below to review your <i>Formula</i>.',
                                'to_chat_id': 1})

    @time_machine.travel("2022-04-21", tick=False)
    def test_on_review_next_time(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(65)
        user['review_counter_state'] = counter.serialize()
        user['difficulty']  = 4
        user['rewards'] = 5
        user['last_reward_time'] = datetime.datetime(2022, 4, 20)
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
                                'menu_commands': [],
                                'message': 'Time since the last review: 0d 1h 5m\n'
                                           'Review your <i> Formula</i> 💫\n'
                                           '\n'
                                           'Press any button below to review your <i>Formula</i>.',
                                'to_chat_id': 1})

    @time_machine.travel("2022-04-21", tick=False)
    def test_on_start_game_reset_existing_game(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(1)
        user['paused_counter_state'] = counter.serialize()
        user['difficulty']  = 4
        user['rewards'] = 5
        user['last_reward_time'] = datetime.datetime(2022, 4, 20).astimezone(datetime.timezone.utc)
        user['lang_code'] = 'en'
        user['review_counter_state'] = counter.serialize()
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_data_provided(1, 'start_game;next_review:10:00,,11:00,,12:00,,13:00,,14:00')

        self.assertEqual(data, [{'buttons': [],
                                 'image': './badge-images/f0.jpg',
                                 'menu_commands': [],
                                 'message': "You've got a new achievement! 🌟",
                                 'to_chat_id': 1},
                                {'buttons': [{'text': 'Review your "Formula"',
                                              'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'}],
                                 'image': None,
                                 'menu_commands': [],
                                 'message': 'The game has started 🏁\n'
                                            '\n'
                                            '💪<a '
                                            'href="https://mindwarriorgame.org/faq.en.html#difficulty">Difficulty '
                                            'level</a>: Expert\n'
                                            '\n'
                                            'Review your <i>Formula</i> before 14:00\n'
                                            '\n'
                                            '/difficulty - change the difficulty\n'
                                            '/pause - pause the gameㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ',
                                 'to_chat_id': 1}])

        user = self.users_orm.get_user_by_id(1)
        self.assertIsNone(user['paused_counter_state'])
        self.assertIsNotNone(user['active_game_counter_state'])
        counter = Counter(user['active_game_counter_state'])
        self.assertTrue(counter.is_active())
        self.assertLess(abs(counter.get_total_seconds()), 0.001)
        self.assertEqual(user['difficulty'], 4)
        self.assertEqual(user['rewards'], 0)
        self.assertEqual(user['last_reward_time'], None)
        self.assertEqual(user['next_prompt_time'], datetime.datetime(2022, 4, 21, 0, 45).astimezone(datetime.timezone.utc))
        counter = Counter(user['review_counter_state'])
        self.assertEqual(counter.is_active(), True)
        self.assertEqual(counter.get_total_seconds(), 0)



    @time_machine.travel("2022-04-22")
    def test_set_difficulty_renders_start_button(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_data_provided(1, 'set_difficulty:1')[0]

        self.assertEqual(data['to_chat_id'], 1)
        self.assertEqual(data['message'].index('stranger') >= 0, True)
        self.assertEqual(data['buttons'], [
            {'text': 'Write "Formula" and start playing!',
             'url': 'http://frontend?env=prod&lang_code=en&new_game=1&next_review_prompt_minutes=360,180,90,60,45'}
        ])

    @time_machine.travel("2022-04-22", tick=False)
    def test_set_difficulty_updates_difficulty_resets_scores_for_high_levels(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(15)
        user['paused_counter_state'] = counter.serialize()
        user['difficulty']  = 2
        user['rewards'] = 5
        user['active_game_counter_state'] = counter.serialize()
        user['last_reward_time'] = datetime.datetime(2022, 4, 21)
        user['lang_code'] = 'en'
        user['review_counter_state'] = counter.serialize()
        user['badges_serialized'] = 'asd'
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_data_provided(1, 'set_difficulty:3;next_review:05:29,,02:29,,00:59,,00:29,,00:14')[0]

        self.assertEqual(data, {'buttons': [{'text': 'Review your "Formula"',
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
                                           '🌟 Total stars: 0\n'
                                           '⏳ Play time: 0d 0h 0m\n'
                                           '\n'
                                           'Next review before 00:29\n',
                                'to_chat_id': 1})
        user = self.users_orm.get_user_by_id(1)
        self.assertEqual(user['difficulty'], 3)
        self.assertEqual(user['rewards'], 0)
        self.assertIsNone(user['paused_counter_state'])
        self.assertEqual(user['last_reward_time'], None)
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
        user['rewards'] = 5
        user['active_game_counter_state'] = counter.serialize()
        user['last_reward_time'] = datetime.datetime(2022, 4, 21)
        user['lang_code'] = 'en'
        user['review_counter_state'] = counter.serialize()
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_data_provided(1, 'set_difficulty:1;next_review:05:29,,02:29,,00:59,,00:29,,00:14')[0]

        self.assertEqual(data, {'buttons': [{'text': 'Review your "Formula"',
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
                                           '🌟 Total stars: 0\n'
                                           '⏳ Play time: 0d 0h 0m\n'
                                           '\n'
                                           'Next review before 02:29\n',
                                'to_chat_id': 1})
        user = self.users_orm.get_user_by_id(1)
        self.assertEqual(user['difficulty'], 1)
        self.assertEqual(user['rewards'], 0)
        self.assertIsNone(user['paused_counter_state'])
        self.assertEqual(user['last_reward_time'], None)
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
        user['rewards'] = 5
        user['active_game_counter_state'] = counter.serialize()
        user['last_reward_time'] = datetime.datetime(2022, 4, 21)
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
        user['rewards'] = 5
        user['active_game_counter_state'] = counter.serialize()
        user['last_reward_time'] = datetime.datetime(2022, 4, 21)
        user['next_prompt_time'] = datetime.datetime(2022, 4, 22, 1, 45).astimezone(datetime.timezone.utc)
        user['lang_code'] = 'en'
        user['review_counter_state'] = counter.serialize()
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_stats_command(1)
        self.assertEqual(data, {'buttons': [],
                                'image': None,
                                'menu_commands': [],
                                'message': '🌟 <a href="https://mindwarriorgame.org/faq.en.html#review">Earned '
                                           'stars</a>: 5\n'
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
        self.assertEqual(data['buttons'], [{'text': 'Write "Formula" and start playing!',
                                            'url': 'http://frontend?env=prod&lang_code=en&new_game=1&next_review_prompt_minutes=360,180,90,60,45'}])

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

        self.assertEqual(data, {'buttons': [{'text': 'Review your "Formula"',
                                             'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'}],
                                'image': None,
                                'menu_commands': [],
                                'message': 'The game is paused ⏸️\n'
                                           '\n'
                                           'You will not be receiving reminders about your <i>Formula</i>, '
                                           'and the active play time counter <a href=\"https://mindwarriorgame.org/faq.en#pause\">are frozen</a>.\n'
                                           '\n'
                                           'To resume the game, simply review your <i>Formula</i> using the '
                                           'button below.',
                                'to_chat_id': 1})

    @time_machine.travel("2022-04-21", tick=False)
    def test_on_data_reviewed_records_counter_histories_and_adds_one_star(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(15)
        user['paused_counter_state'] = counter.serialize()
        user['difficulty']  = 2
        user['rewards'] = 5
        counter.move_time_back(10)
        user['active_game_counter_state'] = counter.serialize()
        user['review_counter_state'] = counter.serialize()
        user['last_reward_time'] = datetime.datetime(2022, 4, 20)
        user['lang_code'] = 'en'
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_data_provided(1, 'reviewed_at:' + str(int(time.time())) + ';next_review:12:15 am,,12:16 am,,12:17 am')

        self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula"',
                                              'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'}],
                                 'image': None,
                                 'menu_commands': [],
                                 'message': 'The game is resumed.\n'
                                            '<i>Formula</i> has been reviewed 🎉\n'
                                            '\n'
                                            "<b>😺 You've got a new star!</b>\n"
                                            '\n'
                                            '🌟 Total stars: 6\n'
                                            '⏳ Play time: 0d 0h 25m\n'
                                            '\n'
                                            'Next review before 12:17 am\n'
                                            '\n'
                                            '/pause - pause the game',
                                 'to_chat_id': 1}])
        user = self.users_orm.get_user_by_id(1)
        self.assertEqual(user['counters_history_serialized'], '['
            '{"counter_name": "paused", "counter_stopped_duration_secs": 900, "event_datetime": {"_isoformat": "2022-04-20T14:00:00+00:00"}}, '
            '{"counter_name": "review", "counter_stopped_duration_secs": 1500, "event_datetime": {"_isoformat": "2022-04-20T14:00:00+00:00"}}]')
        self.assertEqual(user['rewards'], 6)
        self.assertEqual(user['last_reward_time'], datetime.datetime(2022, 4, 21).astimezone(datetime.timezone.utc))
        self.assertEqual(user['next_prompt_type'], 'reminder')
        self.assertEqual(user['next_prompt_time'], datetime.datetime(2022, 4, 21, 1, 15).astimezone(datetime.timezone.utc))

    @time_machine.travel("2022-04-21", tick=False)
    def test_on_data_reviewed_records_counter_histories_and_adds_two_stars(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(15)
        user['paused_counter_state'] = counter.serialize()
        user['difficulty']  = 0
        user['rewards'] = 5
        counter.move_time_back(10)
        user['active_game_counter_state'] = counter.serialize()
        user['review_counter_state'] = counter.serialize()
        user['last_reward_time'] = datetime.datetime(2022, 4, 20)
        user['lang_code'] = 'en'
        user['next_prompt_type'] = 'reminder'
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_data_provided(1, 'reviewed_at:' + str(int(time.time())) + ';next_review:12:15 am,,12:16 am,,12:17 am')

        self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula"',
                                              'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'}],
                                 'image': None,
                                 'menu_commands': [],
                                 'message': 'The game is resumed.\n'
                                            '<i>Formula</i> has been reviewed 🎉\n'
                                            '\n'
                                            "<b>😻 You've got 2 new stars!</b>\n"
                                            '\n'
                                            '🌟 Total stars: 7\n'
                                            '⏳ Play time: 0d 0h 25m\n'
                                            '\n'
                                            'Next review before 12:15 am\n'
                                            '\n'
                                            '/pause - pause the game',
                                 'to_chat_id': 1}])

    @time_machine.travel("2022-04-21", tick=False)
    def test_on_data_reviewed_records_counter_histories_correctly_calculates_next_prompt_for_high_levels_without_prompts(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(15)
        user['paused_counter_state'] = counter.serialize()
        user['difficulty']  = 3
        user['rewards'] = 5
        counter.move_time_back(10)
        user['active_game_counter_state'] = counter.serialize()
        user['review_counter_state'] = counter.serialize()
        user['last_reward_time'] = datetime.datetime(2022, 4, 20)
        user['lang_code'] = 'en'
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_data_provided(1, 'reviewed_at:' + str(int(time.time())) + ';next_review:12:15 am,,12:16 am,,12:17 am,,12:18 am,,12:19 am')

        self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula"',
                                              'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'}],
                                 'image': None,
                                 'menu_commands': [],
                                 'message': 'The game is resumed.\n'
                                            '<i>Formula</i> has been reviewed 🎉\n'
                                            '\n'
                                            "<b>😺 You've got a new star!</b>\n"
                                            '\n'
                                            '🌟 Total stars: 6\n'
                                            '⏳ Play time: 0d 0h 25m\n'
                                            '\n'
                                            'Next review before 12:18 am\n'
                                            '\n'
                                            '/pause - pause the game',
                                 'to_chat_id': 1}])
        user = self.users_orm.get_user_by_id(1)
        self.assertEqual(user['counters_history_serialized'], '['
                                                              '{"counter_name": "paused", "counter_stopped_duration_secs": 900, "event_datetime": {"_isoformat": "2022-04-20T14:00:00+00:00"}}, '
                                                              '{"counter_name": "review", "counter_stopped_duration_secs": 1500, "event_datetime": {"_isoformat": "2022-04-20T14:00:00+00:00"}}]')
        self.assertEqual(user['rewards'], 6)
        self.assertEqual(user['next_prompt_type'], 'penalty')
        self.assertEqual(user['next_prompt_time'], datetime.datetime(2022, 4, 21, 1, 0).astimezone(datetime.timezone.utc))

    @time_machine.travel("2022-04-21", tick=False)
    def test_on_data_reviewed_cooldown_rule(self):
        user = self.users_orm.get_user_by_id(1)
        counter = Counter("")
        counter.resume()
        counter.move_time_back(15)
        user['paused_counter_state'] = counter.serialize()
        user['difficulty']  = 2
        user['rewards'] = 5
        counter.move_time_back(10)
        user['active_game_counter_state'] = counter.serialize()
        user['review_counter_state'] = counter.serialize()
        user['last_reward_time'] = datetime.datetime(2022, 4, 20)
        user['lang_code'] = 'en'
        self.users_orm.upsert_user(user)

        self.game_manager.on_data_provided(1, 'reviewed_at:' + str(int(time.time())) + ';next_review:12:15 am,,12:16 am,,12:17 am')
        data = self.game_manager.on_data_provided(1, 'reviewed_at:' + str(int(time.time())) + ';next_review:12:15 am,,12:16 am,,12:17 am')

        self.assertEqual(data, [{'buttons': [{'text': 'Review your "Formula"',
                                              'url': 'http://frontend?env=prod&lang_code=en&review=1&next_review_prompt_minutes=360,180,90,60,45'}],
                                 'image': None,
                                 'menu_commands': [],
                                 'message': '<i>Formula</i> has been reviewed 🎉\n'
                                            '\n'
                                            'No reward (<a '
                                            'href="https://mindwarriorgame.org/faq.en.html#difficulty:~:text=will%20be%20rewarded%20(-,%22cool%2Ddown%22%20rule,-).">cool-down '
                                            'rule</a>)\n'
                                            '\n'
                                            '🌟 Total stars: 6\n'
                                            '⏳ Play time: 0d 0h 25m\n'
                                            '\n'
                                            'Next review before 12:17 am\n'
                                            '\n'
                                            '/pause - pause the game',
                                 'to_chat_id': 1}])

    def test_formula_command_renders_set_letter_button(self):
        user = self.users_orm.get_user_by_id(1)
        user['lang_code'] = 'en'
        user['shared_key_uuid'] = '84504531-c5bf-4cf4-9e88-5c1180870ee2'
        self.users_orm.upsert_user(user)

        data = self.game_manager.on_formula_command(1)

        self.assertEqual(data, {'buttons': [{'text': 'Update your Formula',
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
        self.users_orm.upsert_user(user)
        self.game_manager.on_data_provided(1, 'start_game;next_review:10:00,,11:00,,12:00')
        self.game_manager.on_pause_command(1)

        data = self.game_manager.on_data_command(1)
        user = self.users_orm.get_user_by_id(1)
        self.assertEqual(data, {'buttons': [{'text': 'View localStorage data',
                                             'url': 'http://frontend?env=prod&lang_code=en&view_localstorage=1'},
                                            {'text': 'DELETE ALL DATA',
                                             'url': 'http://frontend?env=prod&lang_code=en&delete_data=1'}],
                                'image': None,
                                'menu_commands': [],
                                'message': 'Your raw data:\n'
                                           '\n'
                                           f" - shared_key_uuid: {user['shared_key_uuid']}\n"
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
                                           ' - last_reward_time: None\n'
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
                                           ' - rewards: 0\n'
                                           '\n'
                                           ' - counters_history_serialized: None\n'
                                           '\n'
                                           ' - next_prompt_type: reminder\n'
                                           '\n'
                                           f" - badges_serialized: {user['badges_serialized']}",
                                'to_chat_id': 1})