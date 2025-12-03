import datetime
import os
import unittest

import time_machine

from users_orm import UsersOrm, User

class TestUsersOrm(unittest.IsolatedAsyncioTestCase):

    users_orm: UsersOrm

    def setUp(self):
        try:
            os.unlink('test.db')
        except FileNotFoundError:
            pass
        self.users_orm = UsersOrm('test.db')
        self.maxDiff = None

    def tearDown(self):
        self.users_orm.__del__()
        try:
            os.unlink('test.db')
        except FileNotFoundError:
            pass

    def test_get_user_returns_empty_user(self):
        user = self.users_orm.get_user_by_id(123)
        self.assertGreaterEqual(len(user['shared_key_uuid']), 10)
        user['shared_key_uuid'] = 'abcd'
        self.assertEqual(user, User(
            user_id=123,
            lang_code=None,
            difficulty=1,
            review_counter_state=None,
            next_prompt_time=None,
            active_game_counter_state=None,
            paused_counter_state=None,
            counters_history_serialized=None,
            shared_key_uuid='abcd',
            next_prompt_type='',
            badges_serialized='',
            next_autopause_event_time=None,
            autopause_config_serialized=None,
            diamonds=0,
            spent_diamonds=0,
            frontend_base_url_override=None
        ))

    @time_machine.travel("2022-04-21")
    def test_upsert_user(self):
        user = self.users_orm.get_user_by_id(123)
        user['lang_code'] = 'ru'
        self.users_orm.upsert_user(user)
        user = self.users_orm.get_user_by_id(123)
        self.assertGreaterEqual(len(user['shared_key_uuid']), 10)
        user['shared_key_uuid'] = 'abcd'
        user['next_prompt_type'] = 'qwe'
        user['diamonds'] = 5
        user['spent_diamonds'] = 6
        user['frontend_base_url_override'] = 'over'
        self.assertEqual(user, User(
            user_id=123,
            lang_code='ru',
            difficulty=1,
            review_counter_state=None,
            next_prompt_time=None,
            active_game_counter_state=None,
            paused_counter_state=None,
            counters_history_serialized=None,
            shared_key_uuid='abcd',
            next_prompt_type='qwe',
            badges_serialized='',
            next_autopause_event_time=None,
            autopause_config_serialized=None,
            diamonds=5,
            spent_diamonds=6,
            frontend_base_url_override='over'
        ))

        user['lang_code'] = 'en'
        user['difficulty'] = 2
        user['review_counter_state'] = 'my_review_counter_state'
        user['next_prompt_time'] = datetime.datetime(2022, 4, 21, 2, 0, 0)
        user['active_game_counter_state'] = 'my_active_game_counter_state'
        user['paused_counter_state'] = 'my_paused_counter_state'
        user['counters_history_serialized'] = 'my_counters_history_serialized'
        user['shared_key_uuid'] = 'dbca'
        user['next_prompt_type'] = 'ewq'
        user['badges_serialized'] = 'badges_serialized'
        user['next_autopause_event_time'] = datetime.datetime(2022, 4, 21, 2, 0, 0)
        user['autopause_config_serialized'] = 'blah'
        user['diamonds'] = 6
        user['spent_diamonds'] = 7
        user['frontend_base_url_override'] = 'newover'
        self.users_orm.upsert_user(user)

        self.assertEqual(self.users_orm.get_user_by_id(123), User(
            user_id=123,
            lang_code='en',
            difficulty=2,
            review_counter_state='my_review_counter_state',
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0).astimezone(datetime.timezone.utc),
            active_game_counter_state='my_active_game_counter_state',
            paused_counter_state='my_paused_counter_state',
            counters_history_serialized='my_counters_history_serialized',
            shared_key_uuid='dbca',
            next_prompt_type='ewq',
            badges_serialized='badges_serialized',
            next_autopause_event_time=datetime.datetime(2022, 4, 21, 2, 0, 0).astimezone(datetime.timezone.utc),
            autopause_config_serialized='blah',
            diamonds=6,
            spent_diamonds=7,
            frontend_base_url_override='newover'
        ))

    def test_get_some_users_for_prompt_when_no_user(self):
        self.assertEqual(self.users_orm.get_some_users_for_prompt(10, 1), [])

    @time_machine.travel("2023-04-21 05:00:00")
    def test_get_users_for_prompt_fetches_eligible_users(self):
        user = User(
            user_id=124,
            lang_code='ru',
            difficulty=1,
            review_counter_state='my_review_counter_state',
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0).astimezone(datetime.timezone.utc),
            active_game_counter_state='my_active_game_counter_state',
            paused_counter_state=None,
            counters_history_serialized='my_counters_history_serialized',
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized',
            next_autopause_event_time=datetime.datetime(2022, 4, 21, 2, 0, 0).astimezone(datetime.timezone.utc),
            autopause_config_serialized='blah',
            diamonds=7,
            spent_diamonds=8,
            frontend_base_url_override='over'
        )
        self.users_orm.upsert_user(user)
        self.assertEqual(self.users_orm.get_some_users_for_prompt(10, 1), [user])

    @time_machine.travel("2023-04-21 05:00:00")
    def test_get_next_autopause_events_fetch_eligible_users(self):
        user = User(
            user_id=124,
            lang_code='ru',
            difficulty=1,
            review_counter_state='my_review_counter_state',
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0).astimezone(datetime.timezone.utc),
            active_game_counter_state='my_active_game_counter_state',
            paused_counter_state=None,
            counters_history_serialized='my_counters_history_serialized',
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized',
            next_autopause_event_time=datetime.datetime(2022, 4, 21, 2, 0, 0).astimezone(datetime.timezone.utc),
            autopause_config_serialized='blah',
            diamonds=8,
            spent_diamonds=9,
            frontend_base_url_override='over'
        )
        self.users_orm.upsert_user(user)
        self.assertEqual(self.users_orm.get_some_next_autopause_events(10), [user])
        user['next_autopause_event_time'] = datetime.datetime(2023, 4, 23, 2, 0, 0).astimezone(datetime.timezone.utc)
        self.users_orm.upsert_user(user)
        self.assertEqual(self.users_orm.get_some_next_autopause_events(10), [])

    @time_machine.travel("2023-04-21 05:00:00")
    def test_get_users_for_prompt_not_fetches_not_started_users(self):
        user = User(
            user_id=124,
            lang_code='ru',
            difficulty=1,
            review_counter_state='my_review_counter_state',
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            active_game_counter_state=None,
            paused_counter_state=None,
            counters_history_serialized='counters_history_serialized',
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized',
            next_autopause_event_time=None,
            autopause_config_serialized=None,
            diamonds=9,
            spent_diamonds=8,
            frontend_base_url_override='over'
        )
        self.users_orm.upsert_user(user)
        self.assertEqual(self.users_orm.get_some_users_for_prompt(10, 1), [])

    @time_machine.travel("2023-04-21 05:00:00")
    def test_get_users_for_prompt_not_fetches_users_with_different_difficulty(self):
        user = User(
            user_id=124,
            lang_code='ru',
            difficulty=1,
            review_counter_state='my_review_counter_state',
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            active_game_counter_state='my_active_game_counter_state',
            paused_counter_state=None,
            counters_history_serialized='my_counters_history_serialized',
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized',
            next_autopause_event_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            autopause_config_serialized='blah',
            diamonds=10,
            spent_diamonds=8,
            frontend_base_url_override='over'
        )
        self.users_orm.upsert_user(user)
        self.assertEqual(self.users_orm.get_some_users_for_prompt(10, 2), [])


    @time_machine.travel("2023-04-21 05:00:00")
    def test_get_users_for_prompt_not_fetches_recently_prompted_users(self):
        user = User(
            user_id=124,
            lang_code='ru',
            difficulty=1,
            review_counter_state='my_review_counter_state',
            next_prompt_time=datetime.datetime(2023, 4, 21, 5, 59, 0),
            active_game_counter_state='my_active_game_counter_state',
            paused_counter_state=None,
            counters_history_serialized=None,
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized',
            next_autopause_event_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            autopause_config_serialized='blah',
            diamonds=11,
            spent_diamonds=7,
            frontend_base_url_override=None
        )
        self.users_orm.upsert_user(user)
        self.assertEqual(self.users_orm.get_some_users_for_prompt(10, 1), [])


    @time_machine.travel("2023-04-21 05:00:00")
    def test_get_users_for_prompt_not_fetches_paused_users(self):
        user = User(
            user_id=124,
            lang_code='ru',
            difficulty=1,
            review_counter_state='my_review_counter_state',
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            active_game_counter_state='my_active_game_counter_state',
            paused_counter_state='my_paused_counter_state',
            counters_history_serialized=None,
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized',
            next_autopause_event_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            autopause_config_serialized='blah',
            diamonds=12,
            spent_diamonds=10,
            frontend_base_url_override='over'
        )
        self.users_orm.upsert_user(user)
        self.assertEqual(self.users_orm.get_some_users_for_prompt(10, 1), [])

    def test_delete_user(self):
        user = User(
            user_id=124,
            lang_code='ru',
            difficulty=3,
            review_counter_state='my_review_counter_state',
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            active_game_counter_state='my_active_game_counter_state',
            paused_counter_state='my_paused_counter_state',
            counters_history_serialized=None,
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized',
            next_autopause_event_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            autopause_config_serialized='blah',
            diamonds=13,
            spent_diamonds=11,
            frontend_base_url_override='over'
        )
        self.users_orm.upsert_user(user)
        self.users_orm.remove_user(124)
        user = self.users_orm.get_user_by_id(124)
        self.assertGreater(len(user['shared_key_uuid']), 10)
        user['shared_key_uuid'] = 'abcd'
        self.assertEqual(user, User(
            user_id=124,
            lang_code=None,
            difficulty=1,
            review_counter_state=None,
            next_prompt_time=None,
            active_game_counter_state=None,
            paused_counter_state=None,
            counters_history_serialized=None,
            shared_key_uuid='abcd',
            next_prompt_type='',
            badges_serialized='',
            next_autopause_event_time=None,
            autopause_config_serialized=None,
            diamonds=0,
            spent_diamonds=0,
            frontend_base_url_override=None
        ))

    @time_machine.travel("2022-04-21 00:00:00")
    def test_counters(self):
        user = User(
            user_id=124,
            lang_code='ru',
            difficulty=1,
            review_counter_state='my_review_counter_state',
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            active_game_counter_state='my_active_game_counter_state',
            paused_counter_state=None,
            counters_history_serialized=None,
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized',
            next_autopause_event_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            autopause_config_serialized='blah',
            diamonds=44,
            spent_diamonds=1,
            frontend_base_url_override='over'
        )
        self.users_orm.upsert_user(user)
        self.assertEqual(self.users_orm.count_active_users(1), 1)
        self.assertEqual(self.users_orm.count_paused_users(1), 0)
        self.assertEqual(self.users_orm.count_inactive_users(1), 0)
        self.assertEqual(self.users_orm.count_recently_rewarded_users(1), 0)

    def test_count_paused_users(self):
        user = User(
            user_id=124,
            lang_code='ru',
            difficulty=1,
            review_counter_state='my_review_counter_state',
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            active_game_counter_state='my_active_game_counter_state',
            paused_counter_state='paused',
            counters_history_serialized=None,
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized',
            next_autopause_event_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            autopause_config_serialized='blah',
            diamonds=55,
            spent_diamonds=2,
            frontend_base_url_override=None
        )
        self.users_orm.upsert_user(user)
        self.assertEqual(self.users_orm.count_active_users(1), 0)
        self.assertEqual(self.users_orm.count_paused_users(1), 1)
        self.assertEqual(self.users_orm.count_inactive_users(1), 0)

    def test_count_inactive_users(self):
        user = User(
            user_id=124,
            lang_code='ru',
            difficulty=1,
            review_counter_state='my_review_counter_state',
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            active_game_counter_state=None,
            paused_counter_state=None,
            counters_history_serialized=None,
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized',
            next_autopause_event_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            autopause_config_serialized='blah',
            diamonds=66,
            spent_diamonds=3,
            frontend_base_url_override=None
        )
        self.users_orm.upsert_user(user)
        self.assertEqual(self.users_orm.count_active_users(1), 0)
        self.assertEqual(self.users_orm.count_paused_users(1), 0)
        self.assertEqual(self.users_orm.count_inactive_users(1), 1)



