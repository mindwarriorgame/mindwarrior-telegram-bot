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
    next_prompt_time: Optional[datetime]

    # Game is started when active_game_counter is not None
    active_game_counter_state: Optional[str]
    paused_counter_state: Optional[str]

    counters_history_serialized: Optional[str]

    shared_key_uuid: str

    next_prompt_type: str

    badges_serialized: str

    next_autopause_event_time: Optional[datetime]
    autopause_config_serialized: Optional[str]

    diamonds: int
    spent_diamonds: int

    frontend_base_url_override: Optional[str]

    last_reward_time_at_active_counter_time_secs: int

    has_repeller: bool

    last_admin_message_id_sent: int


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
                next_prompt_time TEXT,
                
                active_game_counter_state TEXT,
                active_game_counter_state_is_null INTEGER NOT NULL DEFAULT 1,
                
                paused_counter_state TEXT,
                paused_counter_state_is_null INTEGER NOT NULL DEFAULT 1,
                                
                counters_history_serialized TEXT,
                
                shared_key_uuid TEXT NOT NULL DEFAULT "",
                
                next_prompt_type TEXT NOT NULL DEFAULT "",
                
                badges_serialized TEXT NOT NULL DEFAULT "",
                
                next_autopause_event_time TEXT,
                autopause_config_serialized TEXT,
                            
                has_repeller INTEGER NOT NULL DEFAULT 1,

                last_admin_message_id_sent INTEGER NOT NULL DEFAULT 0,
                
                PRIMARY KEY (user_id)
            )
        ''')
        self.conn.commit()

        self.cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in self.cursor.fetchall()]
        if "diamonds" not in columns:
            self.cursor.execute(
                "ALTER TABLE users ADD COLUMN diamonds INTEGER NOT NULL DEFAULT 0"
            )
            self.conn.commit()

        if "spent_diamonds" not in columns:
            self.cursor.execute(
                "ALTER TABLE users ADD COLUMN spent_diamonds INTEGER NOT NULL DEFAULT 0"
            )
            self.conn.commit()

        if "frontend_base_url_override" not in columns:
            self.cursor.execute(
                "ALTER TABLE users ADD COLUMN frontend_base_url_override TEXT"
            )
            self.conn.commit()

        if "last_reward_time_at_active_counter_time_secs" not in columns:
            self.cursor.execute(
                "ALTER TABLE users ADD COLUMN last_reward_time_at_active_counter_time_secs INTEGER NOT NULL DEFAULT 0"
            )
            self.conn.commit()

        if "has_repeller" not in columns:
            self.cursor.execute(
                "ALTER TABLE users ADD COLUMN has_repeller INTEGER NOT NULL DEFAULT 1"
            )
            self.conn.commit()

        if "last_admin_message_id_sent" not in columns:
            self.cursor.execute(
                "ALTER TABLE users ADD COLUMN last_admin_message_id_sent INTEGER NOT NULL DEFAULT 0"
            )
            self.conn.commit()

        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_next_prompt_time ON users (difficulty, active_game_counter_state_is_null, paused_counter_state_is_null, next_prompt_time)')
        self.conn.commit()

        self.cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_shared_key_uuid ON users (shared_key_uuid)')
        self.conn.commit()

        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_next_autopause_event_time ON users (next_autopause_event_time)')
        self.conn.commit()

        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_admin_message_id_sent ON users (active_game_counter_state_is_null, last_admin_message_id_sent)')
        self.conn.commit()

    def get_user_by_id(self, user_id: int) -> User:
        """

        :rtype: object
        """
        self.cursor.execute("""SELECT
            user_id,
            lang_code,
            difficulty,
            review_counter_state,
            next_prompt_time,
            active_game_counter_state,
            active_game_counter_state_is_null,
            paused_counter_state,
            paused_counter_state_is_null,
            counters_history_serialized,
            shared_key_uuid,
            next_prompt_type,
            badges_serialized,
            next_autopause_event_time,
            autopause_config_serialized,
            diamonds,
            spent_diamonds,
            frontend_base_url_override,
            last_reward_time_at_active_counter_time_secs,
            has_repeller,
            last_admin_message_id_sent
                FROM users WHERE user_id = ?""", (user_id,))
        return self._to_user_obj(self.cursor.fetchone(), user_id)

    def get_some_users_for_prompt(self, limit: int, difficulty: int) -> list[User]:
        cutoff_time = datetime.now(tz=timezone.utc).isoformat()
        self.cursor.execute("""SELECT
            user_id,
            lang_code,
            difficulty,
            review_counter_state,
            next_prompt_time,
            active_game_counter_state,
            active_game_counter_state_is_null,
            paused_counter_state,
            paused_counter_state_is_null,
            counters_history_serialized,
            shared_key_uuid,
            next_prompt_type,
            badges_serialized,
            next_autopause_event_time,
            autopause_config_serialized,
            diamonds,
            spent_diamonds,
            frontend_base_url_override,
            last_reward_time_at_active_counter_time_secs,
            has_repeller,
            last_admin_message_id_sent
                FROM users WHERE difficulty = ? AND active_game_counter_state_is_null = 0 AND paused_counter_state_is_null = 1 AND next_prompt_time < ? LIMIT ?""",
                            (difficulty, cutoff_time, limit))
        return [self._to_user_obj(row, row[0]) for row in self.cursor.fetchall()]

    def get_some_next_autopause_events(self, limit: int) -> list[User]:
        cutoff_time = datetime.now(tz=timezone.utc).isoformat()
        self.cursor.execute("""SELECT
            user_id,
            lang_code,
            difficulty,
            review_counter_state,
            next_prompt_time,
            active_game_counter_state,
            active_game_counter_state_is_null,
            paused_counter_state,
            paused_counter_state_is_null,
            counters_history_serialized,
            shared_key_uuid,
            next_prompt_type,
            badges_serialized,
            next_autopause_event_time,
            autopause_config_serialized,
            diamonds,
            spent_diamonds,
            frontend_base_url_override,
            last_reward_time_at_active_counter_time_secs,
            has_repeller,
            last_admin_message_id_sent
                FROM users WHERE next_autopause_event_time < ? LIMIT ?""",
                            (cutoff_time, limit))
        return [self._to_user_obj(row, row[0]) for row in self.cursor.fetchall()]

    def count_active_users(self, difficulty: int) -> int:
        self.cursor.execute('SELECT COUNT(*) FROM users WHERE difficulty = ? AND active_game_counter_state_is_null = 0 AND paused_counter_state_is_null = 1',
                            (difficulty,))
        return self.cursor.fetchone()[0]

    def count_recently_rewarded_users(self, difficulty: int) -> int:
        cutoff_time = (datetime.now(tz=timezone.utc) - timedelta(days=1)).isoformat()
        self.cursor.execute('SELECT COUNT(*) FROM users WHERE difficulty = ? AND active_game_counter_state_is_null = 0 AND paused_counter_state_is_null = 1 AND next_prompt_time < ?',
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
                next_prompt_time=None,
                active_game_counter_state=None,
                paused_counter_state=None,
                counters_history_serialized=None,
                shared_key_uuid=str(uuid.uuid4()),
                next_prompt_type="",
                badges_serialized="",
                next_autopause_event_time=None,
                autopause_config_serialized=None,
                diamonds=0,
                spent_diamonds=0,
                frontend_base_url_override=None,
                last_reward_time_at_active_counter_time_secs=0,
                has_repeller=True,
                last_admin_message_id_sent=0
            )
        return User(
            user_id=param[0],
            lang_code=param[1],
            difficulty=param[2],
            review_counter_state=param[3],
            next_prompt_time=safe_convert_to_datetime(param[4]),
            active_game_counter_state=param[5],
            paused_counter_state=param[7],
            counters_history_serialized=param[9],
            shared_key_uuid=param[10],
            next_prompt_type=param[11],
            badges_serialized=param[12],
            next_autopause_event_time=safe_convert_to_datetime(param[13]),
            autopause_config_serialized=param[14],
            diamonds=param[15],
            spent_diamonds=param[16],
            frontend_base_url_override=param[17],
            last_reward_time_at_active_counter_time_secs=param[18],
            has_repeller=bool(param[19]),
            last_admin_message_id_sent=param[20]
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
                next_prompt_time, 
                active_game_counter_state,
                active_game_counter_state_is_null, 
                paused_counter_state,
                paused_counter_state_is_null,
                counters_history_serialized,
                shared_key_uuid,
                next_prompt_type,
                badges_serialized,
                next_autopause_event_time,
                autopause_config_serialized,
                diamonds,
                spent_diamonds,
                frontend_base_url_override,
                last_reward_time_at_active_counter_time_secs,
                has_repeller,
                last_admin_message_id_sent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                lang_code = excluded.lang_code,
                difficulty = excluded.difficulty,
                review_counter_state = excluded.review_counter_state,
                next_prompt_time = excluded.next_prompt_time,
                active_game_counter_state = excluded.active_game_counter_state,
                active_game_counter_state_is_null = excluded.active_game_counter_state_is_null,
                paused_counter_state = excluded.paused_counter_state,
                paused_counter_state_is_null = excluded.paused_counter_state_is_null,
                counters_history_serialized = excluded.counters_history_serialized,
                shared_key_uuid = excluded.shared_key_uuid,
                next_prompt_type = excluded.next_prompt_type,
                badges_serialized = excluded.badges_serialized,
                next_autopause_event_time = excluded.next_autopause_event_time,
                autopause_config_serialized = excluded.autopause_config_serialized,
                diamonds = excluded.diamonds,
                spent_diamonds = excluded.spent_diamonds,
                frontend_base_url_override = excluded.frontend_base_url_override,
                last_reward_time_at_active_counter_time_secs = excluded.last_reward_time_at_active_counter_time_secs,
                has_repeller = excluded.has_repeller,
                last_admin_message_id_sent = excluded.last_admin_message_id_sent
        ''', (
            user['user_id'],
            user['lang_code'],
            user['difficulty'],
            user['review_counter_state'],

            # SQLite doesn't support timezone-aware datetime objects. Let's keep it UTC
            # for portability (if we need to run the bot on a different server)
            user['next_prompt_time'].astimezone(ZoneInfo('UTC')).isoformat() if user['next_prompt_time'] is not None else None,

            user['active_game_counter_state'],
            1 if user['active_game_counter_state'] is None else 0,
            user['paused_counter_state'],
            1 if user['paused_counter_state'] is None else 0,
            user['counters_history_serialized'],
            user['shared_key_uuid'],
            user['next_prompt_type'],
            user['badges_serialized'],

            user['next_autopause_event_time'].astimezone(ZoneInfo('UTC')).isoformat() if user['next_autopause_event_time'] is not None else None,
            user['autopause_config_serialized'],
            user['diamonds'],
            user['spent_diamonds'],
            user['frontend_base_url_override'],
            user.get('last_reward_time_at_active_counter_time_secs', 0),

            1 if user.get('has_repeller', True) else 0,
            user.get('last_admin_message_id_sent', 0)
        ))
        self.conn.commit()

    def get_one_user_for_admin_message(self, last_admin_message_id: int) -> Optional[User]:
        self.cursor.execute("""SELECT
            user_id,
            lang_code,
            difficulty,
            review_counter_state,
            next_prompt_time,
            active_game_counter_state,
            active_game_counter_state_is_null,
            paused_counter_state,
            paused_counter_state_is_null,
            counters_history_serialized,
            shared_key_uuid,
            next_prompt_type,
            badges_serialized,
            next_autopause_event_time,
            autopause_config_serialized,
            diamonds,
            spent_diamonds,
            frontend_base_url_override,
            last_reward_time_at_active_counter_time_secs,
            has_repeller,
            last_admin_message_id_sent
                FROM users WHERE active_game_counter_state_is_null = 0 AND last_admin_message_id_sent < ?
                ORDER BY last_admin_message_id_sent ASC, user_id ASC LIMIT 1""",
                            (last_admin_message_id,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        return self._to_user_obj(row, row[0])
