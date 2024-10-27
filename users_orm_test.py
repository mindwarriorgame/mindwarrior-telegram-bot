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
            last_reward_time=None,
            next_prompt_time=None,
            active_game_counter_state=None,
            paused_counter_state=None,
            rewards=0,
            counters_history_serialized=None,
            shared_key_uuid='abcd',
            next_prompt_type='',
            badges_serialized=''
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
        self.assertEqual(user, User(
            user_id=123,
            lang_code='ru',
            difficulty=1,
            review_counter_state=None,
            last_reward_time=None,
            next_prompt_time=None,
            active_game_counter_state=None,
            paused_counter_state=None,
            rewards=0,
            counters_history_serialized=None,
            shared_key_uuid='abcd',
            next_prompt_type='qwe',
            badges_serialized=''
        ))

        user['lang_code'] = 'en'
        user['difficulty'] = 2
        user['review_counter_state'] = 'my_review_counter_state'
        user['last_reward_time'] = datetime.datetime(2022, 4, 21, 1, 0, 0)
        user['next_prompt_time'] = datetime.datetime(2022, 4, 21, 2, 0, 0)
        user['active_game_counter_state'] = 'my_active_game_counter_state'
        user['paused_counter_state'] = 'my_paused_counter_state'
        user['rewards'] = 10
        user['counters_history_serialized'] = 'my_counters_history_serialized'
        user['shared_key_uuid'] = 'dbca'
        user['next_prompt_type'] = 'ewq'
        user['badges_serialized'] = 'badges_serialized'
        self.users_orm.upsert_user(user)

        self.assertEqual(self.users_orm.get_user_by_id(123), User(
            user_id=123,
            lang_code='en',
            difficulty=2,
            review_counter_state='my_review_counter_state',
            last_reward_time=datetime.datetime(2022, 4, 21, 1, 0, 0).astimezone(datetime.timezone.utc),
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0).astimezone(datetime.timezone.utc),
            active_game_counter_state='my_active_game_counter_state',
            paused_counter_state='my_paused_counter_state',
            rewards=10,
            counters_history_serialized='my_counters_history_serialized',
            shared_key_uuid='dbca',
            next_prompt_type='ewq',
            badges_serialized='badges_serialized'
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
            last_reward_time=datetime.datetime(2022, 4, 21, 1, 0, 0).astimezone(datetime.timezone.utc),
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0).astimezone(datetime.timezone.utc),
            active_game_counter_state='my_active_game_counter_state',
            paused_counter_state=None,
            rewards=10,
            counters_history_serialized='my_counters_history_serialized',
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized'
        )
        self.users_orm.upsert_user(user)
        self.assertEqual(self.users_orm.get_some_users_for_prompt(10, 1), [user])

    @time_machine.travel("2023-04-21 05:00:00")
    def test_get_users_for_prompt_not_fetches_not_started_users(self):
        user = User(
            user_id=124,
            lang_code='ru',
            difficulty=1,
            review_counter_state='my_review_counter_state',
            last_reward_time=datetime.datetime(2022, 4, 21, 1, 0, 0),
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            active_game_counter_state=None,
            paused_counter_state=None,
            rewards=10,
            counters_history_serialized='counters_history_serialized',
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized'
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
            last_reward_time=datetime.datetime(2022, 4, 21, 1, 0, 0),
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            active_game_counter_state='my_active_game_counter_state',
            paused_counter_state=None,
            rewards=10,
            counters_history_serialized='my_counters_history_serialized',
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized'
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
            last_reward_time=datetime.datetime(2022, 4, 21, 1, 0, 0),
            next_prompt_time=datetime.datetime(2023, 4, 21, 5, 59, 0),
            active_game_counter_state='my_active_game_counter_state',
            paused_counter_state=None,
            rewards=10,
            counters_history_serialized=None,
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized'
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
            last_reward_time=datetime.datetime(2022, 4, 21, 1, 0, 0),
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            active_game_counter_state='my_active_game_counter_state',
            paused_counter_state='my_paused_counter_state',
            rewards=10,
            counters_history_serialized=None,
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized'
        )
        self.users_orm.upsert_user(user)
        self.assertEqual(self.users_orm.get_some_users_for_prompt(10, 1), [])

    def test_delete_user(self):
        user = User(
            user_id=124,
            lang_code='ru',
            difficulty=3,
            review_counter_state='my_review_counter_state',
            last_reward_time=datetime.datetime(2022, 4, 21, 1, 0, 0),
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            active_game_counter_state='my_active_game_counter_state',
            paused_counter_state='my_paused_counter_state',
            rewards=10,
            counters_history_serialized=None,
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized'
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
            last_reward_time=None,
            next_prompt_time=None,
            active_game_counter_state=None,
            paused_counter_state=None,
            rewards=0,
            counters_history_serialized=None,
            shared_key_uuid='abcd',
            next_prompt_type='',
            badges_serialized=''
        ))

    def test_count_active_users(self):
        user = User(
            user_id=124,
            lang_code='ru',
            difficulty=1,
            review_counter_state='my_review_counter_state',
            last_reward_time=datetime.datetime(2022, 4, 21, 1, 0, 0),
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            active_game_counter_state='my_active_game_counter_state',
            paused_counter_state=None,
            rewards=10,
            counters_history_serialized=None,
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized'
        )
        self.users_orm.upsert_user(user)
        self.assertEqual(self.users_orm.count_active_users(1), 1)
        self.assertEqual(self.users_orm.count_paused_users(1), 0)
        self.assertEqual(self.users_orm.count_inactive_users(1), 0)
        self.assertEqual(self.users_orm.count_recently_rewarded_users(1), 0)

    @time_machine.travel("2022-04-21 00:00:00")
    def test_count_recently_rewarded_users(self):
        user = User(
            user_id=124,
            lang_code='ru',
            difficulty=1,
            review_counter_state='my_review_counter_state',
            last_reward_time=datetime.datetime(2022, 4, 21, 1, 0, 0),
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            active_game_counter_state='my_active_game_counter_state',
            paused_counter_state=None,
            rewards=10,
            counters_history_serialized=None,
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized'
        )
        self.users_orm.upsert_user(user)
        self.assertEqual(self.users_orm.count_active_users(1), 1)
        self.assertEqual(self.users_orm.count_paused_users(1), 0)
        self.assertEqual(self.users_orm.count_inactive_users(1), 0)
        self.assertEqual(self.users_orm.count_recently_rewarded_users(1), 1)

    def test_count_paused_users(self):
        user = User(
            user_id=124,
            lang_code='ru',
            difficulty=1,
            review_counter_state='my_review_counter_state',
            last_reward_time=datetime.datetime(2022, 4, 21, 1, 0, 0),
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            active_game_counter_state='my_active_game_counter_state',
            paused_counter_state='paused',
            rewards=10,
            counters_history_serialized=None,
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized'
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
            last_reward_time=datetime.datetime(2022, 4, 21, 1, 0, 0),
            next_prompt_time=datetime.datetime(2022, 4, 21, 2, 0, 0),
            active_game_counter_state=None,
            paused_counter_state=None,
            rewards=10,
            counters_history_serialized=None,
            shared_key_uuid='abcd',
            next_prompt_type='prompt_type',
            badges_serialized='badges_serialized'
        )
        self.users_orm.upsert_user(user)
        self.assertEqual(self.users_orm.count_active_users(1), 0)
        self.assertEqual(self.users_orm.count_paused_users(1), 0)
        self.assertEqual(self.users_orm.count_inactive_users(1), 1)



