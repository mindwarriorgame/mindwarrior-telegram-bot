import datetime
import inspect
import os
import sys

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from counter import Counter
from history import get_timer_recs_from_history, add_timer_rec_to_history
from users_orm import UsersOrm, User

db_fname = os.path.abspath('../mindwarrior.db')
if not os.path.exists(db_fname):
    raise Exception('Database file not found')
users_orm = UsersOrm(db_fname)

# get user_id from command line
user_id = int(sys.argv[1])

user = users_orm.get_user_by_id(user_id)
if user['active_game_counter_state'] is None:
    raise Exception('User has no active game')

def _move_time_n_minutes(self, user: User, n_minutes: int):
    if user['review_counter_state'] is not None:
        counter = Counter(user['review_counter_state'])
        counter.move_time_back(n_minutes)
        user['review_counter_state'] = counter.serialize()
        print(f"Review counter state: {user['review_counter_state']}")
    if user['last_reward_time'] is not None:
        user['last_reward_time'] = user['last_reward_time'] - datetime.timedelta(minutes=n_minutes)
    if user['next_prompt_time'] is not None:
        user['next_prompt_time'] = user['next_prompt_time'] - datetime.timedelta(minutes=n_minutes)
    if user['active_game_counter_state'] is not None:
        counter = Counter(user['active_game_counter_state'])
        counter.move_time_back(n_minutes)
        user['active_game_counter_state'] = counter.serialize()
    if user['paused_counter_state'] is not None:
        counter = Counter(user['paused_counter_state'])
        counter.move_time_back(n_minutes)
        user['paused_counter_state'] = counter.serialize()
    if user['counters_history_serialized'] is not None:
        history_recs = get_timer_recs_from_history(user['counters_history_serialized'])
        new_history = ""
        for rec in history_recs:
            rec['event_datetime'] = rec['event_datetime'] - datetime.timedelta(minutes=n_minutes)
            new_history = add_timer_rec_to_history(new_history, rec)
        user['counters_history_serialized'] = new_history

_move_time_n_minutes(users_orm, user, 60)
users_orm.upsert_user(user)