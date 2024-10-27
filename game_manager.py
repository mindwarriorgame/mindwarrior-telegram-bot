import datetime
import uuid
from typing import TypedDict, Optional
import time

from badges_manager import BadgesManager
from counter import Counter
from graph_renderer import REVIEW_COUNTER_HISTORY_NAME, PAUSED_COUNTER_HISTORY_NAME, GraphRenderer
from history import add_timer_rec_to_history, get_timer_recs_from_history
from lang_provider import LangProvider, Lang
from users_orm import UsersOrm, User


class Button(TypedDict):
    text: str
    url: str

class Reply(TypedDict):
    to_chat_id: int
    message: str
    buttons: list[Button]
    menu_commands: list[list[str]]
    image: Optional[str]

REVIEW_INTERVAL_MINS = 15

PROMPT_MINUTES = [60*6, 60*3, 60 + 30, 60, 45]

REWARD_BEFORE_REMINDER = [2, 2, 1, 1, 1, 1]
REWARD_AFTER_REMINDER = [1, 1, 1, 1, 1, 1]
HAS_REMINDER = [True, True, True, False, False]

PENALTY_SMALL = 3
PENALTY_FULL = 6
PENALTY_FIRST =      [0, 0, 3, 3, 6]
PENALTY_CONSEQUENT = [0, 3, 6, 6, 6]

NEXT_REVIEW_PROMPT_MINUTES_QUERY_PARAM  = 'next_review_prompt_minutes=' + ",".join([str(PROMPT_MINUTES[idx]) for idx in range(0, len(PROMPT_MINUTES))])

NEXT_PROMPT_TYPE_REMINDER = "reminder"
NEXT_PROMPT_TYPE_PENALTY = "penalty"

def now_utc() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.timezone.utc)

class GameManager:
    def __init__(self, db_fname, env, frontend_base_url):
        self.users_orm = UsersOrm(db_fname)
        self.env = env
        self.frontend_base_url = frontend_base_url

    def on_start_command(self, chat_id: int) -> Reply:
        languages = LangProvider.get_available_languages()
        return self._render_list_of_langs(chat_id, languages)

    def on_help_command(self, chat_id: int) -> Reply:
        user = self.users_orm.get_user_by_id(chat_id)
        if user['lang_code'] is None:
            return self.on_start_command(chat_id)
        lang = self._get_user_lang(user['lang_code'])

        return self._render_start_game_button(lang, user)

    def on_lang_input(self, chat_id: int, user_message: str) -> Reply:
        lang_code = user_message[1:]
        languages = LangProvider.get_available_languages()
        if lang_code in languages:
            user = self.users_orm.get_user_by_id(chat_id)
            user['lang_code'] = lang_code
            self.users_orm.upsert_user(user)
            return self.on_help_command(chat_id)
        else:
            return self._render_single_message(chat_id, "Invalid language code. Try again (/start)")

    def _get_user_lang(self, lang_code: str) -> Lang:
        languages = LangProvider.get_available_languages()
        lang = languages[lang_code]
        if lang is None:
            raise Exception(f"Unsupported language code: {lang_code}")
        return lang

    def on_data_provided(self, chat_id: int, user_message: str) -> list[Reply]:
        user = self.users_orm.get_user_by_id(chat_id)
        if user['lang_code'] is None:
            return [self.on_start_command(chat_id)]

        lang = self._get_user_lang(user['lang_code'])
        if "render_screen_" in user_message:
            return self.on_render_screen(chat_id, user_message)
        if "start_game" in user_message:
            return self._on_start_game(lang, user, user_message)
        if "formula_updated" in user_message:
            return self._on_formula_updated(lang, user)
        if "set_difficulty:" in user_message:
            return [self._on_set_difficulty(lang, user, user_message)]
        if "reviewed_at:" in user_message:
            return self._on_reviewed(lang, user, user_message)
        if "regenerate_shared_key_uuid" in user_message:
            user['shared_key_uuid'] = str(uuid.uuid4())
            self.users_orm.upsert_user(user)
            return [self._render_single_message(chat_id, "Shared key UUID regenerated")]
        if "delete_data_confirmed" in user_message:
            self.users_orm.remove_user(chat_id)
            return [self._render_single_message(chat_id, lang.data_deleted)]

        return [self._render_single_message(chat_id, "Invalid data")]

    def _format_time_minutes(self, lang: Lang, time_secs: int, skip_zeros = False) -> str:
        days = int(time_secs // 86400)
        hours = int((time_secs % 86400) // 3600)
        minutes = int((time_secs % 3600) // 60)

        ret = []
        if days > 0 or not skip_zeros:
            ret.append(f"{days}{lang.days_short}")
        if hours > 0 or not skip_zeros:
            ret.append(f"{hours}{lang.hours_short}")

        if len(ret) == 0 or minutes > 0:
            ret.append(f"{minutes}{lang.minutes_short}")

        return " ".join(ret)

    def _format_time_seconds(self, lang: Lang, time_secs: int) -> str:
        minutes = int(time_secs // 60)
        seconds = int(time_secs % 60)
        return f"{minutes}{lang.minutes_short} {seconds}{lang.seconds_short}"

    def _on_start_game(self, lang: Lang, user: User, user_message) -> [Reply]:
        next_review_prompt_times = user_message.split("start_game;next_review:")[1].split(",,")
        self._restart_user_game(user)

        return self._wrap_with_badge(lang, user, 'on_game_started', self._render_game_started_screen(next_review_prompt_times[user['difficulty']], user['difficulty'], lang, user['user_id']))

    def _on_formula_updated(self, lang: Lang, user: User) -> [Reply]:
        return self._wrap_with_badge(lang, user, 'on_formula_updated', self._render_single_message(user['user_id'], lang.formula_changed))

    def _on_set_difficulty(self, lang: Lang, user: User, user_message: str) -> Reply:
        if user['active_game_counter_state'] is None:
            return self._render_start_game_button(lang, user)

        new_difficulty = 0
        next_review_at = 0
        try :
            split = user_message.split("set_difficulty:")[1]
            new_difficulty = int(split.split(';')[0])
            next_reviews = split.split(';')[1].split('next_review:')[1].split(',,')
            next_review_at = next_reviews[new_difficulty]
        except:
            return self._render_single_message(user['user_id'], "Cannot parse input")
        if new_difficulty < 0 or new_difficulty >= len(lang.difficulties):
            return self._render_single_message(user['user_id'], "Invalid difficulty level")

        old_difficulty = user['difficulty']
        if old_difficulty is None:
            old_difficulty = 0

        is_resumed = self._maybe_resume(user, lang)

        user['difficulty'] = new_difficulty
        self._restart_user_game(user)

        self.users_orm.upsert_user(user)

        return self._render_difficulty_changed(user['user_id'], lang, old_difficulty, new_difficulty, next_review_at, is_resumed)

    def _restart_user_game(self, user: User):
        user['review_counter_state'] = Counter('').resume().serialize()
        user['last_reward_time'] = None

        self._reset_user_next_prompt(user)

        user['active_game_counter_state'] = Counter('').resume().serialize()
        user['paused_counter_state'] = None

        user['rewards'] = 0
        user['counters_history_serialized'] = None
        user['badges_serialized'] = ''
        self.users_orm.upsert_user(user)

    def on_review_command(self, chat_id) -> Reply:
        user = self.users_orm.get_user_by_id(chat_id)
        if user['lang_code'] is None:
            return self.on_start_command(chat_id)
        lang = self._get_user_lang(user['lang_code'])

        if user['active_game_counter_state'] is None:
            return self._render_start_game_button(lang, user)

        counter_active_game = Counter(user['active_game_counter_state'])
        counter_review_state = Counter(user['review_counter_state'])

        since_last_review_secs = None
        if abs(counter_active_game.get_total_seconds() - counter_review_state.get_total_seconds()) > 60:
            since_last_review_secs = int(Counter(user['review_counter_state']).get_total_seconds())

        is_paused = user['paused_counter_state'] is not None

        return self._render_review_screen(lang, user['user_id'], is_paused, since_last_review_secs)


    def _on_reviewed(self, lang: Lang, user: User, user_message: str) -> [Reply]:
        if user['active_game_counter_state'] is None:
            return self._render_start_game_button(lang, user)

        now_timestamp = time.time()
        next_review = None
        user_timestamp = 0
        try:
            user_timestamp = int(user_message.split('reviewed_at:')[1].split(';')[0])
            next_review = user_message.split('next_review:')[1].split(',,')[user['difficulty']]
        except:
            return [self._render_single_message(user['user_id'], "Cannot parse input")]
        delta = abs(now_timestamp - user_timestamp)
        if delta > 60:
            return [{
                'to_chat_id': user['user_id'],
                'message': lang.review_command_timeout,
                'buttons': [self._render_review_button(lang)],
                'menu_commands': []
            }]

        is_resumed = self._maybe_resume(user, lang)

        since_last_review_secs = int(Counter(user['review_counter_state']).get_total_seconds())

        new_stars = REWARD_AFTER_REMINDER[user['difficulty']]
        if user['next_prompt_type'] == NEXT_PROMPT_TYPE_REMINDER and since_last_review_secs < PROMPT_MINUTES[user['difficulty']] * 60:
            new_stars = REWARD_BEFORE_REMINDER[user['difficulty']]

        if user['last_reward_time'] is not None and (now_utc() - user['last_reward_time']).total_seconds() < 5*60:
            new_stars = 0
        else:
            user['last_reward_time'] = now_utc()
            user['rewards'] += new_stars

        self._record_counter_time(user, REVIEW_COUNTER_HISTORY_NAME, user['review_counter_state'])
        user['review_counter_state'] = Counter('').resume().serialize()

        self._reset_user_next_prompt(user)

        self.users_orm.upsert_user(user)

        if new_stars > 0:
            return self._wrap_with_badge(lang, user, 'on_review', self._render_review_command_success(user['rewards'], next_review,
                                                time=self._format_time_minutes(lang, self._calculate_active_play_time_seconds(user)),
                                                lang=lang,
                                                chat_id=user['user_id'], is_resumed=is_resumed, new_stars=new_stars))
        else:
            return [self._render_review_command_success_no_rewards(user['rewards'], next_review,
                                                time=self._format_time_minutes(lang, self._calculate_active_play_time_seconds(user)),
                                                lang=lang,
                                                chat_id=user['user_id'], is_resumed=is_resumed)]


    def _calculate_active_play_time_seconds(self, user: User) -> int:
        counter = Counter(user['active_game_counter_state'])
        return int(counter.get_total_seconds())

    def _render_start_game_button(self, lang: Lang, user: User) -> Reply:
        return {
            'to_chat_id': user['user_id'],
            'message': lang.help_command_text.format(difficulty=lang.difficulties[user['difficulty']]),
            'buttons': [
                {
                    'text': lang.help_command_start_playing_button,
                    'url': self.frontend_base_url + f'?env={self.env}&lang_code={lang.lang_code}&new_game=1&{NEXT_REVIEW_PROMPT_MINUTES_QUERY_PARAM}'
                }
            ],
            'menu_commands': [
                ["review", lang.menu_review],
                ["pause", lang.menu_pause],
                ["formula", lang.menu_formula],
                ["stats", lang.menu_stats],
                ["difficulty", lang.menu_difficulty],
                ["data", lang.menu_data]
            ],
            'image': None
        }

    def on_data_command(self, chat_id) -> Reply:
        user = self.users_orm.get_user_by_id(chat_id)
        if user['lang_code'] is None:
            return self.on_start_command(chat_id)
        lang = self._get_user_lang(user['lang_code'])

        data = [" - shared_key_uuid: " + user['shared_key_uuid']]
        for key in user:
            value = str(user[key])
            if len(value) > 256:
                value = value[:256] + "..."
            if key != 'shared_key_uuid':
                data.append(f" - {key}: {value}")

        return self._render_delete_data_screen(lang, chat_id, data)

    def on_pause_command(self, chat_id) -> Reply:
        user = self.users_orm.get_user_by_id(chat_id)
        if user['lang_code'] is None:
            return self.on_start_command(chat_id)
        lang = self._get_user_lang(user['lang_code'])

        if user['active_game_counter_state'] is None:
            return self._render_start_game_button(lang, user)

        if user['paused_counter_state'] is None:
            paused_counter = Counter("")
            paused_counter.resume()
            user['paused_counter_state'] = paused_counter.serialize()

            active_counter = Counter(user['active_game_counter_state'])
            active_counter.pause()
            user['active_game_counter_state'] = active_counter.serialize()

            review_counter = Counter(user['review_counter_state'])
            review_counter.pause()
            user['review_counter_state'] = review_counter.serialize()

            self.users_orm.upsert_user(user)

            return self._render_on_pause(lang, user['user_id'])
        else:
            return self._render_already_on_pause(lang, chat_id)

    def on_stats_command(self, chat_id) -> Reply:
        user = self.users_orm.get_user_by_id(chat_id)
        if user['lang_code'] is None:
            return self.on_start_command(chat_id)
        lang = self._get_user_lang(user['lang_code'])

        if user['active_game_counter_state'] is None:
            return self._render_start_game_button(lang, user)

        last_reward_time = user['last_reward_time'] if user['last_reward_time'] is not None else now_utc()
        since_last_reward_secs = int((now_utc() - last_reward_time).total_seconds())

        till_next_prompt_time = 0
        if user['next_prompt_time'] is not None:
            till_next_prompt_time = int((user['next_prompt_time'] - now_utc()).total_seconds())
            if till_next_prompt_time < 0:
                till_next_prompt_time = 0

        paused_at = None
        if user['paused_counter_state'] is not None:
            paused_at = now_utc() - datetime.timedelta(seconds=Counter(user['paused_counter_state']).get_total_seconds())

        fname = GraphRenderer().render_graph(lang, get_timer_recs_from_history(
            user['counters_history_serialized']), PROMPT_MINUTES[user['difficulty']]
                                             , lang.difficulties[user['difficulty']],
                                             paused_at)

        return self._render_stats(lang, user['user_id'], user['rewards'], user['difficulty'], self._calculate_active_play_time_seconds(user),
                                  user['paused_counter_state'] is not None, since_last_reward_secs, till_next_prompt_time, fname)

    def on_difficulty_command(self, chat_id) -> Reply:
        user = self.users_orm.get_user_by_id(chat_id)
        if user['lang_code'] is None:
            return self.on_start_command(chat_id)
        lang = self._get_user_lang(user['lang_code'])

        return self._render_difficulty_buttons(lang, user['user_id'], user['difficulty'])

    def on_formula_command(self, chat_id) -> Reply:
        user = self.users_orm.get_user_by_id(chat_id)
        if user['lang_code'] is None:
            return self.on_start_command(chat_id)
        lang = self._get_user_lang(user['lang_code'])

        return self._render_edit_formula(lang, user["shared_key_uuid"], user['user_id'])

    def process_tick(self) -> list[Reply]:
        replies: list[Reply] = []
        for difficulty in range(0, 5):
            users = self.users_orm.get_some_users_for_prompt(20, difficulty)
            for user in users:
                if user['next_prompt_type'] == NEXT_PROMPT_TYPE_PENALTY:
                    replies += self._process_penalty_prompt(user)
                else:
                    replies += self._process_reminder_prompt(user)

        return replies

    def _process_penalty_prompt(self, user: User) -> [Reply]:
        difficulty = user['difficulty']
        penalty_minutes = PROMPT_MINUTES[difficulty]

        self._reset_user_next_prompt(user)

        lang = self._get_user_lang(user['lang_code'])

        review_counter = Counter(user['review_counter_state'])
        is_first_penalty = (review_counter.get_total_seconds() / 60) <= penalty_minutes * 1.5

        user['rewards'] -= self._calculate_penalty(difficulty, is_first_penalty)
        self.users_orm.upsert_user(user)

        return self._wrap_with_badge(lang, user, 'on_penalty', self._render_penalty(lang, user['user_id'], user['difficulty'], user['rewards'], is_first_penalty))

    def _record_counter_time(self, user: User, counter_name: str, serialized_counter: str):
        counter = Counter(serialized_counter)
        user['counters_history_serialized'] = add_timer_rec_to_history(user['counters_history_serialized'], {
            'counter_name': counter_name,
            'counter_stopped_duration_secs': int(counter.get_total_seconds()),
            'event_datetime': now_utc()
        })

    def _render_review_button(self, lang) -> Button:
        return {
            'text': lang.review_btn,
            'url': self.frontend_base_url +
                   f'?env={self.env}&lang_code={lang.lang_code}&review=1&{NEXT_REVIEW_PROMPT_MINUTES_QUERY_PARAM}'
        }

    def _render_game_started_screen(self, next_review: str, difficulty: int, lang: Lang, chat_id: int) -> Reply:
        difficulty = lang.difficulties[difficulty]
        return {
            'to_chat_id': chat_id,
            'message': lang.game_started.format(next_review=next_review, difficulty=difficulty),
            'buttons': [self._render_review_button(lang)],
            'menu_commands': [],
            'image': None
        }

    def _render_review_command_success(self, score: int, next_review: str, time: str, lang: Lang, chat_id: int, is_resumed: bool, new_stars: int) -> Reply:
        if new_stars != 1 and new_stars != 2:
            raise Exception("Invalid new_stars value")
        message = lang.review_command_success_text.format(score=score, next_review=next_review, time=time,
                                                          reward_msg=lang.review_reward_msg if new_stars == 1 else lang.review_reward_msg_very_happy)
        if is_resumed:
            message = lang.resumed + "\n" + message
        return {
            'to_chat_id': chat_id,
            'message': message,
            'buttons': [self._render_review_button(lang)],
            'menu_commands': [],
            'image': None
        }

    def _render_review_command_success_no_rewards(self, score: int, next_review: str, time: str, lang: Lang, chat_id: int, is_resumed: bool) -> Reply:
        message = lang.review_command_success_no_rewards_text.format(score=score, next_review=next_review, time=time)
        if is_resumed:
            message = lang.resumed + "\n" + message
        return {
            'to_chat_id': chat_id,
            'message': message,
            'buttons': [self._render_review_button(lang)],
            'menu_commands': [],
            'image': None
        }



    def on_render_screen(self, chat_id, user_message) -> list[Reply]:
        langs = LangProvider.get_available_languages()

        if user_message == "render_screen_0":
            return [self._render_list_of_langs(chat_id, langs)]

        if user_message == "render_screen_1":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_game_started_screen("10:00", 1, lang, chat_id)]
            return ret

        if user_message == "render_screen_2":
            ret = []
            for is_resumed in [True, False]:
                for lang_code, lang in langs.items():
                    ret = ret + [self._render_review_command_success(5, "10:00", "1d 3h 5m", lang, chat_id, is_resumed, 1)]
                    ret = ret + [self._render_review_command_success(5, "10:00", "1d 3h 5m", lang, chat_id, is_resumed, 2)]
            return ret

        if user_message == "render_screen_3":
            ret = []
            for is_resumed in [True, False]:
                for lang_code, lang in langs.items():
                    ret = ret + [self._render_review_command_success_no_rewards(5, "10:00", "1d 3h 5m", lang, chat_id, is_resumed)]
            return ret

        if user_message == "render_screen_4":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_penalty(lang, chat_id, 0, 10, True)]
                ret = ret + [self._render_penalty(lang, chat_id, 4, 10, True)]
            return ret

        if user_message == "render_screen_5":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_penalty(lang, chat_id, 1, 10, True)]
                ret = ret + [self._render_penalty(lang, chat_id, 1, 10, False)]
            return ret

        if user_message == "render_screen_6":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_penalty(lang, chat_id, 2, 10, True)]
                ret = ret + [self._render_penalty(lang, chat_id, 2, 10, False)]
            return ret


        if user_message == "render_screen_7":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_difficulty_buttons(lang, chat_id, 2)]
            return ret

        if user_message == "render_screen_8":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_difficulty_changed(chat_id, lang, 0, 1, "10:00", False)]
                ret = ret + [self._render_difficulty_changed(chat_id, lang, 2, 3, "10:00", True)]
                ret = ret + [self._render_difficulty_changed(chat_id, lang, 3, 4, "10:00", False)]
            return ret

        if user_message == "render_screen_9":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_stats(lang, chat_id, 5, 2, 1000, False, 100, 1000, None)]
            return ret

        if user_message == "render_screen_10":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_edit_formula(lang, 'blahbah', chat_id)]
            return ret

        if user_message == "render_screen_11":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_review_screen(lang, chat_id, True, None)]
                ret = ret + [self._render_review_screen(lang, chat_id, False, None)]
                ret = ret + [self._render_review_screen(lang, chat_id, False, 123321)]
            return ret

        if user_message == "render_screen_12":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_on_pause(lang, chat_id)]
            return ret

        if user_message == "render_screen_13":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_already_on_pause(lang, chat_id)]
            return ret

        if user_message == "render_screen_14":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_delete_data_screen(lang, chat_id, [" - shared_key_uuid: blahblah"])]
            return ret

        if user_message == "render_screen_15":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_single_message(chat_id, lang.data_deleted)]
            return ret

        if user_message == "render_screen_16":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_single_message(chat_id, lang.formula_changed)]
            return ret

        if user_message == "render_screen_17":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_reminder_prompt(lang, chat_id)]
            return ret
        return []

    def _maybe_resume(self, user: User, lang: Lang) -> bool:
        if user['paused_counter_state']:
            active_play_time_counter = Counter(user['active_game_counter_state'])
            active_play_time_counter.resume()
            user['active_game_counter_state'] = active_play_time_counter.serialize()

            self._record_counter_time(user, PAUSED_COUNTER_HISTORY_NAME, user['paused_counter_state'])
            user['paused_counter_state'] = None

            review_counter = Counter(user['review_counter_state'])
            review_counter.resume()
            user['review_counter_state'] = review_counter.serialize()

            user['paused_counter_state'] = None

            return True
        return False

    def _render_list_of_langs(self, chat_id, languages: dict[str, Lang]) -> Reply:
        message = ""
        for lang_code in sorted(languages):
            lang = languages[lang_code]
            new_lang_msg = "/" + lang_code + " - " + lang.lang_name
            if (lang_code == "en"):
                message = new_lang_msg + "\n\n" + message
            else:
                message += new_lang_msg + "\n\n"
        return self._render_single_message(chat_id, message)

    def _render_single_message(self, chat_id, msg) -> Reply:
        return {
            'to_chat_id': chat_id,
            'message': msg,
            'buttons': [],
            'menu_commands': [],
            'image': None
        }

    def _render_difficulty_buttons(self, lang: Lang, chat_id, curr_difficulty) -> Reply:
        buttons: list[Button] = []
        for difficulty in range(0, 5):
            text = lang.difficulties[difficulty] + " (" + self._format_time_minutes(lang, PROMPT_MINUTES[difficulty] * 60, skip_zeros=True) + ")"

            if difficulty == curr_difficulty:
                text = text + " - " + lang.current_difficulty
            buttons.append({
                'text': text,
                'url': self.frontend_base_url + f'?env={self.env}&lang_code={lang.lang_code}&set_difficulty={difficulty}&' + NEXT_REVIEW_PROMPT_MINUTES_QUERY_PARAM
            })

        return {
            'to_chat_id': chat_id,
            'message': lang.difficulty_command_text,
            'buttons': buttons,
            'menu_commands': [],
            'image': None
        }

    def _render_difficulty_changed(self, chat_id, lang, old_difficulty, new_difficulty, next_review_at, is_resumed) -> Reply:
        message = lang.difficulty_level_changed.format(old=lang.difficulties[old_difficulty], new=lang.difficulties[new_difficulty], next_review=next_review_at)
        if is_resumed:
            message = lang.resumed + "\n" + message
        return {
            'to_chat_id': chat_id,
            'message': message,
            'buttons': [self._render_review_button(lang)],
            'menu_commands': [],
            'image': None
        }

    def _render_stats(self, lang, chat_id, rewards, difficulty, active_play_time_seconds, is_paused, since_last_reward_secs, till_next_prompt_time, fname) -> Reply:
        return {
            'to_chat_id': chat_id,
            'message': lang.stats_command.format(
                score=rewards,
                difficulty=lang.difficulties[difficulty],
                difficulty_details=str(difficulty + 1) + "/" + str(len(lang.difficulties)),
                time=self._format_time_minutes(lang, active_play_time_seconds),
                paused="⚪" if is_paused is None else "🟢",
                cooldown=self._format_time_seconds(lang, 5*60 - since_last_reward_secs if since_last_reward_secs < 5*60 else 0),
                punishment=self._format_time_minutes(lang, till_next_prompt_time, skip_zeros=True)
            ),
            'buttons': [],
            'menu_commands': [],
            'image': fname
        }

    def _render_edit_formula(self, lang, shared_key_uuid, chat_id):
        return {
            'to_chat_id': chat_id,
            'message': lang.formula_command_text,
            'buttons': [
                {
                    'text': lang.formula_command_button,
                    'url': self.frontend_base_url + f'?env={self.env}&lang_code={lang.lang_code}&formula=1&shared_key_uuid={shared_key_uuid}'
                }
            ],
            'menu_commands': [],
            'image': None
        }

    def _render_review_screen(self, lang, chat_id, is_paused: bool, since_last_review_secs):
        message = []
        if is_paused:
            message.append(lang.review_paused_text)
        elif since_last_review_secs is not None:
            message.append(lang.review_since_last_time.format(duration=self._format_time_minutes(lang, since_last_review_secs)))

        message.append(lang.review_command_text)

        return {
            'to_chat_id': chat_id,
            'message': "\n".join(message),
            'buttons': [
                {
                    'text': lang.review_command_button_yourself,
                    'url': self.frontend_base_url +
                           f'?env={self.env}&lang_code={lang.lang_code}&review=1&{NEXT_REVIEW_PROMPT_MINUTES_QUERY_PARAM}'
                },
                {
                    'text': lang.review_command_button_world,
                    'url': self.frontend_base_url +
                           f'?env={self.env}&lang_code={lang.lang_code}&review=1&{NEXT_REVIEW_PROMPT_MINUTES_QUERY_PARAM}'
                }
            ],
            'menu_commands': [],
            'image': None
        }

    def _render_on_pause(self, lang: Lang, chat_id):
        return {
            'to_chat_id': chat_id,
            'message': lang.paused_command,
            'buttons': [self._render_review_button(lang)],
            'menu_commands': [],
            'image': None
        }

    def _render_already_on_pause(self, lang: Lang, chat_id):
        return {
            'to_chat_id': chat_id,
            'message': lang.already_paused,
            'buttons': [self._render_review_button(lang)],
            'menu_commands': [],
            'image': None
        }

    def _render_delete_data_screen(self, lang, chat_id, data):
        return {
            'to_chat_id': chat_id,
            'message': lang.data_view + "\n\n" + "\n\n".join(data),
            'buttons': [
                {
                    'text': lang.data_view_localstorage_button,
                    'url': self.frontend_base_url + f'?env={self.env}&lang_code={lang.lang_code}&view_localstorage=1'
                },
                {
                    'text': lang.data_delete_button,
                    'url': self.frontend_base_url + f'?env={self.env}&lang_code={lang.lang_code}&delete_data=1'
                }
            ],
            'menu_commands': [],
            'image': None
        }

    def _render_penalty(self, lang: Lang, chat_id: int, difficulty: int, scores: int, is_first_penalty: bool) -> Reply:
        penalty_msg = ""
        penalty = self._calculate_penalty(difficulty, is_first_penalty)

        if PENALTY_CONSEQUENT[difficulty] == 0:
            penalty_msg = lang.penalty_msg_no_penalty_for_level.format(difficulty=lang.difficulties[difficulty])

        elif is_first_penalty and PENALTY_FIRST[difficulty] == 0:
            penalty_msg = lang.penalty_msg_no_penalty_first_time.format(difficulty=lang.difficulties[difficulty])

        elif is_first_penalty and PENALTY_FIRST[difficulty] < PENALTY_CONSEQUENT[difficulty]:
            penalty_msg = lang.penalty_msg_first_time.format(difficulty=lang.difficulties[difficulty], penalty=penalty, score=scores)

        elif penalty == PENALTY_SMALL:
            penalty_msg = lang.penalty_msg_generic_small.format(difficulty=lang.difficulties[difficulty], penalty=penalty, score=scores)

        elif penalty == PENALTY_FULL:
            penalty_msg = lang.penalty_msg_generic_full.format(difficulty=lang.difficulties[difficulty], penalty=penalty, score=scores)

        if penalty_msg == "":
            raise Exception("Unknown penalty message")

        return {
            'to_chat_id': chat_id,
            'message': lang.penalty_text.format(penalty_msg=penalty_msg),
            'buttons': [self._render_review_button(lang)],
            'menu_commands': [],
            'image': None
        }

    def _process_reminder_prompt(self, user: User) -> [Reply]:
        lang = self._get_user_lang(user['lang_code'])

        user['next_prompt_type'] = NEXT_PROMPT_TYPE_PENALTY
        user['next_prompt_time'] = now_utc() + datetime.timedelta(minutes=REVIEW_INTERVAL_MINS)
        self.users_orm.upsert_user(user)

        return self._wrap_with_badge(lang, user, 'on_prompt', self._render_reminder_prompt(lang, user['user_id']))

    def _reset_user_next_prompt(self, user: User):
        difficulty = user['difficulty']
        penalty_minutes = PROMPT_MINUTES[difficulty]

        user['next_prompt_time'] = now_utc() + datetime.timedelta(minutes=penalty_minutes)
        user['next_prompt_type'] = NEXT_PROMPT_TYPE_PENALTY
        if HAS_REMINDER[difficulty]:
            user['next_prompt_time'] -= datetime.timedelta(minutes=REVIEW_INTERVAL_MINS)
            user['next_prompt_type'] = NEXT_PROMPT_TYPE_REMINDER

    def _calculate_penalty(self, difficulty, is_first_penalty):
        return PENALTY_FIRST[difficulty] if is_first_penalty else PENALTY_CONSEQUENT[difficulty]

    def _render_reminder_prompt(self, lang, chat_id):
        return {
            'to_chat_id': chat_id,
            'message': lang.reminder_text,
            'buttons': [self._render_review_button(lang)],
            'menu_commands': [],
            'image': None
        }

    def _wrap_with_badge(self, lang: Lang, user: User, action, reply: Reply) -> [Reply]:
        badges_manager = BadgesManager(user['badges_serialized'])
        active_game_counter_secs = Counter(user['active_game_counter_state']).get_total_seconds()
        badge = getattr(badges_manager, action)(active_game_counter_secs)
        user['badges_serialized'] = badges_manager.serialize()
        self.users_orm.upsert_user(user)
        result = []
        if badge is not None:
            result = result + [{
                'to_chat_id': user['user_id'],
                'message': lang.new_achievement,
                'buttons': [],
                'menu_commands': [],
                'image': './badge-images/' + badge + '.jpg'
            }]
        # stretch the content to align with the badge
        INVISIBLE_SPACE_EMOJI = "ㅤ"
        reply['message']  = reply['message'] + ((INVISIBLE_SPACE_EMOJI + " ") * 10)
        result = result + [reply]
        return result




















