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
    is_active: NotRequired[bool]
    is_target: NotRequired[bool]
    projectile_override: NotRequired[str] # for c0 only

class UserBadgesData(TypedDict):
    badges_state: dict[str, str]
    last_badge: Optional[str]
    level: int
    board: list[BoardCell]

class BadgesManager:

    def __init__(self, badges_serialized = None):
        if badges_serialized is None or badges_serialized == "":
            self.data = UserBadgesData(badges_state={}, board=self._level_to_new_board(LEVELS[0]), level=1)
        else:
            self.data = UserBadgesData(**json.loads(badges_serialized))

    def on_game_started(self, active_play_time_secs: float, difficulty: int) -> Optional[str]:
        return self._chain_badge_counters("on_game_started", int(active_play_time_secs), difficulty)

    def on_formula_updated(self, active_play_time_secs: float, difficulty: int) -> Optional[str]:
        return self._chain_badge_counters("on_formula_updated", int(active_play_time_secs), difficulty)

    def on_prompt(self, active_play_time_secs: float, difficulty: int) -> Optional[str]:
        return self._chain_badge_counters("on_prompt", int(active_play_time_secs), difficulty)

    def on_penalty(self, active_play_time_secs: float, difficulty: int) -> Optional[str]:
        return self._chain_badge_counters("on_penalty", int(active_play_time_secs), difficulty)

    def on_review(self, active_play_time_secs: float, difficulty: int) -> Optional[str]:
        return self._chain_badge_counters("on_review", int(active_play_time_secs), difficulty, True)

    def get_level(self):
        return self.data["level"]

    def get_board(self):
        return self.data["board"]

    def get_last_badge(self):
        return self.data.get("last_badge")

    def _chain_badge_counters(self, method_name, active_play_time_secs: int, difficulty: int, terminate_if_found = False) -> Optional[str]:
        counters = [
            CatBadgeCounter(),
            TimeBadgeCounter(),
            StarBadgeCounter(),
            FeatherBadgeCounter()
        ]

        if self._is_level_over(self.data["board"]):
            self.data["level"] += 1
            self.data["board"] = self._level_to_new_board(LEVELS[self.data["level"] - 1])
            self.data["badges_state"] = {}
            for counter in counters:
                badge, new_state = counter.on_game_started(active_play_time_secs, None, difficulty)
                self.data["badges_state"][counter.__class__.__name__] = new_state

        badge_to_return = None
        has_grumpy_cat = self._has_grump_cats_on_board(self.data["board"])
        for counter in counters:
            state = None
            if self.data["badges_state"].get(counter.__class__.__name__) is not None:
                state = self.data["badges_state"][counter.__class__.__name__]

            method = getattr(counter, method_name)
            badge, new_state = method(active_play_time_secs, state, difficulty)

            # Grumpy cat is always the first badge to kick out, and the badge that was used for it
            # shouldn't be accommodated for anything else
            if has_grumpy_cat:
                if badge:
                    badge_to_return = badge
                    break
                continue

            self.data["badges_state"][counter.__class__.__name__] = new_state

            if badge is not None and badge_to_return is None:
                badge_to_return = badge
                if terminate_if_found:
                    break

        self.data["last_badge"] = badge_to_return
        self.data["board"] = self._put_badge_to_board(badge_to_return)

        return badge_to_return

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
                maybe_progress = counter.progress(badge, int(active_play_time_secs), self.data["badges_state"][counter.__class__.__name__], difficulty)
                if maybe_progress is not None:
                    all_progress[badge] = maybe_progress

        return all_progress


    def serialize(self) -> str:
        return json.dumps(self.data)

    def _normalize_board(self, board):
        normalized_board: [BoardCell] = []
        for cell in board:
            normalized_cell: BoardCell = {
                "badge": cell["badge"],
            }
            if cell.get("is_target"):
                normalized_cell["is_active"] = not cell.get("is_active")
            else:
                normalized_cell["is_active"] = cell.get("is_active")

            normalized_board.append(normalized_cell)
        return normalized_board

    def _level_to_new_board(self, level) -> [BoardCell]:
        board = []
        for badge in level:
            board.append({
                "badge": badge,
            })
        return board

    def _put_grumpy_cat_to_board(self, normalized_board: [BoardCell]):
        for cell in normalized_board:
            if cell["badge"] == "c0" and not cell.get("is_active"):
                cell["is_target"] = True
                break
        return normalized_board

    def _has_grump_cats_on_board(self, normalized_board):
        for cell in normalized_board:
            if cell["badge"] == "c0" and cell.get("is_active"):
                return True
        return False

    def _expell_grumpy_cat(self, normalized_board, badge):
        for cell in normalized_board:
            if cell["badge"] == "c0" and cell.get("is_active"):
                cell["is_target"] = True
                cell["projectile_override"] = badge
                break
        return normalized_board

    def _has_closed_badge_on_board(self, normalized_board, badge):
        for cell in normalized_board:
            if cell["badge"] == badge and not cell.get("is_active"):
                return True
        return False

    def _open_badge(self, normalized_board, badge):
        for cell in normalized_board:
            if cell["badge"] == badge and not cell.get("is_active"):
                cell["is_target"] = True
                break
        return normalized_board

    def _put_badge_to_board(self, badge):

        overwrites = [["s2", "s1"], ["s2", "s0"], ["s1", "s0"], ["c2", "c1"]]

        if badge is None:
            return self.data["board"]
        normalized_board = self._normalize_board(self.data["board"])

        if badge == "c0":
            return self._put_grumpy_cat_to_board(normalized_board)

        if self._has_grump_cats_on_board(normalized_board):
            return self._expell_grumpy_cat(normalized_board, badge)

        if self._has_closed_badge_on_board(normalized_board, badge):
            return self._open_badge(normalized_board, badge)

        for overwrite in overwrites:
            senior_badge = overwrite[0]
            junior_badge = overwrite[1]
            if badge == senior_badge and self._has_closed_badge_on_board(normalized_board, junior_badge):
                return self._open_badge(normalized_board, junior_badge)

        return normalized_board


    def _is_level_over(self, board) -> bool:
        normalized_board = self._normalize_board(board)
        fine_cells = 0
        for cell in normalized_board:
            if cell["badge"] == "c0":
                if not cell.get("is_active"):
                    fine_cells += 1
            elif cell.get("is_active"):
                fine_cells += 1


        return fine_cells == len(normalized_board)

    def is_level_completed(self):
        return self._is_level_over(self.data["board"])
