import copy
import datetime
import uuid
from typing import TypedDict, Optional, NotRequired
import time

import numpy as np

from autopause_manager import AutopauseManager
from badges_manager import BadgesManager
from board_serializer import serialize_board, serialize_progress
from counter import Counter
from graph_renderer import REVIEW_COUNTER_HISTORY_NAME, PAUSED_COUNTER_HISTORY_NAME, GraphRenderer
from history import add_timer_rec_to_history, get_timer_recs_from_history
from lang_provider import LangProvider, Lang, en, ru
from users_orm import UsersOrm, User


class Button(TypedDict):
    text: str
    data: NotRequired[str]
    url: NotRequired[str]

class Reply(TypedDict):
    to_chat_id: int
    message: str
    buttons: list[Button]
    menu_commands: list[list[str]]
    image: Optional[str]

REVIEW_INTERVAL_MINS = 15

PROMPT_MINUTES = [60*6, 60*3, 60 + 30, 60, 45]

HAS_REMINDER = [True, True, True, False, False]

NEXT_REVIEW_PROMPT_MINUTES_QUERY_PARAM  = 'next_review_prompt_minutes=' + ",".join([str(PROMPT_MINUTES[idx]) for idx in range(0, len(PROMPT_MINUTES))])

NEXT_PROMPT_TYPE_REMINDER = "reminder"
NEXT_PROMPT_TYPE_PENALTY = "penalty"

# Too much effort to keep it in the Db, and too low value. Let's do in-memory instead
LAST_PROGRESS_CACHE = {}

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

        return self._render_start_game_screen(lang, user)

    def on_lang_input(self, chat_id: int, user_message: str) -> Reply:
        lang_code = user_message[1:] if user_message.startswith("/") else user_message
        languages = LangProvider.get_available_languages()
        if lang_code in languages:
            user = self.users_orm.get_user_by_id(chat_id)
            user['lang_code'] = lang_code
            self.users_orm.upsert_user(user)
            return self.on_help_command(chat_id)
        else:
            return self._render_single_message(chat_id, "Invalid language code. Try again (/start)", None, None)

    def _get_user_lang(self, lang_code: str) -> Lang:
        languages = LangProvider.get_available_languages()
        lang = languages[lang_code]
        if lang is None:
            raise Exception(f"Unsupported language code: {lang_code}")
        return lang

    def on_data_provided(self, chat_id: int, user_message: str) -> list[Reply]:
        user_message = user_message.replace('<code>', '').replace('</code>', '')
        user_message = user_message.replace('<tg-spoiler>', '').replace('</tg-spoiler>', '')
        if "render_screen_" in user_message:
            return self.on_render_screen(chat_id, user_message)

        user = self.users_orm.get_user_by_id(chat_id)
        if user['lang_code'] is None:
            return [self.on_start_command(chat_id)]

        lang = self._get_user_lang(user['lang_code'])

        if "start_game" in user_message:
            return [self._on_start_game(lang, user, user_message)]
        if "formula_updated" in user_message:
            return [self._on_formula_updated(lang, user)]
        if "set_difficulty:" in user_message:
            return [self._on_set_difficulty(lang, user, user_message)]
        if "reviewed_at:" in user_message:
            return [self._on_reviewed(lang, user, user_message)]
        if "sleep_config:" in user_message:
            return [self._on_sleep_config(lang, user, user_message)]
        if "achievements_button" in user_message:
            return [self._render_single_message(chat_id, lang.achievements_link_regenerated, None, {
                "text": lang.view_badges_button,
                "url": self._render_board_url(chat_id, lang, BadgesManager(user['difficulty'], user['badges_serialized']), Counter(user['active_game_counter_state']).get_total_seconds())
            })]
        if "regenerate_shared_key_uuid" in user_message:
            user['shared_key_uuid'] = str(uuid.uuid4())
            self.users_orm.upsert_user(user)
            return [self._render_single_message(chat_id, "Shared key UUID regenerated", None, None)]
        if "delete_data_confirmed" in user_message:
            self.users_orm.remove_user(chat_id)
            return [self._render_single_message(chat_id, lang.data_deleted, None, None)]

        if user["active_game_counter_state"] is None:
            return [self._render_single_message(chat_id, lang.start_game_prompt, None, self._render_start_game_button(lang, user))]
        return [self._render_single_message(chat_id, "Invalid data", None, None)]

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

    def _on_start_game(self, lang: Lang, user: User, user_message) -> Reply:
        next_review_prompt_times = user_message.split("start_game;next_review:")[1].split(",,")
        self._restart_user_game(user)

        badge_message, badge_button = self._handle_badge_event(user, 'on_game_started')
        return self._render_game_started_screen(next_review_prompt_times[user['difficulty']], user['difficulty'], lang, user['user_id'], badge_message, badge_button)

    def _on_formula_updated(self, lang: Lang, user: User) -> Reply:
        maybe_badge_msg, maybe_badge_button = self._handle_badge_event(user, 'on_formula_updated')
        return self._render_single_message(user['user_id'], lang.formula_changed, maybe_badge_msg, maybe_badge_button)

    def _on_set_difficulty(self, lang: Lang, user: User, user_message: str) -> Reply:
        if user['active_game_counter_state'] is None:
            return self._render_start_game_screen(lang, user)

        new_difficulty = 0
        next_review_at = 0
        try :
            split = user_message.split("set_difficulty:")[1]
            new_difficulty = int(split.split(';')[0])
            next_reviews = split.split(';')[1].split('next_review:')[1].split(',,')
            next_review_at = next_reviews[new_difficulty]
        except:
            return self._render_single_message(user['user_id'], "Cannot parse input", None, None)
        if new_difficulty < 0 or new_difficulty >= len(lang.difficulties):
            return self._render_single_message(user['user_id'], "Invalid difficulty level", None, None)

        old_difficulty = user['difficulty']
        if old_difficulty is None:
            old_difficulty = 0

        is_resumed = self._maybe_resume(user)

        user['difficulty'] = new_difficulty
        self._restart_user_game(user)

        self.users_orm.upsert_user(user)

        return self._render_difficulty_changed(user['user_id'], lang, old_difficulty, new_difficulty, next_review_at, is_resumed)

    def _restart_user_game(self, user: User):
        user['review_counter_state'] = Counter('').resume().serialize()

        self._reset_user_next_prompt(user)

        user['active_game_counter_state'] = Counter('').resume().serialize()
        user['paused_counter_state'] = None

        user['counters_history_serialized'] = None
        user['badges_serialized'] = ""
        self.users_orm.upsert_user(user)

    def on_review_command(self, chat_id) -> Reply:
        user = self.users_orm.get_user_by_id(chat_id)
        if user['lang_code'] is None:
            return self.on_start_command(chat_id)
        lang = self._get_user_lang(user['lang_code'])

        if user['active_game_counter_state'] is None:
            return self._render_start_game_screen(lang, user)

        counter_active_game = Counter(user['active_game_counter_state'])
        counter_review_state = Counter(user['review_counter_state'])

        since_last_review_secs = None
        if abs(counter_active_game.get_total_seconds() - counter_review_state.get_total_seconds()) > 60:
            since_last_review_secs = int(Counter(user['review_counter_state']).get_total_seconds())

        is_paused = user['paused_counter_state'] is not None

        return self._render_review_screen(lang, user['user_id'], is_paused, since_last_review_secs)


    def _on_reviewed(self, lang: Lang, user: User, user_message: str):
        if user['active_game_counter_state'] is None:
            return self._render_start_game_screen(lang, user)

        now_timestamp = time.time()
        next_review = None
        user_timestamp = 0
        try:
            user_timestamp = int(user_message.split('reviewed_at:')[1].split(';')[0])
            next_review = user_message.split('next_review:')[1].split(',,')[user['difficulty']]
        except:
            return self._render_single_message(user['user_id'], "Cannot parse input", None, None)
        delta = abs(now_timestamp - user_timestamp)
        if delta > 60:
            return {
                'to_chat_id': user['user_id'],
                'message': lang.review_command_timeout,
                'buttons': [self._render_review_button(lang)],
                'menu_commands': []
            }

        is_resumed = self._maybe_resume(user)

        since_last_review_secs = int(Counter(user['review_counter_state']).get_total_seconds())

        is_cooldown = (since_last_review_secs < 5*60) and user['counters_history_serialized'] is not None

        self._record_counter_time(user, REVIEW_COUNTER_HISTORY_NAME, user['review_counter_state'])
        user['review_counter_state'] = Counter('').resume().serialize()

        self._reset_user_next_prompt(user)
        self.users_orm.upsert_user(user)

        autopause_manager = AutopauseManager(user['autopause_config_serialized'])

        if is_cooldown:
            return self._render_review_command_success(lang.cooldown_msg, None, next_review,
                                                       lang=lang,
                                                       chat_id=user['user_id'], is_resumed=is_resumed,
                                                       is_autopause_enabled=autopause_manager.is_enabled())

        else:
            maybe_badge_msg, maybe_badge_button =  self._handle_badge_event(user, 'on_review')
            return self._render_review_command_success(maybe_badge_msg, maybe_badge_button, next_review,
                                                       lang=lang,
                                                       chat_id=user['user_id'], is_resumed=is_resumed,
                                                       is_autopause_enabled=autopause_manager.is_enabled())


    def _calculate_active_play_time_seconds(self, user: User) -> int:
        counter = Counter(user['active_game_counter_state'])
        return int(counter.get_total_seconds())

    def _render_start_game_screen(self, lang: Lang, user: User) -> Reply:
        return {
            'to_chat_id': user['user_id'],
            'message': lang.help_command_text.format(difficulty=lang.difficulties[user['difficulty']]),
            'buttons': [self._render_start_game_button(lang, user)],
            'menu_commands': self._render_menu_commands(lang),
            'image': None
        }

    def _render_start_game_button(self, lang: Lang, user: User) -> Button:
        return {
            'text': lang.help_command_start_playing_button,
            'url': self.frontend_base_url + f'?env={self.env}&lang_code={lang.lang_code}&new_game=1&{NEXT_REVIEW_PROMPT_MINUTES_QUERY_PARAM}&shared_key_uuid={user["shared_key_uuid"]}'
        }

    def on_data_command(self, chat_id) -> [Reply]:
        user = self.users_orm.get_user_by_id(chat_id)
        if user['lang_code'] is None:
            return self.on_start_command(chat_id)
        lang = self._get_user_lang(user['lang_code'])

        data = [" - shared_key_uuid: " + user['shared_key_uuid']]
        data_short = [" - shared_key_uuid: " + user['shared_key_uuid']]
        for key in user:
            value = str(user[key])
            value_short = value
            if len(value) > 256:
                value_short = value[:256] + "..."
            if key != 'shared_key_uuid':
                data.append(f" - {key}: {value}")
                data_short.append(f" - {key}: {value_short}")

        return self._render_delete_data_screen(lang, chat_id, data_short, data)

    def on_feedback_command(self, chat_id) -> [Reply]:
        user = self.users_orm.get_user_by_id(chat_id)
        if user['lang_code'] is None:
            return self.on_start_command(chat_id)
        lang = self._get_user_lang(user['lang_code'])

        return self._render_single_message(chat_id, lang.feedback_text, None, None)

    def on_pause_command(self, chat_id) -> Reply:
        user = self.users_orm.get_user_by_id(chat_id)
        if user['lang_code'] is None:
            return self.on_start_command(chat_id)
        lang = self._get_user_lang(user['lang_code'])

        if user['active_game_counter_state'] is None:
            return self._render_start_game_screen(lang, user)

        if user['paused_counter_state'] is None:
            self._pause_user(user)

            self.users_orm.upsert_user(user)

            return self._render_on_pause(lang, user['user_id'])
        else:
            return self._render_already_on_pause(lang, chat_id)

    def on_sleep_command(self, chat_id) -> Reply:
        user = self.users_orm.get_user_by_id(chat_id)
        if user['lang_code'] is None:
            return self.on_start_command(chat_id)
        lang = self._get_user_lang(user['lang_code'])

        autopause_manager = AutopauseManager(user['autopause_config_serialized'])
        return self._render_single_message(
            chat_id,
            lang.sleep_command_text.format(
                is_enabled='🟢' if autopause_manager.is_enabled() else '⚪️',
                bed_time=autopause_manager.get_bed_time() if autopause_manager.get_bed_time() is not None else 'N/A',
                wakeup_time=autopause_manager.get_wakep_time() if autopause_manager.get_wakep_time() is not None else 'N/A',
            ), None, {
                "text": lang.sleep_command_button,
                "url": self.frontend_base_url + f'?env={self.env}'
                                                f'&lang_code={lang.lang_code}'
                                                f'&sleep=1'
                                                f'&enabled={"true" if autopause_manager.is_enabled() else "false"}'
                                                f'&bed_time={"22:00" if autopause_manager.get_bed_time() is None else autopause_manager.get_bed_time()}'
                                                f'&wakeup_time={"06:00" if autopause_manager.get_wakep_time() is None else autopause_manager.get_wakep_time()}'
            })

    def on_stats_command(self, chat_id) -> Reply:
        user = self.users_orm.get_user_by_id(chat_id)
        if user['lang_code'] is None:
            return self.on_start_command(chat_id)
        lang = self._get_user_lang(user['lang_code'])

        if user['active_game_counter_state'] is None:
            return self._render_start_game_screen(lang, user)

        since_last_review_secs = int(Counter(user['review_counter_state']).get_total_seconds())

        till_next_prompt_time = 0
        if user['next_prompt_time'] is not None:
            till_next_prompt_time = max(int((user['next_prompt_time'] - now_utc()).total_seconds()), 0)

        paused_at = None
        if user['paused_counter_state'] is not None:
            paused_at = now_utc() - datetime.timedelta(seconds=Counter(user['paused_counter_state']).get_total_seconds())

        fname = GraphRenderer().render_graph(lang, get_timer_recs_from_history(
            user['counters_history_serialized']), PROMPT_MINUTES[user['difficulty']]
                                             , lang.difficulties[user['difficulty']],
                                             paused_at)

        return self._render_stats(lang, BadgesManager(user['difficulty'], user['badges_serialized']), user['user_id'], user['difficulty'], self._calculate_active_play_time_seconds(user),
                                  user['paused_counter_state'] is not None, since_last_review_secs, till_next_prompt_time, fname)

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
        quota = 20
        for difficulty in range(0, 5):
            if quota <= 0:
                break
            users = self.users_orm.get_some_users_for_prompt(quota, difficulty)
            for user in users:
                quota -= 3
                if user['next_prompt_type'] == NEXT_PROMPT_TYPE_PENALTY:
                    replies += [self._process_penalty_prompt(user)]
                else:
                    replies += [self._process_reminder_prompt(user)]

        autopaused_events = self.users_orm.get_some_next_autopause_events(quota)
        for user in autopaused_events:
            replies += self._process_autopause(user)

        return replies

    def _process_autopause(self, user: User) -> [Reply]:
        autopause_manager = AutopauseManager(user['autopause_config_serialized'])
        user['next_autopause_event_time'] = datetime.datetime.fromtimestamp(autopause_manager.get_next_autopause_event_at_timestamp() + 1, tz=datetime.timezone.utc)
        self.users_orm.upsert_user(user)

        if autopause_manager.is_in_interval(now_utc().timestamp()):
            if user['paused_counter_state'] is None:
                self._pause_user(user)
                self.users_orm.upsert_user(user)

                lang = self._get_user_lang(user['lang_code'])
                return [self._render_single_message(user['user_id'], lang.autopause_on_msg.format(until_time=autopause_manager.get_wakep_time()), None, None)]
            else:
                return []
        else:
            is_resumed = self._maybe_resume(user)
            self.users_orm.upsert_user(user)

            if is_resumed:
                lang = self._get_user_lang(user['lang_code'])
                return [self._render_single_message(user['user_id'], lang.autopause_resumed_msg, None, self._render_review_button(lang))]
            else:
                return []

    def _process_penalty_prompt(self, user: User) -> Reply:
        self._reset_user_next_prompt(user)
        self.users_orm.upsert_user(user)

        maybe_badge_msg, maybe_badge_button = self._handle_badge_event(user, 'on_penalty')

        lang = self._get_user_lang(user['lang_code'])
        autopause_manager = AutopauseManager(user['autopause_config_serialized'])
        return self._render_penalty(lang, maybe_badge_msg, maybe_badge_button, user['user_id'], autopause_manager.is_enabled())

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

    def _render_game_started_screen(self, next_review: str, difficulty: int, lang: Lang, chat_id: int, maybe_badge_message: Optional[str], maybe_badge_button: Optional[Button]) -> Reply:
        difficulty = lang.difficulties[difficulty]
        buttons = [self._render_review_button(lang)]
        if maybe_badge_button is not None:
            buttons.append(maybe_badge_button)
        return {
            'to_chat_id': chat_id,
            'message': lang.game_started.format(next_review=next_review, difficulty=difficulty
                                                , maybe_achievement=("\n" + maybe_badge_message + "\n") if maybe_badge_message is not None else ""),
            'buttons': buttons,
            'menu_commands': [],
            'image': None
        }

    def _render_review_command_success(self, maybe_achievement_msg: Optional[str], maybe_achievement_button: Optional[Button], next_review: str, lang: Lang, chat_id: int, is_resumed: bool, is_autopause_enabled: bool) -> Reply:
        message = lang.review_command_success_text.format(next_review=next_review, time=time,
                                                          pause_prompt=self._render_pause_prompt(lang, is_autopause_enabled),
                                                          maybe_achievement=("\n" + maybe_achievement_msg + "\n") if maybe_achievement_msg is not None else "")
        buttons = [self._render_review_button(lang)]
        if maybe_achievement_button is not None:
            buttons.append(maybe_achievement_button)
        if is_resumed:
            message = lang.resumed + "\n" + message
        return {
            'to_chat_id': chat_id,
            'message': message,
            'buttons': buttons,
            'menu_commands': self._render_menu_commands(lang),
            'image': None
        }

    def on_render_screen(self, chat_id, user_message) -> list[Reply]:
        langs = LangProvider.get_available_languages()

        if user_message == "render_screen_0":
            return [self._render_list_of_langs(chat_id, langs)]

        if user_message == "render_screen_1":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_game_started_screen("10:00", 1, lang, chat_id, None, None)]
                ret = ret + [self._render_game_started_screen("10:00", 1, lang, chat_id, lang.badge_new, {
                    "text": lang.view_badges_button,
                    "url": "https://google.com"
                })]
            return ret

        if user_message == "render_screen_2":
            ret = []
            for is_resumed in [True, False]:
                for lang_code, lang in langs.items():
                    ret = ret + [self._render_review_command_success(None, None, "10:00", lang, chat_id, is_resumed, True)]
                    ret = ret + [self._render_review_command_success(lang.badge_new, {
                        "text": lang.view_badges_button,
                        "url": "https://google.com"
                    }, "10:00", lang, chat_id, is_resumed, False)]
                    ret = ret + [self._render_review_command_success(lang.kicking_out_grumpy_cat, {
                        "text": lang.view_badges_button,
                        "url": "https://google.com"
                    }, "10:00", lang, chat_id, is_resumed, True)]
                    ret = ret + [self._render_review_command_success(lang.grumpy_cat_kicked_out + "\n" + lang.achievements_unblocked, {
                        "text": lang.view_badges_button,
                        "url": "https://google.com"
                    }, "10:00", lang, chat_id, is_resumed, False)]
                    ret = ret + [self._render_review_command_success(lang.cooldown_msg, None, "10:00", lang, chat_id, is_resumed, True)]
            return ret

        if user_message == "render_screen_3":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_penalty(lang, None, None, chat_id, True)]
                ret = ret + [self._render_penalty(lang, lang.badge_unhappy_cat, {
                    "text": lang.view_badges_button,
                    "url": "https://google.com"
                }, chat_id, False)]
            return ret

        if user_message == "render_screen_4":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_difficulty_buttons(lang, chat_id, 2)]
            return ret

        if user_message == "render_screen_5":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_difficulty_changed(chat_id, lang, 0, 1, "10:00", False)]
                ret = ret + [self._render_difficulty_changed(chat_id, lang, 2, 3, "10:00", True)]
                ret = ret + [self._render_difficulty_changed(chat_id, lang, 3, 4, "10:00", False)]
            return ret

        if user_message == "render_screen_6":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_stats(lang, BadgesManager(0, None), chat_id, 2, 1000, False, 100, 1000, None)]
            return ret

        if user_message == "render_screen_7":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_edit_formula(lang, 'blahbah', chat_id)]
            return ret

        if user_message == "render_screen_8":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_review_screen(lang, chat_id, True, None)]
                ret = ret + [self._render_review_screen(lang, chat_id, False, None)]
                ret = ret + [self._render_review_screen(lang, chat_id, False, 123321)]
            return ret

        if user_message == "render_screen_9":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_on_pause(lang, chat_id)]
            return ret

        if user_message == "render_screen_10":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_already_on_pause(lang, chat_id)]
            return ret

        if user_message == "render_screen_11":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_delete_data_screen(lang, chat_id, [" - shared_key_uuid: blahblah"], [" - shared_key_uuid: blahblah"])]
            return ret

        if user_message == "render_screen_12":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_single_message(chat_id, lang.data_deleted, None, None)]
            return ret

        if user_message == "render_screen_13":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_single_message(chat_id, lang.formula_changed, None, None)]
                ret = ret + [self._render_single_message(chat_id, lang.formula_changed, lang.badge_new, {
                    "text": lang.view_badges_button,
                    "url": "https://google.com"
                })]
            return ret

        if user_message == "render_screen_14":
            ret = []
            for is_autopause_enabled in [True, False]:
                for lang_code, lang in langs.items():
                    ret = ret + [self._render_reminder_prompt(lang, chat_id, {
                        "text": lang.view_badges_button,
                        "url": "https://google.com"
                    }, is_autopause_enabled)]
            return ret
        return []

    def _maybe_resume(self, user: User) -> bool:
        if user['paused_counter_state']:
            pause_counter = Counter(user['paused_counter_state'])
            seconds = pause_counter.get_total_seconds()
            if user['next_prompt_time'] is not None:
                user['next_prompt_time'] = user['next_prompt_time'] + datetime.timedelta(seconds=seconds)

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
        buttons = []
        for lang_code in sorted(languages):
            lang = languages[lang_code]
            if lang_code == "en":
                buttons = [{
                    "text": lang.lang_name,
                    "data": lang_code
                }] + buttons
            else:
                buttons += [{
                    "text": lang.lang_name,
                    "data": lang_code
                }]
        return {
            'to_chat_id': chat_id,
            'message': "Select your language:",
            'buttons': buttons,
            'menu_commands': [],
            'image': None
        }

    def _render_single_message(self, chat_id, msg: str, maybe_badge_message: Optional[str], maybe_badge_button: Optional[Button]) -> Reply:
        buttons = []
        if maybe_badge_button is not None:
            buttons.append(maybe_badge_button)
        return {
            'to_chat_id': chat_id,
            'message': msg + ("\n\n" + maybe_badge_message if maybe_badge_message is not None else ""),
            'buttons': buttons,
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

    def _render_stats(self, lang, badges_manager, chat_id, difficulty, active_play_time_seconds, is_paused, since_last_review_secs, till_next_prompt_time, fname) -> Reply:
        return {
            'to_chat_id': chat_id,
            'message': lang.stats_command.format(
                level=badges_manager.get_level() + 2 if badges_manager.is_level_completed() else badges_manager.get_level() + 1,
                difficulty=lang.difficulties[difficulty],
                difficulty_details=str(difficulty + 1) + "/" + str(len(lang.difficulties)),
                time=self._format_time_minutes(lang, active_play_time_seconds),
                paused="⚪" if not is_paused else "🟢",
                cooldown=self._format_time_seconds(lang, 5*60 - since_last_review_secs if since_last_review_secs < 5*60 else 0),
                punishment=self._format_time_minutes(lang, till_next_prompt_time, skip_zeros=True)
            ),
            'buttons': [{
                'text': lang.view_badges_button,
                'url': self._render_board_url(chat_id, lang, badges_manager, active_play_time_seconds)
            }],
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
            'menu_commands': self._render_menu_commands(lang),
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

    def _render_delete_data_screen(self, lang, chat_id, data_short, data) -> [Reply]:
        random_fname = 'tmp_user_data_' + str(np.random.randint(100000, 900000)) + '.txt'
        # write message to file
        with open(random_fname, 'w') as f:
            f.write("\n\n".join(data))

        with open(random_fname, 'rb') as file:
            return [
                {
                    'to_chat_id': chat_id,
                    'message': lang.data_view + "\n\n<code>" + "\n\n".join(data_short) + "</code>",
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
                    'menu_commands': self._render_menu_commands(lang),
                    'image': random_fname
                }]


    def _render_penalty(self, lang: Lang, maybe_badge_message: Optional[str], maybe_badge_button: Optional[Button], chat_id: int, is_autopause_enabled: bool) -> Reply:

        buttons = [self._render_review_button(lang)]
        if maybe_badge_button is not None:
            buttons.append(maybe_badge_button)

        return {
            'to_chat_id': chat_id,
            'message': lang.penalty_text.format(
                maybe_achievement=("\n" + maybe_badge_message + "\n") if maybe_badge_message is not None else "",
                pause_prompt=self._render_pause_prompt(lang, is_autopause_enabled)
            ),
            'buttons': buttons,
            'menu_commands': [],
            'image': None
        }

    def _process_reminder_prompt(self, user: User):
        lang = self._get_user_lang(user['lang_code'])

        user['next_prompt_type'] = NEXT_PROMPT_TYPE_PENALTY
        user['next_prompt_time'] = now_utc() + datetime.timedelta(minutes=REVIEW_INTERVAL_MINS)

        self.users_orm.upsert_user(user)

        _, maybe_badge_button = self._handle_badge_event(user, 'on_prompt')

        autopause_manager = AutopauseManager(user['autopause_config_serialized'])

        return self._render_reminder_prompt(lang, user['user_id'], maybe_badge_button, autopause_manager.is_enabled())

    def _reset_user_next_prompt(self, user: User):
        difficulty = user['difficulty']
        penalty_minutes = PROMPT_MINUTES[difficulty]

        user['next_prompt_time'] = now_utc() + datetime.timedelta(minutes=penalty_minutes)
        user['next_prompt_type'] = NEXT_PROMPT_TYPE_PENALTY
        if HAS_REMINDER[difficulty]:
            user['next_prompt_time'] -= datetime.timedelta(minutes=REVIEW_INTERVAL_MINS)
            user['next_prompt_type'] = NEXT_PROMPT_TYPE_REMINDER

    def _render_reminder_prompt(self, lang, chat_id, maybe_badge_button: Button, is_autopause_enabled):
        buttons = [self._render_review_button(lang)]
        if maybe_badge_button is not None:
            buttons.append(maybe_badge_button)
        return {
            'to_chat_id': chat_id,
            'message': lang.reminder_text.format(pause_prompt=self._render_pause_prompt(lang, is_autopause_enabled)),
            'buttons': buttons,
            'menu_commands': [],
            'image': None
        }

    def _render_board_url(self, chat_id: int, lang: Lang, badges_manager: BadgesManager, active_play_time_secs) -> str:
        button_url = self.frontend_base_url.replace("index.html", "board.html")
        button_url += '?lang=' + lang.lang_code + '&env=' + self.env
        if badges_manager.get_last_badge() is not None:
            button_url += '&new_badge=' + badges_manager.get_last_badge()

        button_url += "&level=" + str(badges_manager.get_level() + 1)
        button_url += "&b1=" + serialize_board(badges_manager.get_board())

        progress = badges_manager.progress(active_play_time_secs)
        button_url += "&bp1=" + serialize_progress(progress)

        if badges_manager.is_level_completed():
            button_url += "&b2=" + serialize_board(badges_manager.get_next_level_board())
            button_url += "&bp2=" + serialize_progress(badges_manager.new_level_empty_progress())

        button_url += "&ts=" + str(int(time.time()))

        return button_url

    def _handle_badge_event(self, user, event) -> (Optional[str], Optional[Button]):
        badges_manager = BadgesManager(user['difficulty'], user['badges_serialized'])

        active_play_time_secs = self._calculate_active_play_time_seconds(user)

        badge = getattr(badges_manager, event)(active_play_time_secs)

        user['badges_serialized'] = badges_manager.serialize()
        self.users_orm.upsert_user(user)

        lang = self._get_user_lang(user['lang_code'])
        button_url = self._render_board_url(user['user_id'], lang, badges_manager, active_play_time_secs)

        view_achievements_button = {
            'text': lang.view_badges_button,
            'url': button_url
        }

        if badge == "c0_removed":
            if badges_manager.count_active_grumpy_cats_on_board() == 0:
                return lang.grumpy_cat_kicked_out + "\n" + lang.achievements_unblocked, view_achievements_button
            return lang.grumpy_cat_kicked_out + "\n" + lang.remained_grumpy_cats.format(count=badges_manager.count_active_grumpy_cats_on_board()), view_achievements_button

        if badge is None:
            if badges_manager.count_active_grumpy_cats_on_board() > 0:
                return lang.kicking_out_grumpy_cat if event == 'on_review' else lang.locked_achievements, view_achievements_button

            return None, None if event == 'on_formula_updated' else view_achievements_button

        return lang.badge_unhappy_cat if badge == "c0" else lang.badge_new, view_achievements_button

    def _pause_user(self, user: User):
        paused_counter = Counter("")
        paused_counter.resume()
        user['paused_counter_state'] = paused_counter.serialize()

        active_counter = Counter(user['active_game_counter_state'])
        active_counter.pause()
        user['active_game_counter_state'] = active_counter.serialize()

        review_counter = Counter(user['review_counter_state'])
        review_counter.pause()
        user['review_counter_state'] = review_counter.serialize()

    def _render_pause_prompt(self, lang, is_autopause_enabled):
        pause_prompt = lang.pause_prompt
        if not is_autopause_enabled:
            pause_prompt += "\n\n" + lang.autopause_prompt
        return pause_prompt

    def _on_sleep_config(self, lang: Lang, user: User, user_message: str) -> Reply:
        msg_tail = user_message.split('sleep_config:')[1]
        split = msg_tail.split(',,')
        enabled = split[0] == '1' or split[0].lower() == 'true'
        user_tz = split[1]
        user_tz_offset_secs = int(split[2])
        bed_time = split[3]
        wakeup_time = split[4]

        autopause_manager = AutopauseManager(user['autopause_config_serialized'])
        autopause_manager.update(enabled, user_tz, user_tz_offset_secs, bed_time, wakeup_time)
        user['autopause_config_serialized'] = autopause_manager.serialize()
        if autopause_manager.is_enabled():
            user['next_autopause_event_time'] = datetime.datetime.fromtimestamp(autopause_manager.get_next_autopause_event_at_timestamp() + 1, tz=datetime.timezone.utc)
        else:
            user['next_autopause_event_time'] = None
        self.users_orm.upsert_user(user)

        return self._render_single_message(user['user_id'], lang.sleep_config_updated.format(
            is_enabled='🟢' if enabled else '⚪️',
            bed_time=autopause_manager.get_bed_time() if autopause_manager.get_bed_time() is not None else 'N/A',
            wakeup_time=autopause_manager.get_wakep_time() if autopause_manager.get_wakep_time() is not None else 'N/A'
        ), None, None)

    def on_settings_command(self, chat_id) -> Reply:
        user = self.users_orm.get_user_by_id(chat_id)
        if user['lang_code'] is None:
            return self.on_start_command(chat_id)
        lang = self._get_user_lang(user['lang_code'])

        return self._render_settings_screen(chat_id, lang)

    def _render_menu_commands(self, lang):
        return [
            ["review", lang.menu_review],
            ["pause", lang.menu_pause],
            ["formula", lang.menu_formula],
            ["stats", lang.menu_stats],
            ["settings", lang.menu_settings]
        ]

    def _render_settings_screen(self, chat_id, lang) -> Reply:
        sub_commands = [
            { "data": "sleep", "text": lang.menu_sleep },
            { "data": "difficulty", "text": lang.menu_difficulty },
            { "data": "data", "text": lang.menu_data },
            { "data": "feedback", "text": lang.menu_feedback }
        ]

        return {
            'to_chat_id': chat_id,
            'message': lang.settings_title,
            'buttons': sub_commands,
            'menu_commands': [],
            'image': None
        }

















