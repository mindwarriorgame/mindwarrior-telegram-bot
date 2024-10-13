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

db_fname = os.path.abspath('../betterninja_v8.db')
if not os.path.exists(db_fname):
    raise Exception('Database file not found')
users_orm = UsersOrm(db_fname)


count_active_users = 0
count_inactive_users = 0
count_paused_users = 0
count_recently_rewarded_users = 0

for difficulty in range(0, 10):
    count_active_users += users_orm.count_active_users(difficulty)
    count_inactive_users += users_orm.count_inactive_users(difficulty)
    count_paused_users += users_orm.count_paused_users(difficulty)
    count_recently_rewarded_users += users_orm.count_recently_rewarded_users(difficulty)

print(f'Active users: {count_active_users}')
print(f'Recently rewarded users: {count_recently_rewarded_users}')
print(f'Inactive users: {count_inactive_users}')
print(f'Paused users: {count_paused_users}')