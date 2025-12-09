import copy
import datetime
import uuid
from typing import Tuple, TypedDict, Optional, NotRequired, cast
import time

import numpy as np

from autopause_manager import AutopauseManager
from badges_manager import BadgesManager
from board_serializer import serialize_board, serialize_progress
from counter import Counter
from frontend_base_url_extractor import get_frontend_base_urls
from graph_renderer import REVIEW_COUNTER_HISTORY_NAME, PAUSED_COUNTER_HISTORY_NAME, GraphRenderer
from history import add_timer_rec_to_history, get_timer_recs_from_history
from lang_provider import LangProvider, Lang, en, ru
from users_orm import UsersOrm, User

SET_SERVER_PREFIX = "set_server:"

class Button(TypedDict):
    text: str
    data: NotRequired[str]
    url: NotRequired[str]

class Reply(TypedDict):
    to_chat_id: int
    message: str
    buttons: list[Button]
    menu_commands: list[Tuple[str, str]]
    image: Optional[str]

REVIEW_INTERVAL_MINS = 15

PROMPT_MINUTES = [60*6, 60*3, 60 + 30, 60, 45]

PRICE_DIAMONDS = [10, 20, 30, 40, 50, 60]

HAS_REMINDER = [True, True, True, False, False]

NEXT_REVIEW_PROMPT_MINUTES_QUERY_PARAM  = 'next_review_prompt_minutes=' + ",".join([str(PROMPT_MINUTES[idx]) for idx in range(0, len(PROMPT_MINUTES))])

NEXT_PROMPT_TYPE_REMINDER = "reminder"
NEXT_PROMPT_TYPE_PENALTY = "penalty"

# Too much effort to keep it in the Db, and too low value. Let's do in-memory instead
LAST_PROGRESS_CACHE = {}

def now_utc() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.timezone.utc)

class GameManager:
    def __init__(self, user: User, env):
        self.env = env
        self.user = user

        lang_code = self.user['lang_code']
        if lang_code is None:
            lang_code = 'en'
        languages = LangProvider.get_available_languages()
        self.lang = languages[lang_code]
        if self.lang is None:
            raise Exception(f"Unsupported language code: {lang_code}")

    def on_start_command(self) -> Reply:
        return self._render_list_of_langs()

    def on_lang_input(self, user_message: str) -> Reply:
        lang_code = user_message[1:] if user_message.startswith("/") else user_message
        languages = LangProvider.get_available_languages()
        if lang_code in languages:
            self.user['lang_code'] = lang_code
            self.lang = languages[lang_code]
            if lang_code == 'ru':
                # Apparently Russian government is blocking netlify :(
                # TODO: add ability to select servers in settings
                # TODO: add backend to ru.mindwarriorgame as well 
                self.user['frontend_base_url_override'] = "https://ru.mindwarriorgame.org/miniapp-frontend/index.html"
            return self._render_start_game_screen()
        else:
            return self._render_single_message("Invalid language code. Try again (/start)", None, None)

    def on_data_provided(self, user_message: str) -> list[Reply]:
        user_message = user_message.replace('<code>', '').replace('</code>', '')
        user_message = user_message.replace('<tg-spoiler>', '').replace('</tg-spoiler>', '')
        if "start_game" in user_message:
            return [self._on_start_game(user_message)]
        if "formula_updated" in user_message:
            return [self._on_formula_updated()]
        if "set_difficulty:" in user_message:
            return [self._on_set_difficulty(user_message)]
        if "reviewed_at:" in user_message:
            return [self._on_reviewed(user_message)]
        if "sleep_config:" in user_message:
            return [self._on_sleep_config(user_message)]
        if "achievements_button" in user_message:
            return [self._render_single_message(self.lang.achievements_link_regenerated, None, {
                "text": self.lang.view_badges_button,
                "url": self._render_board_url()
            })]
        if "regenerate_shared_key_uuid" in user_message:
            self.user['shared_key_uuid'] = str(uuid.uuid4())
            return [self._render_single_message("Shared key UUID regenerated", None, None)]
        if "delete_data_confirmed" in user_message:
            ret = [self._render_single_message(self.lang.data_deleted, None, None)]
            self.user['user_id'] = -1
            return ret
        
        if "stash" in user_message:
            return [self.on_stash()]
        
        if "pop" in user_message:
            return [self.on_pop()]

        if self.user["active_game_counter_state"] is None:
            return [self._render_single_message(self.lang.start_game_prompt, None, self._render_start_game_button())]
        return [self._render_single_message("Invalid data", None, None)]
    
    def on_stash(self) -> Reply:
        if self.user['active_game_counter_state'] is None:
            return self._render_single_message("Cannot stash inactive user", None, None)
        
        user_orm2 = UsersOrm("mindwarrior_stash.db")
        stashed_user = user_orm2.get_user_by_id(self.user['user_id'])
        if stashed_user.get('active_game_counter_state') is not None:
            return self._render_single_message("Already stashed", None, None)
        
        user_orm2.upsert_user(self.user)
        return self._render_single_message("Stashed!", None, None)
    
    def on_pop(self) -> Reply:
        user_orm2 = UsersOrm("mindwarrior_stash.db")
        stashed_user = user_orm2.get_user_by_id(self.user['user_id'])
        if stashed_user.get('active_game_counter_state') is None:
            return self._render_single_message("No active stash user found", None, None)
        for key in User.__annotations__.keys():
            self.user[key] = stashed_user[key]
        user_orm2.remove_user(stashed_user['user_id'])
        return self._render_single_message("User is restored", None, None)

    
    def change_server_command(self) -> Reply:
        parsed_base_urls = get_frontend_base_urls()
        buttons: list[Button] = []
        for parsed_base_url in parsed_base_urls:
            if parsed_base_url['is_enabled'] == True:
                is_current = False
                if self.user['frontend_base_url_override'] is None and parsed_base_url['id'] == 'ny':
                    is_current = True
                if self.user['frontend_base_url_override'] == parsed_base_url['base_url']:
                    is_current = True
                buttons.append({
                    "text": "Server " + parsed_base_url['id'] + (" ({c})".format(c=self.lang.change_server_current) if is_current else ""),
                    "data": SET_SERVER_PREFIX + parsed_base_url['id']
                })
        return {
            'to_chat_id': self.user['user_id'],
            "message": self.lang.change_server_descr,
            "menu_commands": [],
            "image": None,
            'buttons': buttons
        }
    
    def on_set_server_command(self, server_id: str) -> Reply:
        parsed_base_urls = get_frontend_base_urls()
        for parsed_base_url in parsed_base_urls:
            if parsed_base_url['id'] == server_id:
                self.user['frontend_base_url_override'] = parsed_base_url['base_url']
                return self._render_single_message(self.lang.change_server_done, None, None)
        return self._render_single_message("Server {server} not found".format(server_id), None, None)

    def _format_time_minutes(self, time_secs: int, skip_zeros = False) -> str:
        days = int(time_secs // 86400)
        hours = int((time_secs % 86400) // 3600)
        minutes = int((time_secs % 3600) // 60)

        ret = []
        if days > 0 or not skip_zeros:
            ret.append(f"{days}{self.lang.days_short}")
        if hours > 0 or not skip_zeros:
            ret.append(f"{hours}{self.lang.hours_short}")

        if len(ret) == 0 or minutes > 0:
            ret.append(f"{minutes}{self.lang.minutes_short}")

        return " ".join(ret)

    def _format_time_seconds(self, time_secs: int) -> str:
        minutes = int(time_secs // 60)
        seconds = int(time_secs % 60)
        return f"{minutes}{self.lang.minutes_short} {seconds}{self.lang.seconds_short}"

    def _on_start_game(self, user_message) -> Reply:
        next_review_prompt_times = user_message.split("start_game;next_review:")[1].split(",,")
        self._restart_user_game()

        badge_message, badge_button = self._handle_badge_event('on_game_started')
        return self._render_game_started_screen(next_review_prompt_times[self.user['difficulty']], badge_message, badge_button)

    def _on_formula_updated(self) -> Reply:
        maybe_badge_msg, maybe_badge_button = self._handle_badge_event('on_formula_updated')
        return self._render_single_message(self.lang.formula_changed, maybe_badge_msg, maybe_badge_button)

    def _on_set_difficulty(self, user_message: str) -> Reply:
        if self.user['active_game_counter_state'] is None:
            return self._render_start_game_screen()

        new_difficulty = 0
        next_review_at = 0
        try :
            split = user_message.split("set_difficulty:")[1]
            new_difficulty = int(split.split(';')[0])
            next_reviews = split.split(';')[1].split('next_review:')[1].split(',,')
            next_review_at = next_reviews[new_difficulty]
        except:
            return self._render_single_message("Cannot parse input", None, None)
        if new_difficulty < 0 or new_difficulty >= len(self.lang.difficulties):
            return self._render_single_message("Invalid difficulty level", None, None)

        old_difficulty = self.user['difficulty']
        if old_difficulty is None:
            old_difficulty = 0

        is_resumed = self._maybe_resume()

        self.user['difficulty'] = new_difficulty
        self._restart_user_game()

        return self._render_difficulty_changed(old_difficulty, new_difficulty, next_review_at, is_resumed)

    def _restart_user_game(self):
        self.user['review_counter_state'] = Counter('').resume().serialize()

        self._reset_user_next_prompt()

        self.user['active_game_counter_state'] = Counter('').resume().serialize()
        self.user['paused_counter_state'] = None

        self.user['counters_history_serialized'] = None
        self.user['badges_serialized'] = ""
        self.user['diamonds'] = 0

    def on_review_command(self) -> Reply:
        if self.user['active_game_counter_state'] is None:
            return self._render_start_game_screen()

        counter_active_game = Counter(self.user['active_game_counter_state'])
        counter_review_state = Counter(self.user['review_counter_state'])

        since_last_review_secs = None
        if abs(counter_active_game.get_total_seconds() - counter_review_state.get_total_seconds()) > 60:
            since_last_review_secs = Counter(self.user['review_counter_state']).get_total_seconds()

        return self._render_review_screen(since_last_review_secs)


    def _on_reviewed(self, user_message: str) -> Reply:
        if self.user['active_game_counter_state'] is None:
            return self._render_start_game_screen()

        now_timestamp = time.time()
        next_review = None
        user_timestamp = 0
        try:
            user_timestamp = int(user_message.split('reviewed_at:')[1].split(';')[0])
            next_review = user_message.split('next_review:')[1].split(',,')[self.user['difficulty']]
        except:
            return self._render_single_message("Cannot parse input", None, None)
        delta = abs(now_timestamp - user_timestamp)
        if delta > 60:
            return {
                'to_chat_id': self.user['user_id'],
                'message': self.lang.review_command_timeout,
                'buttons': [self._render_review_button()],
                'menu_commands': [],
                'image': None
            }

        is_resumed = self._maybe_resume()

        now_in_active_playtime_seconds = Counter(self.user['active_game_counter_state']).get_total_seconds()
        since_last_reward_secs = now_in_active_playtime_seconds - self.user['last_reward_time_at_active_counter_time_secs']

        is_cooldown = (since_last_reward_secs < 5*60) and self.user['counters_history_serialized'] is not None

        self._record_counter_time(REVIEW_COUNTER_HISTORY_NAME, self.user['review_counter_state'])
        self.user['review_counter_state'] = Counter('').resume().serialize()

        self._reset_user_next_prompt()

        if is_cooldown:
            return self._render_review_command_success(self.lang.cooldown_msg, None, next_review,
                                                       is_resumed=is_resumed)

        else:
            self.user['last_reward_time_at_active_counter_time_secs'] = Counter(self.user['active_game_counter_state']).get_total_seconds()
            maybe_badge_msg, maybe_badge_button =  self._handle_badge_event('on_review')
            badges_manager = BadgesManager(self.user['difficulty'], self.user['badges_serialized'])
            diamonds_msg = None
            
            if badges_manager.count_active_grumpy_cats_on_board() == 0:
                self.user['diamonds'] = self.user['diamonds'] + 1
            
                diamonds_msg = self.lang.diamond_new.format(count=self.user['diamonds'])
                if self.user['diamonds'] >= self._calculate_shop_price():
                    diamonds_msg += '\n' + self.lang.buy_next_achievement_for_diamonds.format(diamonds=self._calculate_shop_price())
            
            if badges_manager.count_active_grumpy_cats_on_board() > 0 and self.user['diamonds'] >= self._calculate_shop_price():
                diamonds_msg = self.lang.kick_grumpy_cat_for_diamonds.format(diamonds=self._calculate_shop_price())
            
            if diamonds_msg:
                maybe_badge_msg = (maybe_badge_msg + "\n\n" + diamonds_msg) if maybe_badge_msg else diamonds_msg
            return self._render_review_command_success(maybe_badge_msg, maybe_badge_button, next_review,
                                                       is_resumed=is_resumed)


    def _render_start_game_screen(self) -> Reply:
        return {
            'to_chat_id': self.user['user_id'],
            'message': self.lang.help_command_text.format(difficulty=self.lang.difficulties[self.user['difficulty']]),
            'buttons': [self._render_start_game_button()],
            'menu_commands': self._render_menu_commands(),
            'image': None
        }

    def _render_start_game_button(self) -> Button:
        return {
            'text': self.lang.help_command_start_playing_button,
            'url': self._get_frontend_base_url() + f'?env={self.env}&lang_code={self.lang.lang_code}&new_game=1&{NEXT_REVIEW_PROMPT_MINUTES_QUERY_PARAM}&shared_key_uuid={self.user["shared_key_uuid"]}'
        }

    def on_data_command(self) -> list[Reply]:
        data = [" - shared_key_uuid: " + self.user['shared_key_uuid']]
        data_short = [" - shared_key_uuid: " + self.user['shared_key_uuid']]
        for key in self.user:
            value = str(self.user[key])
            value_short = value
            if len(value) > 256:
                value_short = value[:256] + "..."
            if key != 'shared_key_uuid':
                data.append(f" - {key}: {value}")
                data_short.append(f" - {key}: {value_short}")

        return self._render_delete_data_screen(data_short, data)

    def on_feedback_command(self) -> Reply:
        return self._render_single_message(self.lang.feedback_text, None, None)

    def on_pause_command(self) -> Reply:
        if self.user['active_game_counter_state'] is None:
            return self._render_start_game_screen()

        if self.user['paused_counter_state'] is None:
            self._pause_user()

            return self._render_on_pause()
        else:
            return self._render_already_on_pause()

    def on_sleep_command(self) -> Reply:
        autopause_manager = AutopauseManager(self.user['autopause_config_serialized'])
        return self._render_single_message(
            self.lang.sleep_command_text.format(
                is_enabled='🟢' if autopause_manager.is_enabled() else '⚪️',
                bed_time=autopause_manager.get_bed_time() if autopause_manager.get_bed_time() is not None else 'N/A',
                wakeup_time=autopause_manager.get_wakep_time() if autopause_manager.get_wakep_time() is not None else 'N/A',
            ), None, {
                "text": self.lang.sleep_command_button,
                "url": self._get_frontend_base_url() + f'?env={self.env}'
                                                f'&lang_code={self.lang.lang_code}'
                                                f'&sleep=1'
                                                f'&enabled={"true" if autopause_manager.is_enabled() else "false"}'
                                                f'&bed_time={"22:00" if autopause_manager.get_bed_time() is None else autopause_manager.get_bed_time()}'
                                                f'&wakeup_time={"06:00" if autopause_manager.get_wakep_time() is None else autopause_manager.get_wakep_time()}'
            })

    def on_stats_command(self) -> Reply:
        if self.user['active_game_counter_state'] is None:
            return self._render_start_game_screen()

        till_next_prompt_time = 0
        if self.user['next_prompt_time'] is not None:
            till_next_prompt_time = max(int((self.user['next_prompt_time'] - now_utc()).total_seconds()), 0)

        paused_at = None
        if self.user['paused_counter_state'] is not None:
            paused_at = now_utc() - datetime.timedelta(seconds=Counter(self.user['paused_counter_state']).get_total_seconds())

        fname = GraphRenderer().render_graph(self.lang, get_timer_recs_from_history(
            self.user['counters_history_serialized']), PROMPT_MINUTES[self.user['difficulty']]
                                             , self.lang.difficulties[self.user['difficulty']],
                                             paused_at)

        return self._render_stats(till_next_prompt_time, fname)

    def on_shop_command(self) -> Reply:
        return {
            'to_chat_id': self.user['user_id'],
            'message': self.lang.shop_description.format(diamonds=self.user['diamonds']),
            'buttons': [
                {
                    'text': self.lang.shop_button_kick_grumpy_cat.format(price=self._calculate_shop_price()),
                    'data': 'shop_unblock'
                },
                {
                    'text': self.lang.shop_button_next_achivement.format(price=self._calculate_shop_price()),
                    'data': 'shop_progress'
                }
            ],
            'menu_commands': [],
            'image': None
        }
    
    def _calculate_shop_price(self) -> int:
        return PRICE_DIAMONDS[self.user['difficulty']]
    
    def on_shop_unblock_command(self) -> Reply:
        price = self._calculate_shop_price()
        if price > self.user['diamonds']:
            return self._render_single_message(self.lang.shop_no_enough_diamonds, None, None)
        
        badges_manager = BadgesManager(self.user['difficulty'], self.user['badges_serialized'])
        if badges_manager.count_active_grumpy_cats_on_board() < 1:
            return self._render_single_message(self.lang.shop_no_grumpy_cat, None, None)
        
        self.user['diamonds'] -= price
        self.user['spent_diamonds'] += price
        
        maybe_badge_msg, maybe_badge_button = self._handle_badge_event("on_shoo_cat")

        return {
            'message': (maybe_badge_msg if maybe_badge_msg else "Should never happen") + "\n\n" +
                        self.lang.shop_diamonds_left.format(diamonds=self.user['diamonds']),
            'to_chat_id': self.user['user_id'],
            'buttons': [maybe_badge_button] if maybe_badge_button else [],
            'menu_commands': self._render_menu_commands(),
            'image': None
        }

    def on_shop_progress_command(self) -> Reply:
        price = self._calculate_shop_price()
        if price > self.user['diamonds']:
            return self._render_single_message(self.lang.shop_no_enough_diamonds, None, None)
        
        badges_manager = BadgesManager(self.user['difficulty'], self.user['badges_serialized'])
        if badges_manager.count_active_grumpy_cats_on_board() > 0:
            return self._render_single_message(self.lang.locked_achievements, None, None)
        
        self.user['diamonds'] -= price
        self.user['spent_diamonds'] += price
        
        maybe_badge_msg, maybe_badge_button = self._handle_badge_event("on_force_badge_open")

        return {
            'message': (maybe_badge_msg if maybe_badge_msg else "Should never happen") + "\n\n" +
                        self.lang.shop_diamonds_left.format(diamonds=self.user['diamonds']),
            'to_chat_id': self.user['user_id'],
            'buttons': [maybe_badge_button] if maybe_badge_button else [],
            'menu_commands': self._render_menu_commands(),
            'image': None
        }

    def on_difficulty_command(self) -> Reply:
        return self._render_difficulty_buttons()

    def on_formula_command(self) -> Reply:
        return self._render_edit_formula()

    @staticmethod
    def process_tick(users_orm: UsersOrm, env) -> list[Reply]:
        replies: list[Reply] = []
        quota = 20
        for difficulty in range(0, 5):
            if quota <= 0:
                break
            users = users_orm.get_some_users_for_prompt(quota, difficulty)
            for user in users:
                quota -= 3
                manager = GameManager(user, env)
                if user['next_prompt_type'] == NEXT_PROMPT_TYPE_PENALTY:
                    replies += [manager._process_penalty_prompt()]
                else:
                    replies += [manager._process_reminder_prompt()]
                users_orm.upsert_user(user)

        autopaused_events = users_orm.get_some_next_autopause_events(quota)
        for user in autopaused_events:
            manager = GameManager(user, env)
            replies += manager._process_autopause()
            users_orm.upsert_user(user)

        return replies

    def _process_autopause(self) -> list[Reply]:
        autopause_manager = AutopauseManager(self.user['autopause_config_serialized'])
        next_autopause_event_timestamp = autopause_manager.get_next_autopause_event_at_timestamp()
        if next_autopause_event_timestamp is None:
            return []
        self.user['next_autopause_event_time'] = datetime.datetime.fromtimestamp(next_autopause_event_timestamp + 1, tz=datetime.timezone.utc)

        if autopause_manager.is_in_interval(now_utc().timestamp()):
            if self.user['paused_counter_state'] is None:
                self._pause_user()

                return [self._render_single_message(self.lang.autopause_on_msg.format(until_time=autopause_manager.get_wakep_time()), None, None)]
            else:
                return []
        else:
            is_resumed = self._maybe_resume()

            if is_resumed:
                return [self._render_single_message(self.lang.autopause_resumed_msg, None, self._render_review_button())]
            else:
                return []

    def _process_penalty_prompt(self) -> Reply:
        self._reset_user_next_prompt()

        maybe_badge_msg, maybe_badge_button = self._handle_badge_event('on_penalty')

        return self._render_penalty(maybe_badge_msg, maybe_badge_button)

    def _record_counter_time(self, counter_name: str, serialized_counter: Optional[str]):
        counter = Counter(serialized_counter)
        self.user['counters_history_serialized'] = add_timer_rec_to_history(self.user['counters_history_serialized'], {
            'counter_name': counter_name,
            'counter_stopped_duration_secs': counter.get_total_seconds(),
            'event_datetime': now_utc()
        })

    def _render_review_button(self) -> Button:
        return {
            'text': self.lang.review_btn,
            'url': self._get_frontend_base_url() +
                   f'?env={self.env}&lang_code={self.lang.lang_code}&review=1&{NEXT_REVIEW_PROMPT_MINUTES_QUERY_PARAM}'
        }

    def _render_game_started_screen(self, next_review: str, maybe_badge_message: Optional[str], maybe_badge_button: Optional[Button]) -> Reply:
        difficulty_name = self.lang.difficulties[self.user['difficulty']]
        buttons = [self._render_review_button()]
        if maybe_badge_button is not None:
            buttons.append(maybe_badge_button)
        return {
            'to_chat_id': self.user['user_id'],
            'message': self.lang.game_started.format(next_review=next_review, difficulty=difficulty_name
                                                , maybe_achievement=("\n" + maybe_badge_message + "\n") if maybe_badge_message is not None else ""),
            'buttons': buttons,
            'menu_commands': [],
            'image': None
        }

    def _render_review_command_success(self, maybe_achievement_msg: Optional[str], maybe_achievement_button: Optional[Button], next_review: str, is_resumed: bool) -> Reply:
        message = self.lang.review_command_success_text.format(next_review=next_review, time=time,
                                                          pause_prompt=self._render_pause_prompt(),
                                                          maybe_achievement=("\n" + maybe_achievement_msg + "\n") if maybe_achievement_msg is not None else "")
        buttons = [self._render_review_button()]
        if maybe_achievement_button is not None:
            buttons.append(maybe_achievement_button)
        if is_resumed:
            message = self.lang.resumed + "\n" + message
        return {
            'to_chat_id': self.user['user_id'],
            'message': message,
            'buttons': buttons,
            'menu_commands': self._render_menu_commands(),
            'image': None
        }

    def _maybe_resume(self) -> bool:
        if self.user['paused_counter_state']:
            pause_counter = Counter(self.user['paused_counter_state'])
            seconds = pause_counter.get_total_seconds()
            if self.user['next_prompt_time'] is not None:
                self.user['next_prompt_time'] = self.user['next_prompt_time'] + datetime.timedelta(seconds=seconds)

            active_play_time_counter = Counter(self.user['active_game_counter_state'])
            active_play_time_counter.resume()
            self.user['active_game_counter_state'] = active_play_time_counter.serialize()

            self._record_counter_time(PAUSED_COUNTER_HISTORY_NAME, self.user['paused_counter_state'])
            self.user['paused_counter_state'] = None

            review_counter = Counter(self.user['review_counter_state'])
            review_counter.resume()
            self.user['review_counter_state'] = review_counter.serialize()

            self.user['paused_counter_state'] = None

            return True
        return False

    def _render_list_of_langs(self) -> Reply:
        languages = LangProvider.get_available_languages()
        buttons: list[Button] = []
        for lang_code in sorted(languages):
            lang = languages[lang_code]
            if lang_code == "en":
                buttons.insert(0, {
                    "text": lang.lang_name,
                    "data": lang_code
                })
            else:
                buttons.append({
                    "text": lang.lang_name,
                    "data": lang_code
                })
        return {
            'to_chat_id': self.user['user_id'],
            'message': "Select your language:",
            'buttons': buttons,
            'menu_commands': [],
            'image': None
        }

    def _render_single_message(self, msg: str, maybe_badge_message: Optional[str], maybe_badge_button: Optional[Button]) -> Reply:
        buttons = []
        if maybe_badge_button is not None:
            buttons.append(maybe_badge_button)
        return {
            'to_chat_id': self.user['user_id'],
            'message': msg + ("\n\n" + maybe_badge_message if maybe_badge_message is not None else ""),
            'buttons': buttons,
            'menu_commands': [],
            'image': None
        }

    def _render_difficulty_buttons(self) -> Reply:
        buttons: list[Button] = []
        for difficulty in range(0, 5):
            text = self.lang.difficulties[difficulty] + " (" + self._format_time_minutes(PROMPT_MINUTES[difficulty] * 60, skip_zeros=True) + ")"

            if difficulty == self.user['difficulty']:
                text = text + " - " + self.lang.current_difficulty
            buttons.append({
                'text': text,
                'url': self._get_frontend_base_url() + f'?env={self.env}&lang_code={self.lang.lang_code}&set_difficulty={difficulty}&' + NEXT_REVIEW_PROMPT_MINUTES_QUERY_PARAM
            })

        return {
            'to_chat_id': self.user['user_id'],
            'message': self.lang.difficulty_command_text,
            'buttons': buttons,
            'menu_commands': [],
            'image': None
        }

    def _render_difficulty_changed(self, old_difficulty, new_difficulty, next_review_at, is_resumed) -> Reply:
        message = self.lang.difficulty_level_changed.format(
            old=self.lang.difficulties[old_difficulty], 
            new=self.lang.difficulties[new_difficulty], next_review=next_review_at
            )
        if is_resumed:
            message = self.lang.resumed + "\n" + message
        return {
            'to_chat_id': self.user['user_id'],
            'message': message,
            'buttons': [self._render_review_button()],
            'menu_commands': [],
            'image': None
        }

    def _render_stats(self, till_next_prompt_time, fname) -> Reply:
        badges_manager = BadgesManager(self.user['difficulty'], self.user['badges_serialized'])
        active_play_time_seconds = Counter(self.user['active_game_counter_state']).get_total_seconds()
        is_paused = self.user['paused_counter_state'] is not None
        since_last_review_secs = Counter(self.user['review_counter_state']).get_total_seconds()

        return {
            'to_chat_id': self.user['user_id'],
            'message': self.lang.stats_command.format(
                level=badges_manager.get_level() + 2 if badges_manager.is_level_completed() else badges_manager.get_level() + 1,
                difficulty=self.lang.difficulties[self.user['difficulty']],
                difficulty_details=str(self.user['difficulty'] + 1) + "/" + str(len(self.lang.difficulties)),
                time=self._format_time_minutes(active_play_time_seconds),
                diamonds=self.user['diamonds'],
                spent_diamonds=self.user['spent_diamonds'],
                paused="⚪" if not is_paused else "🟢",
                cooldown=self._format_time_seconds(5*60 - since_last_review_secs if since_last_review_secs < 5*60 else 0),
                punishment=self._format_time_minutes(till_next_prompt_time, skip_zeros=True)
            ),
            'buttons': [{
                'text': self.lang.view_badges_button,
                'url': self._render_board_url()
            }],
            'menu_commands': [],
            'image': fname
        }

    def _render_edit_formula(self) -> Reply:
        return {
            'to_chat_id': self.user['user_id'],
            'message': self.lang.formula_command_text,
            'buttons': [
                {
                    'text': self.lang.formula_command_button,
                    'url': self._get_frontend_base_url() + 
                        f'?env={self.env}&lang_code={self.lang.lang_code}&formula=1&shared_key_uuid={self.user["shared_key_uuid"]}'
                }
            ],
            'menu_commands': [],
            'image': None
        }

    def _render_review_screen(self, since_last_review_secs) -> Reply:
        message = []
        if self.user['paused_counter_state'] is not None:
            message.append(self.lang.review_paused_text)
        elif since_last_review_secs is not None:
            message.append(self.lang.review_since_last_time.format(duration=self._format_time_minutes(since_last_review_secs)))

        message.append(self.lang.review_command_text)

        return {
            'to_chat_id': self.user['user_id'],
            'message': "\n".join(message),
            'buttons': [
                {
                    'text': self.lang.review_command_button_yourself,
                    'url': self._get_frontend_base_url() +
                           f'?env={self.env}&lang_code={self.lang.lang_code}&review=1&{NEXT_REVIEW_PROMPT_MINUTES_QUERY_PARAM}'
                },
                {
                    'text': self.lang.review_command_button_world,
                    'url': self._get_frontend_base_url() +
                           f'?env={self.env}&lang_code={self.lang.lang_code}&review=1&{NEXT_REVIEW_PROMPT_MINUTES_QUERY_PARAM}'
                }
            ],
            'menu_commands': self._render_menu_commands(),
            'image': None
        }

    def _render_on_pause(self) -> Reply:
        return {
            'to_chat_id': self.user['user_id'],
            'message': self.lang.paused_command,
            'buttons': [self._render_review_button()],
            'menu_commands': [],
            'image': None
        }

    def _render_already_on_pause(self) -> Reply:
        return {
            'to_chat_id': self.user['user_id'],
            'message': self.lang.already_paused,
            'buttons': [self._render_review_button()],
            'menu_commands': [],
            'image': None
        }

    def _render_delete_data_screen(self, data_short, data) -> list[Reply]:
        random_fname = 'tmp_user_data_' + str(np.random.randint(100000, 900000)) + '.txt'
        # write message to file
        with open(random_fname, 'w') as f:
            f.write("\n\n".join(data))

        with open(random_fname, 'rb') as file:
            return [
                {
                    'to_chat_id': self.user['user_id'],
                    'message': self.lang.data_view + "\n\n<code>" + "\n\n".join(data_short) + "</code>",
                    'buttons': [
                        {
                            'text': self.lang.data_view_localstorage_button,
                            'url': self._get_frontend_base_url() + f'?env={self.env}&lang_code={self.lang.lang_code}&view_localstorage=1'
                        },
                        {
                            'text': self.lang.data_delete_button,
                            'url': self._get_frontend_base_url() + f'?env={self.env}&lang_code={self.lang.lang_code}&delete_data=1'
                        }
                    ],
                    'menu_commands': self._render_menu_commands(),
                    'image': random_fname
                }]


    def _render_penalty(self, maybe_badge_message: Optional[str], maybe_badge_button: Optional[Button]) -> Reply:

        buttons = [self._render_review_button()]
        if maybe_badge_button is not None:
            buttons.append(maybe_badge_button)

        return {
            'to_chat_id': self.user['user_id'],
            'message': self.lang.penalty_text.format(
                maybe_achievement=("\n" + maybe_badge_message + "\n") if maybe_badge_message is not None else "",
                pause_prompt=self._render_pause_prompt()
            ),
            'buttons': buttons,
            'menu_commands': [],
            'image': None
        }

    def _process_reminder_prompt(self) -> Reply:
        self.user['next_prompt_type'] = NEXT_PROMPT_TYPE_PENALTY
        self.user['next_prompt_time'] = now_utc() + datetime.timedelta(minutes=REVIEW_INTERVAL_MINS)

        _, maybe_badge_button = self._handle_badge_event('on_prompt')

        return self._render_reminder_prompt(maybe_badge_button)

    def _reset_user_next_prompt(self):
        difficulty = self.user['difficulty']
        penalty_minutes = PROMPT_MINUTES[difficulty]

        self.user['next_prompt_time'] = now_utc() + datetime.timedelta(minutes=penalty_minutes)
        self.user['next_prompt_type'] = NEXT_PROMPT_TYPE_PENALTY
        if HAS_REMINDER[difficulty]:
            self.user['next_prompt_time'] -= datetime.timedelta(minutes=REVIEW_INTERVAL_MINS)
            self.user['next_prompt_type'] = NEXT_PROMPT_TYPE_REMINDER

    def _render_reminder_prompt(self, maybe_badge_button: Optional[Button]) -> Reply:
        buttons = [self._render_review_button()]
        if maybe_badge_button is not None:
            buttons.append(maybe_badge_button)
        return {
            'to_chat_id': self.user['user_id'],
            'message': self.lang.reminder_text.format(pause_prompt=self._render_pause_prompt()),
            'buttons': buttons,
            'menu_commands': [],
            'image': None
        }

    def _render_board_url(self) -> str:
        active_play_time_secs = Counter(self.user['active_game_counter_state']).get_total_seconds()
        button_url = self._get_frontend_base_url().replace("index.html", "board.html")
        button_url += '?lang=' + self.lang.lang_code + '&env=' + self.env
        badges_manager = BadgesManager(self.user['difficulty'], self.user['badges_serialized'])
        maybe_last_badge = badges_manager.get_last_badge()
        if maybe_last_badge is not None:
            button_url += '&new_badge=' + maybe_last_badge

        button_url += "&level=" + str(badges_manager.get_level() + 1)
        button_url += "&b1=" + serialize_board(badges_manager.get_board())

        progress = badges_manager.progress(active_play_time_secs)
        button_url += "&bp1=" + serialize_progress(progress)

        if badges_manager.is_level_completed():
            button_url += "&b2=" + serialize_board(badges_manager.get_next_level_board())
            button_url += "&bp2=" + serialize_progress(badges_manager.new_level_empty_progress())

        button_url += "&ts=" + str(int(time.time()))

        return button_url

    def _handle_badge_event(self, event: str) -> tuple[Optional[str], Optional[Button]]:
        badges_manager = BadgesManager(self.user['difficulty'], self.user['badges_serialized'])

        active_play_time_secs = Counter(self.user['active_game_counter_state']).get_total_seconds()

        badge = getattr(badges_manager, event)(active_play_time_secs)

        self.user['badges_serialized'] = badges_manager.serialize()

        button_url = self._render_board_url()

        view_achievements_button: Button = {
            'text': self.lang.view_badges_button,
            'url': button_url
        }

        if badge == "c0_removed":
            if badges_manager.count_active_grumpy_cats_on_board() == 0:
                return self.lang.grumpy_cat_kicked_out + "\n" + self.lang.achievements_unblocked, view_achievements_button
            return self.lang.grumpy_cat_kicked_out + "\n" + self.lang.remained_grumpy_cats.format(count=badges_manager.count_active_grumpy_cats_on_board()), view_achievements_button

        if badge is None:
            if badges_manager.count_active_grumpy_cats_on_board() > 0:
                return self.lang.kicking_out_grumpy_cat if event == 'on_review' else self.lang.locked_achievements, view_achievements_button

            return None, None if event == 'on_formula_updated' else view_achievements_button

        return self.lang.badge_unhappy_cat if badge == "c0" else self.lang.badge_new, view_achievements_button

    def _pause_user(self):
        paused_counter = Counter("")
        paused_counter.resume()
        self.user['paused_counter_state'] = paused_counter.serialize()

        active_counter = Counter(self.user['active_game_counter_state'])
        active_counter.pause()
        self.user['active_game_counter_state'] = active_counter.serialize()

        review_counter = Counter(self.user['review_counter_state'])
        review_counter.pause()
        self.user['review_counter_state'] = review_counter.serialize()

    def _render_pause_prompt(self):
        autopause_manager = AutopauseManager(self.user['autopause_config_serialized'])
        pause_prompt = self.lang.pause_prompt
        if not autopause_manager.is_enabled():
            pause_prompt += "\n\n" + self.lang.autopause_prompt
        return pause_prompt

    def _on_sleep_config(self, user_message: str) -> Reply:
        msg_tail = user_message.split('sleep_config:')[1]
        split = msg_tail.split(',,')
        enabled = split[0] == '1' or split[0].lower() == 'true'
        user_tz = split[1]
        user_tz_offset_secs = int(split[2])
        bed_time = split[3]
        wakeup_time = split[4]

        autopause_manager = AutopauseManager(self.user['autopause_config_serialized'])
        autopause_manager.update(enabled, user_tz, user_tz_offset_secs, bed_time, wakeup_time)
        self.user['autopause_config_serialized'] = autopause_manager.serialize()
        autopause_next_timestamp = autopause_manager.get_next_autopause_event_at_timestamp()
        if autopause_manager.is_enabled() and autopause_next_timestamp is not None:
            self.user['next_autopause_event_time'] = datetime.datetime.fromtimestamp(autopause_next_timestamp + 1, tz=datetime.timezone.utc)
        else:
            self.user['next_autopause_event_time'] = None

        return self._render_single_message(self.lang.sleep_config_updated.format(
            is_enabled='🟢' if enabled else '⚪️',
            bed_time=autopause_manager.get_bed_time() if autopause_manager.get_bed_time() is not None else 'N/A',
            wakeup_time=autopause_manager.get_wakep_time() if autopause_manager.get_wakep_time() is not None else 'N/A'
        ), None, None)

    def on_settings_command(self) -> Reply:
        return self._render_settings_screen()

    def _render_menu_commands(self) -> list[Tuple[str, str]]:
        return [
            ("review", self.lang.menu_review),
            ("pause", self.lang.menu_pause),
            ("formula", self.lang.menu_formula),
            ("stats", self.lang.menu_stats),
            ("shop", self.lang.menu_shop),
            ("settings", self.lang.menu_settings)
        ]

    def _render_settings_screen(self) -> Reply:
        sub_commands: list[Button] = [
            { "data": "sleep", "text": self.lang.menu_sleep },
            { "data": "difficulty", "text": self.lang.menu_difficulty },
            { "data": "data", "text": self.lang.menu_data },
            { "data": "feedback", "text": self.lang.menu_feedback },
            { "data": "change_server", "text": self.lang.menu_change_server }
        ]

        return {
            'to_chat_id': self.user['user_id'],
            'message': self.lang.settings_title,
            'buttons': sub_commands,
            'menu_commands': [],
            'image': None
        }

    def _get_frontend_base_url(self) -> str:
        if self.user['frontend_base_url_override'] is not None:
            return self.user['frontend_base_url_override']
        else:
            parsed_base_urls = get_frontend_base_urls()
            return parsed_base_urls[0]['base_url']

















