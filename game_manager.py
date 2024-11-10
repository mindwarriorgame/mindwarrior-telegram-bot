import datetime
import uuid
from typing import TypedDict, Optional
import time

from badges_manager import BadgesManager
from board_serializer import serialize_board, serialize_progress
from counter import Counter
from graph_renderer import REVIEW_COUNTER_HISTORY_NAME, PAUSED_COUNTER_HISTORY_NAME, GraphRenderer
from history import add_timer_rec_to_history, get_timer_recs_from_history
from lang_provider import LangProvider, Lang, en, ru
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

HAS_REMINDER = [True, True, True, False, False]

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
            return self._render_single_message(chat_id, "Invalid language code. Try again (/start)", None, None)

    def _get_user_lang(self, lang_code: str) -> Lang:
        languages = LangProvider.get_available_languages()
        lang = languages[lang_code]
        if lang is None:
            raise Exception(f"Unsupported language code: {lang_code}")
        return lang

    def on_data_provided(self, chat_id: int, user_message: str) -> list[Reply]:
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
        if "achievements_button" in user_message:
            return [self._render_single_message(chat_id, lang.achievements_link_regenerated, None, {
                "text": lang.view_badges_button,
                "url": self._render_board_url(lang, None, BadgesManager(user['difficulty'], user['badges_serialized']), Counter(user['active_game_counter_state']).get_total_seconds())
            })]
        if "regenerate_shared_key_uuid" in user_message:
            user['shared_key_uuid'] = str(uuid.uuid4())
            self.users_orm.upsert_user(user)
            return [self._render_single_message(chat_id, "Shared key UUID regenerated", None, None)]
        if "delete_data_confirmed" in user_message:
            self.users_orm.remove_user(chat_id)
            return [self._render_single_message(chat_id, lang.data_deleted, None, None)]

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
            return self._render_start_game_button(lang, user)

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

        is_resumed = self._maybe_resume(user, lang)

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
            return self._render_start_game_button(lang, user)

        counter_active_game = Counter(user['active_game_counter_state'])
        counter_review_state = Counter(user['review_counter_state'])

        since_last_review_secs = None
        if abs(counter_active_game.get_total_seconds() - counter_review_state.get_total_seconds()) > 60:
            since_last_review_secs = int(Counter(user['review_counter_state']).get_total_seconds())

        is_paused = user['paused_counter_state'] is not None

        return self._render_review_screen(lang, user['user_id'], is_paused, since_last_review_secs)


    def _on_reviewed(self, lang: Lang, user: User, user_message: str):
        if user['active_game_counter_state'] is None:
            return self._render_start_game_button(lang, user)

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

        is_resumed = self._maybe_resume(user, lang)

        since_last_review_secs = int(Counter(user['review_counter_state']).get_total_seconds())

        is_cooldown = (since_last_review_secs < 5*60)

        self._record_counter_time(user, REVIEW_COUNTER_HISTORY_NAME, user['review_counter_state'])
        user['review_counter_state'] = Counter('').resume().serialize()

        self._reset_user_next_prompt(user)
        self.users_orm.upsert_user(user)

        if is_cooldown:
            return self._render_review_command_success(lang.cooldown_msg, None, next_review,
                                                       lang=lang,
                                                       chat_id=user['user_id'], is_resumed=is_resumed)

        else:
            maybe_badge_msg, maybe_badge_button =  self._handle_badge_event(user, 'on_review')
            return self._render_review_command_success(maybe_badge_msg, maybe_badge_button, next_review,
                                                       lang=lang,
                                                       chat_id=user['user_id'], is_resumed=is_resumed)


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
        for difficulty in range(0, 5):
            users = self.users_orm.get_some_users_for_prompt(20, difficulty)
            for user in users:
                if user['next_prompt_type'] == NEXT_PROMPT_TYPE_PENALTY:
                    replies += [self._process_penalty_prompt(user)]
                else:
                    replies += [self._process_reminder_prompt(user)]

        return replies

    def _process_penalty_prompt(self, user: User) -> Reply:
        self._reset_user_next_prompt(user)
        self.users_orm.upsert_user(user)

        maybe_badge_msg, maybe_badge_button = self._handle_badge_event(user, 'on_penalty')

        lang = self._get_user_lang(user['lang_code'])
        return self._render_penalty(lang, maybe_badge_msg, maybe_badge_button, user['user_id'])

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

    def _render_review_command_success(self, maybe_achievement_msg: Optional[str], maybe_achievement_button: Optional[Button], next_review: str, lang: Lang, chat_id: int, is_resumed: bool) -> Reply:
        message = lang.review_command_success_text.format(next_review=next_review, time=time,
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
            'menu_commands': [],
            'image': None
        }

    def on_render_screen(self, chat_id, user_message) -> list[Reply]:
        langs = LangProvider.get_available_languages()
        langs = {
            'en': en,
            'ru': ru
        }

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
                    ret = ret + [self._render_review_command_success(None, None, "10:00", lang, chat_id, is_resumed)]
                    ret = ret + [self._render_review_command_success(lang.badge_new, {
                        "text": lang.view_badges_button,
                        "url": "https://google.com"
                    }, "10:00", lang, chat_id, is_resumed)]
                    ret = ret + [self._render_review_command_success(lang.kicking_out_grumpy_cat, {
                        "text": lang.view_badges_button,
                        "url": "https://google.com"
                    }, "10:00", lang, chat_id, is_resumed)]
                    ret = ret + [self._render_review_command_success(lang.grumpy_cat_kicked_out + "\n" + lang.achievements_unblocked, {
                        "text": lang.view_badges_button,
                        "url": "https://google.com"
                    }, "10:00", lang, chat_id, is_resumed)]
                    ret = ret + [self._render_review_command_success(lang.cooldown_msg, None, "10:00", lang, chat_id, is_resumed)]
            return ret

        if user_message == "render_screen_3":
            ret = []
            for lang_code, lang in langs.items():
                ret = ret + [self._render_penalty(lang, None, None, chat_id)]
                ret = ret + [self._render_penalty(lang, lang.badge_unhappy_cat, {
                    "text": lang.view_badges_button,
                    "url": "https://google.com"
                }, chat_id)]
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
                ret = ret + [self._render_delete_data_screen(lang, chat_id, [" - shared_key_uuid: blahblah"])]
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
            for lang_code, lang in langs.items():
                ret = ret + [self._render_reminder_prompt(lang, chat_id, {
                    "text": lang.view_badges_button,
                    "url": "https://google.com"
                })]
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
            if lang_code == "en":
                message = new_lang_msg + "\n\n" + message
            else:
                message += new_lang_msg + "\n\n"
        return self._render_single_message(chat_id, message, None, None)

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
                'url': self._render_board_url(lang, None, badges_manager, active_play_time_seconds)
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

    def _render_penalty(self, lang: Lang, maybe_badge_msg: Optional[str], maybe_badge_button: Optional[Button], chat_id: int) -> Reply:

        buttons = [self._render_review_button(lang)]
        if maybe_badge_button is not None:
            buttons.append(maybe_badge_button)

        return {
            'to_chat_id': chat_id,
            'message': lang.penalty_text + (("\n\n" + maybe_badge_msg) if maybe_badge_msg is not None else ""),
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

        return self._render_reminder_prompt(lang, user['user_id'], maybe_badge_button)

    def _reset_user_next_prompt(self, user: User):
        difficulty = user['difficulty']
        penalty_minutes = PROMPT_MINUTES[difficulty]

        user['next_prompt_time'] = now_utc() + datetime.timedelta(minutes=penalty_minutes)
        user['next_prompt_type'] = NEXT_PROMPT_TYPE_PENALTY
        if HAS_REMINDER[difficulty]:
            user['next_prompt_time'] -= datetime.timedelta(minutes=REVIEW_INTERVAL_MINS)
            user['next_prompt_type'] = NEXT_PROMPT_TYPE_REMINDER

    def _render_reminder_prompt(self, lang, chat_id, maybe_badge_button: Button):
        buttons = [self._render_review_button(lang)]
        if maybe_badge_button is not None:
            buttons.append(maybe_badge_button)
        return {
            'to_chat_id': chat_id,
            'message': lang.reminder_text,
            'buttons': [buttons],
            'menu_commands': [],
            'image': None
        }

    def _render_board_url(self, lang: Lang, badge: Optional[str], badges_manager: BadgesManager, active_play_time_secs) -> str:
        button_url = self.frontend_base_url.replace("index.html", "board.html")
        button_url += '?lang=' + lang.lang_code + '&env=' + self.env
        if badge is not None:
            button_url += '&new_badge=' + badge

        button_url += "&level=" + str(badges_manager.get_level() + 1)
        button_url += "&b1=" + serialize_board(badges_manager.get_board())
        button_url += "&bp1=" + serialize_progress(badges_manager.progress(active_play_time_secs))

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
        button_url = self._render_board_url(lang, badge, badges_manager, active_play_time_secs)

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

            return None, view_achievements_button

        return lang.badge_unhappy_cat if badge == "c0" else lang.badge_new, view_achievements_button


















