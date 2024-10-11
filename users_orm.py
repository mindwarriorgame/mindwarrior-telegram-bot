import uuid
from datetime import datetime, timedelta, timezone
import sqlite3
from typing import TypedDict, Optional
from zoneinfo import ZoneInfo

def safe_convert_to_datetime(date_str):
    try:
        return datetime.fromisoformat(date_str).astimezone(timezone.utc) if isinstance(date_str, str) else None
    except ValueError:
        return None

class User(TypedDict):
    user_id: int
    lang_code: Optional[str]

    difficulty: int

    review_counter_state: Optional[str]
    last_reward_time: Optional[datetime]
    next_prompt_time: Optional[datetime]

    # Game is started when active_game_counter is not None
    active_game_counter_state: Optional[str]
    paused_counter_state: Optional[str]

    rewards: int

    counters_history_serialized: Optional[str]

    shared_key_uuid: str

class UsersOrm:

    def __del__(self) -> None:
        self.conn.close()

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

        # Auxiliary columns "_is_null" for efficient indexing and querying of "NOT NULL" condition
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER NOT NULL,
                lang_code TEXT,
                
                difficulty INTEGER NOT NULL DEFAULT 2,
                
                review_counter_state TEXT,
                last_reward_time TIMESTAMP,
                next_prompt_time TIMESTAMP,
                
                active_game_counter_state TEXT,
                active_game_counter_state_is_null INTEGER NOT NULL DEFAULT 1,
                
                paused_counter_state TEXT,
                paused_counter_state_is_null INTEGER NOT NULL DEFAULT 1,
                
                rewards INTEGER NOT NULL DEFAULT 0,
                
                counters_history_serialized TEXT,
                
                shared_key_uuid TEXT NOT NULL DEFAULT "",
                
                PRIMARY KEY (user_id)
            )
        ''')
        self.conn.commit()

        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_next_prompt_time ON users (difficulty, active_game_counter_state_is_null, paused_counter_state_is_null, next_prompt_time)')
        self.conn.commit()

        self.cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_shared_key_uuid ON users (shared_key_uuid)')
        self.conn.commit()

    def get_user_by_id(self, user_id: int) -> User:
        self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        return self._to_user_obj(self.cursor.fetchone(), user_id)

    def get_some_users_for_prompt(self, limit: int, difficulty: int) -> list[User]:
        cutoff_time = datetime.now(tz=timezone.utc)
        self.cursor.execute('SELECT * FROM users WHERE difficulty = ? AND active_game_counter_state_is_null = 0 AND paused_counter_state_is_null = 1 AND next_prompt_time < ? LIMIT ?',
                            (difficulty, cutoff_time, limit))
        return [self._to_user_obj(row, row[0]) for row in self.cursor.fetchall()]

    def count_active_users(self, difficulty: int) -> int:
        self.cursor.execute('SELECT COUNT(*) FROM users WHERE difficulty = ? AND active_game_counter_state_is_null = 0 AND paused_counter_state_is_null = 1',
                            (difficulty,))
        return self.cursor.fetchone()[0]

    def count_recently_rewarded_users(self, difficulty: int) -> int:
        cutoff_time = datetime.now(tz=timezone.utc) - timedelta(days=1)
        self.cursor.execute('SELECT COUNT(*) FROM users WHERE difficulty = ? AND active_game_counter_state_is_null = 0 AND paused_counter_state_is_null = 1 AND ? < last_reward_time',
                            (difficulty, cutoff_time))
        return self.cursor.fetchone()[0]

    def count_paused_users(self, difficulty: int) -> int:
        self.cursor.execute('SELECT COUNT(*) FROM users WHERE difficulty = ? AND active_game_counter_state_is_null = 0 AND paused_counter_state_is_null = 0',
                            (difficulty,))
        return self.cursor.fetchone()[0]

    def count_inactive_users(self, difficulty: int) -> int:
        self.cursor.execute('SELECT COUNT(*) FROM users WHERE difficulty = ? AND active_game_counter_state_is_null = 1',
                            (difficulty,))
        return self.cursor.fetchone()[0]

    def _to_user_obj(self, param, user_id: int):
        if param is None:
            # return default user object
            return User(
                user_id=user_id,
                lang_code=None,
                difficulty=1,
                review_counter_state=None,
                last_reward_time=None,
                next_prompt_time=None,
                active_game_counter_state=None,
                paused_counter_state=None,
                rewards=0,
                counters_history_serialized=None,
                shared_key_uuid=str(uuid.uuid4())
            )
        return User(
            user_id=param[0],
            lang_code=param[1],
            difficulty=param[2],
            review_counter_state=param[3],
            last_reward_time=safe_convert_to_datetime(param[4]),
            next_prompt_time=safe_convert_to_datetime(param[5]),
            active_game_counter_state=param[6],
            paused_counter_state=param[8],
            rewards=param[10],
            counters_history_serialized=param[11],
            shared_key_uuid=param[12]
        )
    def remove_user(self, user_id: int):
        self.cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        self.conn.commit()

    def upsert_user(self, user: User):
        self.cursor.execute('''
            INSERT INTO users (
                user_id, 
                lang_code,
                difficulty, 
                review_counter_state, 
                last_reward_time, 
                next_prompt_time, 
                active_game_counter_state,
                active_game_counter_state_is_null, 
                paused_counter_state,
                paused_counter_state_is_null,
                rewards,
                counters_history_serialized,
                shared_key_uuid
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                lang_code = excluded.lang_code,
                difficulty = excluded.difficulty,
                review_counter_state = excluded.review_counter_state,
                last_reward_time = excluded.last_reward_time,
                next_prompt_time = excluded.next_prompt_time,
                active_game_counter_state = excluded.active_game_counter_state,
                active_game_counter_state_is_null = excluded.active_game_counter_state_is_null,
                paused_counter_state = excluded.paused_counter_state,
                paused_counter_state_is_null = excluded.paused_counter_state_is_null,
                rewards = excluded.rewards,
                counters_history_serialized = excluded.counters_history_serialized,
                shared_key_uuid = excluded.shared_key_uuid
        ''', (
            user['user_id'],
            user['lang_code'],
            user['difficulty'],
            user['review_counter_state'],

            # SQLite doesn't support timezone-aware datetime objects. Let's keep it UTC
            # for portability (if we need to run the bot on a different server)
            user['last_reward_time'].astimezone(ZoneInfo('UTC')) if user['last_reward_time'] is not None else None,
            user['next_prompt_time'].astimezone(ZoneInfo('UTC')) if user['next_prompt_time'] is not None else None,

            user['active_game_counter_state'],
            1 if user['active_game_counter_state'] is None else 0,
            user['paused_counter_state'],
            1 if user['paused_counter_state'] is None else 0,
            user['rewards'],
            user['counters_history_serialized'],
            user['shared_key_uuid']
        ))
        self.conn.commit()

