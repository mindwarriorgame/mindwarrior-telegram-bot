import json
import random
from typing import TypedDict, Optional, NotRequired

from badge_counters.cat_badge_counter import CatBadgeCounter
from badge_counters.feather_badge_counter import FeatherBadgeCounter
from badge_counters.star_badge_counter import StarBadgeCounter
from badge_counters.time_badge_counter import TimeBadgeCounter

LEVELS = [
    ["f0", "s0", "c0"],
    ["s1", "t0", "c0", "c0"],
    ["s0", "s1", "c0"],
    ["s0", "s1", "t0", "c0", "c0"],
    ["c0", "c1", "f0"],
    ["f0", "s2", "c2", "c0", "c0"],
]

def generate_levels():
    badges = ["f0", "s0", "s1", "s2", "t0", "c0", "c1", "c2"]

    for levelNo in range(5, 50):
        random_length = random.randint(5, 10)
        level = []
        for levelBadge in range(random_length):
            level.append(random.choice(badges))
        LEVELS.append(level)

    print(json.dumps(LEVELS))

# Pre-generate go make sure all users share same levels
LEVELS += [
           ["t0", "c1", "s2", "c2", "s2", "c1", "c2", "t0", "t0", "c1"], ["s0", "c2", "c1", "c0", "s2", "c1"],
           ["s0", "s1", "t0", "s0", "s0"], ["t0", "t0", "s2", "s0", "s2", "s2"],
           ["f0", "c2", "c0", "c0", "c1", "s0", "s2", "s2"],
           ["t0", "s0", "s0", "s2", "s0", "c2", "c0", "f0", "f0", "s2"], ["c0", "s1", "c1", "c0", "c2"],
           ["f0", "t0", "s1", "f0", "t0", "s2", "c2", "t0", "c1", "s1"], ["c0", "s0", "s0", "f0", "f0", "s0", "c1"],
           ["t0", "c1", "s2", "s0", "s0", "c2", "c0", "s1", "t0"], ["f0", "f0", "f0", "c1", "f0"],
           ["t0", "t0", "f0", "s2", "c0", "c2", "s2", "s0", "c2", "s2"],
           ["c0", "s1", "s1", "s2", "c0", "c1", "s2", "s2", "s1", "c0"], ["s2", "s0", "s1", "s1", "s0"],
           ["s0", "s1", "f0", "s1", "c2", "s2", "s1", "s0", "c2"], ["c2", "t0", "s0", "s2", "c2", "f0"],
           ["s0", "c2", "s2", "f0", "s0", "c0"], ["s2", "s1", "c1", "f0", "t0", "c2", "c2", "s0"],
           ["f0", "t0", "s1", "f0", "c1", "s2", "c0"], ["s2", "f0", "f0", "s0", "s0", "s2", "s1", "s1", "c1", "s1"],
           ["t0", "c0", "s1", "s1", "f0", "c1", "c2"], ["s0", "c0", "s1", "c0", "s2", "t0", "t0", "c1", "s1", "c2"],
           ["t0", "s1", "c2", "s0", "t0", "c1", "c1", "c1"],
           ["f0", "c2", "s2", "s1", "s0", "f0", "c2", "c1", "s0", "c2"], ["c2", "s0", "c1", "f0", "f0", "s0", "s1"],
           ["s1", "s0", "s2", "s0", "s0", "t0"], ["s1", "s1", "s2", "s1", "s2", "s0", "s1", "s2", "s1", "f0"],
           ["t0", "s0", "c2", "s1", "s2", "c1", "s2"], ["c2", "t0", "s1", "f0", "f0", "s0", "f0", "t0"],
           ["c0", "s2", "s0", "c2", "c0", "s1", "f0", "s2", "c0", "s0"],
           ["f0", "c2", "c1", "c1", "c2", "c0", "c0", "f0"], ["s1", "t0", "s1", "s2", "f0", "c0"],
           ["c1", "t0", "f0", "c0", "c2", "c1", "c2", "c0"], ["c1", "s2", "c1", "c2", "c0", "f0", "c1"],
           ["c1", "s2", "s0", "s1", "s1", "t0", "t0"], ["f0", "s2", "s0", "s0", "c2"],
           ["s1", "t0", "c1", "c0", "s1", "c2", "c2"], ["s0", "s2", "s2", "t0", "s2", "s1", "f0", "s1", "c1"],
           ["s0", "s2", "f0", "f0", "c2", "f0", "t0"], ["s0", "s0", "f0", "s0", "s1", "s1", "s1", "s2", "s0", "c0"],
           ["t0", "t0", "f0", "s2", "s2", "s2", "f0", "s2", "f0"], ["c2", "t0", "t0", "c0", "c2", "t0"],
           ["s0", "c2", "c2", "s2", "c0", "t0"], ["s0", "f0", "c0", "s2", "t0", "c1", "s1", "f0"],
           ["c1", "t0", "s2", "c2", "t0", "f0"]]



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

class BadgesManager:

    def __init__(self, badges_serialized = None):
        if badges_serialized is None or badges_serialized == "":
            self.data = UserBadgesData(badges_state={}, board=self._level_to_new_board(LEVELS[0]), level=0)
        else:
            self.data = UserBadgesData(**json.loads(badges_serialized))

        if not self.data.get("badges_state"):
            self.data["badges_state"] = {}

        if not self.data.get("last_badge"):
            self.data["last_badge"] = None

        if not self.data.get("level"):
            self.data["level"] = 0

        if not self.data.get("board"):
            self.data["level"] -= 1
            self.data["board"] = self.get_next_level_board()
            self.data["level"] += 1


    def on_game_started(self, active_play_time_secs: float, difficulty: int) -> Optional[str]:
        # "terminate_if_found" is False we need to initialize all counters. That's a rare case when two badges might be have given
        # on start; we should be OK picking the first one.
        return self._chain_badge_counters("on_game_started", int(active_play_time_secs), difficulty, False)

    def on_formula_updated(self, active_play_time_secs: float, difficulty: int) -> Optional[str]:
        return self._chain_badge_counters("on_formula_updated", int(active_play_time_secs), difficulty, True)

    def on_prompt(self, active_play_time_secs: float, difficulty: int) -> Optional[str]:
        return self._chain_badge_counters("on_prompt", int(active_play_time_secs), difficulty, False)

    def on_penalty(self, active_play_time_secs: float, difficulty: int) -> Optional[str]:
        return self._chain_badge_counters("on_penalty", int(active_play_time_secs), difficulty, False)

    def on_review(self, active_play_time_secs: float, difficulty: int) -> Optional[str]:
        return self._chain_badge_counters("on_review", int(active_play_time_secs), difficulty, True)

    def get_level(self):
        return self.data["level"]

    def get_board(self):
        return self.data["board"]

    def get_last_badge(self):
        return self.data.get("last_badge")

    # "terminate_if_found" is useful when there could be multiple rewards for a single action, to make sure only one of them is given
    # and the state of the others is not updated. However, for penalties, should be False, because the penalty should affect
    # all the badges.
    def _chain_badge_counters(self, method_name, active_play_time_secs: int, difficulty: int, terminate_if_found = False) -> Optional[str]:
        counters = [
            CatBadgeCounter(),
            TimeBadgeCounter(),
            StarBadgeCounter(),
            FeatherBadgeCounter()
        ]

        if self._is_level_over(self.data["board"]):
            self.data["level"] += 1
            self.data["board"] = self._level_to_new_board(LEVELS[self.data["level"]])
            self.data["last_badge"] = None
            self.data["badges_state"] = {}
            for counter in counters:
                badge, new_state = counter.on_game_started(active_play_time_secs, None, difficulty)
                self.data["badges_state"][counter.__class__.__name__] = new_state

        badge_to_put_on_board = None
        has_grumpy_cat = self._has_grumpy_cats_on_board(self.data["board"])
        for counter in counters:
            state = None
            if self.data["badges_state"].get(counter.__class__.__name__) is not None:
                state = self.data["badges_state"][counter.__class__.__name__]

            method = getattr(counter, method_name)
            badge, new_state = method(active_play_time_secs, state, difficulty)

            # Grumpy cat is always the first badge to kick out, and the badge that was used for it
            # shouldn't be accommodated for anything else (which means the change of state should be also ignored)
            if has_grumpy_cat:
                if badge:
                    badge_to_put_on_board = badge
                    break
                continue

            self.data["badges_state"][counter.__class__.__name__] = new_state

            if badge is not None and badge_to_put_on_board is None:
                badge_to_put_on_board = badge
                if terminate_if_found:
                    break

        if badge_to_put_on_board:
            self.data["board"], self.data["last_badge"] = self._put_badge_to_board(badge_to_put_on_board)
            return self.data["last_badge"]
        else:
            # No new badge => no changes on the board
            return None

    def progress(self, active_play_time_secs: float, difficulty: int):
        badges = ["f0", "s0", "s1", "s2", "t0", "c1", "c2"]

        counters = [
            CatBadgeCounter(),
            TimeBadgeCounter(),
            StarBadgeCounter(),
            FeatherBadgeCounter()
        ]

        all_progress = {}
        for counter in counters:
            for badge in badges:
                maybe_progress = counter.progress(badge, int(active_play_time_secs), self.data["badges_state"].get(counter.__class__.__name__), difficulty)
                if maybe_progress is not None:
                    all_progress[badge] = maybe_progress

        return all_progress

    def new_level_progress(self, difficulty):
        badges = ["f0", "s0", "s1", "s2", "t0", "c1", "c2"]

        counters = [
            CatBadgeCounter(),
            TimeBadgeCounter(),
            StarBadgeCounter(),
            FeatherBadgeCounter()
        ]

        all_progress = {}
        for counter in counters:
            for badge in badges:
                maybe_progress = counter.progress(badge, 0, None, difficulty)
                if maybe_progress is not None:
                    all_progress[badge] = maybe_progress

        return all_progress


    def serialize(self) -> str:
        return json.dumps(self.data)

    # Converts "target" cells into normal cells.
    def clone_board_without_last_modified(self, board):
        settled_board: [BoardCell] = []
        for cell in board:
            settled_board.append({
                "badge": cell["badge"],
                "is_active": cell.get("is_active"),
            })
        return settled_board

    def _level_to_new_board(self, level) -> [BoardCell]:
        board = []
        for badge in level:
            board.append({
                "badge": badge,
            })
        return board

    def _has_grumpy_cats_on_board(self, board: [BoardCell]):
        for cell in board:
            if cell["badge"] == "c0" and cell.get("is_active"):
                return True
        return False

    def _expel_grumpy_cat(self, board: [BoardCell], badge):
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

        if badge == "c0":
            return self._activate_badge_on_board(old_board, "c0"), "c0"

        if self._has_grumpy_cats_on_board(old_board):
            return self._expel_grumpy_cat(old_board, badge), badge

        if self._has_inactive_badge_on_board(old_board, badge):
            return self._activate_badge_on_board(old_board, badge), badge

        senior_overwrites = [["s2", "s1"], ["s2", "s0"], ["s1", "s0"], ["c2", "c1"]]
        for overwrite in senior_overwrites:
            senior_badge = overwrite[0]
            junior_badge = overwrite[1]
            if badge == senior_badge and self._has_inactive_badge_on_board(old_board, junior_badge):
                return self._activate_badge_on_board(old_board, junior_badge), junior_badge

        return old_board, badge


    def _is_level_over(self, board) -> bool:
        fine_cells = 0
        for cell in board:
            if cell["badge"] == "c0":
                if not cell.get("is_active"):
                    fine_cells += 1
            elif cell.get("is_active"):
                fine_cells += 1

        return fine_cells == len(board)

    def is_level_completed(self):
        return self._is_level_over(self.data["board"])

    def get_next_level_board(self):
        next_level = self.data["level"] + 1
        if next_level >= len(LEVELS):
            return self._level_to_new_board(random.choice(LEVELS[5:]))
        return self._level_to_new_board(LEVELS[next_level])


