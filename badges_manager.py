import json
from typing import TypedDict, Optional, NotRequired

from badge_counters.cat_badge_counter import CatBadgeCounter
from badge_counters.feather_badge_counter import FeatherBadgeCounter
from badge_counters.star_badge_counter import StarBadgeCounter
from badge_counters.time_badge_counter import TimeBadgeCounter
from level_generator import get_level


class BoardCell(TypedDict):
    badge: str
    is_active: NotRequired[bool] # Means "unlocked" for regular cells and "grumpy-cat-is-in" for c0 cells.
                                 # Default is False (inactive) e.g. for a new level
    is_last_modified: NotRequired[bool]

class UserBadgesData(TypedDict):
    badges_state: dict[str, str]
    last_badge: Optional[str]
    level: int # starting from 0
    board: list[BoardCell]

    c0_hp_next_delta: int
    c0_hp: int
    c0_lock_started_at: int
    c0_active_time_penalty: int

class BadgesManager:

    def __init__(self, difficulty, badges_serialized = None):
        self.difficulty = difficulty
        if badges_serialized is None or badges_serialized == "":
            self.data = UserBadgesData(badges_state={},
                                       board=self._level_badges_to_new_board(get_level(difficulty, 0)),
                                       level=0,
                                       c0_hp=0,
                                       c0_hp_next_delta=3,
                                       last_badge=None,
                                       c0_active_time_penalty=0,
                                       c0_lock_started_at=0)
        else:
            self.data = UserBadgesData(**json.loads(badges_serialized))

        if not self.data.get("badges_state"):
            self.data["badges_state"] = {}

        if not self.data.get("last_badge"):
            self.data["last_badge"] = None

        if not self.data.get("level"):
            self.data["level"] = 0

        if not self.data.get("board"):
            level_badges = get_level(difficulty, self.data["level"])
            self.data["board"] = self._level_badges_to_new_board(level_badges)

        if not self.data.get("c0_hp_next_delta"):
            self.data["c0_hp_next_delta"] = 3

        if not self.data.get("c0_hp"):
            self.data["c0_hp"] = 0
            for cell in self.data["board"]:
                if cell["badge"] == "c0" and cell.get("is_active"):
                    self.data["c0_hp"] = self._max_grumpy_cat_healthpoints()

        if not self.data.get("c0_lock_started_at"):
            self.data["c0_lock_started_at"] = 0

        if not self.data.get("c0_active_time_penalty"):
            self.data["c0_active_time_penalty"] = 0

    def _max_grumpy_cat_healthpoints(self):
        return 5 * (self.difficulty + 1)

    def on_game_started(self, active_play_time_secs: float) -> Optional[str]:
        # "terminate_if_found" is False we need to initialize all counters. That's a rare case when two badges might be have given
        # on start; we should be OK picking the first one.
        self.data["c0_hp_next_delta"] = 3
        self.data["c0_hp"] = 0
        self.data["c0_lock_started_at"] = 0
        self.data["c0_active_time_penalty"] = 0
        return self._chain_badge_counters("on_game_started", int(active_play_time_secs), False)

    def on_formula_updated(self, active_play_time_secs: float) -> Optional[str]:
        return self._chain_badge_counters("on_formula_updated", int(active_play_time_secs),True)

    def on_prompt(self, active_play_time_secs: float) -> Optional[str]:
        self.data["c0_hp_next_delta"] = 2
        return self._chain_badge_counters("on_prompt", int(active_play_time_secs), False)

    def on_penalty(self, active_play_time_secs: float) -> Optional[str]:
        self.data["c0_hp_next_delta"] = 1
        return self._chain_badge_counters("on_penalty", int(active_play_time_secs), False)

    def on_review(self, active_play_time_secs: float) -> Optional[str]:
        old_delta = self.data["c0_hp_next_delta"]
        self.data["c0_hp_next_delta"] = 3

        if self.count_active_grumpy_cats_on_board() > 0:
            self.data["c0_hp"] = max(0, self.data["c0_hp"] - old_delta)
            self.data["board"] = self.clone_board_without_last_modified(self.data["board"])

            if self.data["c0_hp"] == 0:
                self.data["board"] = self._expel_grumpy_cat(self.data["board"])
                if self.count_active_grumpy_cats_on_board() > 0:
                    self.data["c0_hp"] = self._max_grumpy_cat_healthpoints()
                else:
                    self.data["c0_active_time_penalty"] += int(active_play_time_secs) - self.data["c0_lock_started_at"]

                self.data["last_badge"] = "c0_removed"
                return self.data["last_badge"]

        return self._chain_badge_counters("on_review", int(active_play_time_secs), True)

    def get_grumpy_cat_healthpoints(self):
        return self.data["c0_hp"]

    def get_level(self):
        return self.data["level"]

    def get_board(self):
        return self.data["board"]

    def get_last_badge(self):
        return self.data.get("last_badge")

    def _adjust_active_play_time_secs(self, active_play_time_secs: int):
        accum = active_play_time_secs - self.data["c0_active_time_penalty"]
        if self.count_active_grumpy_cats_on_board() > 0:
            extra_curr_cat = active_play_time_secs - self.data["c0_lock_started_at"]
            accum -= extra_curr_cat
        return accum

    # "terminate_if_found" is useful when there could be multiple rewards for a single action, to make sure only one of them is given
    # and the state of the others is not updated. However, for penalties, should be False, because the penalty should affect
    # all the badges.
    def _chain_badge_counters(self, method_name, active_play_time_secs: int, terminate_if_found = False) -> Optional[str]:
        counters = [
            CatBadgeCounter(),
            TimeBadgeCounter(),
            StarBadgeCounter(),
            FeatherBadgeCounter()
        ]

        if self.is_level_completed():
            self.data["level"] += 1
            self.data["board"] = self._level_badges_to_new_board(get_level(self.difficulty, self.data["level"]))
            self.data["last_badge"] = None
            self.data["badges_state"] = {}
            self.data["c0_hp"] = 0
            self.data["c0_hp_next_delta"] = 3
            self.data["c0_lock_started_at"] = 0
            self.data["c0_active_time_penalty"] = 0
            for counter in counters:
                badge, new_state = counter.on_game_started(self._adjust_active_play_time_secs(active_play_time_secs), None, self.difficulty, self._get_inactive_badges_on_board(self.data['board']))
                self.data["badges_state"][counter.__class__.__name__] = new_state

        self.data['board'] = self.clone_board_without_last_modified(self.data['board'])
        self.data['last_badge'] = None

        badge_to_put_on_board = None
        has_old_grumpy_cat = (self.count_active_grumpy_cats_on_board() > 0)
        if has_old_grumpy_cat:
            # TODO: move "c0" logic outside of CatCounter to avoid brain-splitting
            if method_name == "on_penalty":
                badge_to_put_on_board = "c0"
        else:
            for counter in counters:
                state = None
                if self.data["badges_state"].get(counter.__class__.__name__) is not None:
                    state = self.data["badges_state"][counter.__class__.__name__]

                method = getattr(counter, method_name)
                badge, new_state = method(self._adjust_active_play_time_secs(active_play_time_secs), state, self.difficulty, self._get_inactive_badges_on_board(self.data['board']))

                self.data["badges_state"][counter.__class__.__name__] = new_state

                if badge is not None and badge_to_put_on_board is None:
                    badge_to_put_on_board = badge
                    if terminate_if_found:
                        break

        if badge_to_put_on_board:
            self.data["board"], self.data["last_badge"] = self._put_badge_to_board(badge_to_put_on_board)

            if self.data["last_badge"] == "c0" and not has_old_grumpy_cat:
                self.data["c0_lock_started_at"] = active_play_time_secs
                self.data["c0_hp"] = self._max_grumpy_cat_healthpoints()

            return self.data["last_badge"]
        else:
            # No new badge => no changes on the board
            return None

    def _get_inactive_badges_on_board(self, board: [BoardCell]):
        inactive_badges = []
        for cell in board:
            if cell['badge'] != 'c0' and (not cell.get("is_active")):
                inactive_badges.append(cell["badge"])
        return inactive_badges

    def progress(self, active_play_time_secs: float):
        badges = ["f0", "s0", "s1", "s2", "t0", "c1", "c2", "c0"]

        counters = [
            CatBadgeCounter(),
            TimeBadgeCounter(),
            StarBadgeCounter(),
            FeatherBadgeCounter()
        ]

        all_progress = {}
        for counter in counters:
            for badge in badges:
                maybe_progress = None
                if badge == "c0":
                    maybe_progress = {
                        "remaining_reviews": self.data["c0_hp"],
                        "challenge": "review",
                        "badge": badge,
                        "progress_pct": 100 - (self.data["c0_hp"] * 100 // self._max_grumpy_cat_healthpoints())
                    }
                else:
                    maybe_progress = counter.progress(badge, self._adjust_active_play_time_secs(int(active_play_time_secs)), self.data["badges_state"].get(counter.__class__.__name__), self.difficulty, self._get_inactive_badges_on_board(self.data['board']))

                if maybe_progress is not None:
                    all_progress[badge] = maybe_progress

        return all_progress

    def new_level_empty_progress(self):
        badges = ["f0", "s0", "s1", "s2", "t0", "c1", "c2"]

        counters = [
            CatBadgeCounter(),
            TimeBadgeCounter(),
            StarBadgeCounter(),
            FeatherBadgeCounter()
        ]

        all_progress = {}
        next_level_board = self._get_inactive_badges_on_board(get_level(self.difficulty, self.data["level"] + 1))
        for counter in counters:
            for badge in badges:
                maybe_progress = counter.progress(
                    badge,
                    0,
                    None,
                    self.difficulty,
                    next_level_board
                )
                if maybe_progress is not None:
                    all_progress[badge] = maybe_progress

        return all_progress


    def serialize(self) -> str:
        return json.dumps(self.data)

    def clone_board_without_last_modified(self, board):
        settled_board: [BoardCell] = []
        for cell in board:
            settled_board.append({
                "badge": cell["badge"],
                "is_active": cell.get("is_active"),
            })
        return settled_board

    def _level_badges_to_new_board(self, level) -> [BoardCell]:
        board = []
        for badge in level:
            board.append({
                "badge": badge,
            })
        return board

    def count_active_grumpy_cats_on_board(self):
        cnt = 0
        for cell in self.data['board']:
            if cell["badge"] == "c0" and cell.get("is_active"):
                cnt += 1
        return cnt

    def _expel_grumpy_cat(self, board: [BoardCell]):
        settled_board = self.clone_board_without_last_modified(board)
        for cell in settled_board:
            if cell["badge"] == "c0" and cell.get("is_active"):
                cell["is_active"] = False
                cell["is_last_modified"] = True
                break
        return settled_board

    def _has_inactive_badge_on_board(self, board: [BoardCell], badge):
        for cell in board:
            if cell["badge"] == badge and not cell.get("is_active"):
                return True
        return False

    def _activate_badge_on_board(self, board: [BoardCell], badge: str):
        settled_board = self.clone_board_without_last_modified(board)
        for cell in settled_board:
            if cell["badge"] == badge and not cell.get("is_active"):
                cell["is_active"] = True
                cell["is_last_modified"] = True
                break
        return settled_board

    def _put_badge_to_board(self, badge)-> ([BoardCell], str):
        old_board = self.data["board"]

        if self._has_inactive_badge_on_board(old_board, badge):
            return self._activate_badge_on_board(old_board, badge), badge

        return old_board, None

    def is_level_completed(self):
        board = self.data["board"]
        fine_cells = 0
        for cell in board:
            if cell["badge"] == "c0":
                if not cell.get("is_active"):
                    fine_cells += 1
            elif cell.get("is_active"):
                fine_cells += 1

        return fine_cells == len(board)

    def get_next_level_board(self):
        return self._level_badges_to_new_board(get_level(self.difficulty, self.data["level"] + 1))
