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

    c0_hp_next_delta: int
    c0_hp: int

class BadgesManager:

    def __init__(self, difficulty, badges_serialized = None):
        self.difficulty = difficulty
        if badges_serialized is None or badges_serialized == "":
            self.data = UserBadgesData(badges_state={}, board=self._level_to_new_board(LEVELS[0]), level=0, c0_hp=0, c0_hp_next_delta=3, last_badge=None)
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

        if not self.data.get("c0_hp_next_delta"):
            self.data["c0_hp_next_delta"] = 3

        if not self.data.get("c0_hp"):
            self.data["c0_hp"] = 0
            for cell in self.data["board"]:
                if cell["badge"] == "c0" and cell.get("is_active"):
                    self.data["c0_hp"] = self._max_grumpy_cat_healthpoints()

    def _max_grumpy_cat_healthpoints(self):
        return 5 * (self.difficulty + 1)

    def on_game_started(self, active_play_time_secs: float) -> Optional[str]:
        # "terminate_if_found" is False we need to initialize all counters. That's a rare case when two badges might be have given
        # on start; we should be OK picking the first one.
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

            if self.data["c0_hp"] == 0:
                self._kick_off_grump_cat()
                if self.count_active_grumpy_cats_on_board() > 0:
                    self.data["c0_hp"] = self._max_grumpy_cat_healthpoints()

                return "c0_removed"

        return self._chain_badge_counters("on_review", int(active_play_time_secs), True)

    def get_grumpy_cat_healthpoints(self):
        return self.data["c0_hp"]

    def get_level(self):
        return self.data["level"]

    def get_board(self):
        return self.data["board"]

    def get_last_badge(self):
        return self.data.get("last_badge")

    def _kick_off_grump_cat(self):
        self.data["board"] = self._expel_grumpy_cat(self.data["board"])

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

        if self._is_level_over(self.data["board"]):
            self.data["level"] += 1
            self.data["board"] = self._level_to_new_board(LEVELS[self.data["level"]])
            self.data["last_badge"] = None
            self.data["badges_state"] = {}
            for counter in counters:
                badge, new_state = counter.on_game_started(active_play_time_secs, None, self.difficulty, self._get_inactive_badges_on_board(self.data['board']))
                self.data["badges_state"][counter.__class__.__name__] = new_state

        badge_to_put_on_board = None
        has_grumpy_cat = (self.count_active_grumpy_cats_on_board() > 0)
        for counter in counters:
            state = None
            if self.data["badges_state"].get(counter.__class__.__name__) is not None:
                state = self.data["badges_state"][counter.__class__.__name__]

            if has_grumpy_cat and method_name != "on_penalty":
                # Grumpy cat should spoil everything, except of penalty (which will work as usually to make sure all
                # c0 cells will be filled up)
                _, state = counter.on_penalty(active_play_time_secs, state, self.difficulty, self._get_inactive_badges_on_board(self.data['board']))
                self.data["badges_state"][counter.__class__.__name__] = state
                continue

            method = getattr(counter, method_name)
            badge, new_state = method(active_play_time_secs, state, self.difficulty, self._get_inactive_badges_on_board(self.data['board']))

            self.data["badges_state"][counter.__class__.__name__] = new_state

            if badge is not None and badge_to_put_on_board is None:
                badge_to_put_on_board = badge
                if terminate_if_found:
                    break

        if badge_to_put_on_board:
            self.data["board"], self.data["last_badge"] = self._put_badge_to_board(badge_to_put_on_board)

            if self.data["last_badge"] == "c0" and self.data["c0_hp"] == 0:
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
                    maybe_progress = counter.progress(badge, int(active_play_time_secs), self.data["badges_state"].get(counter.__class__.__name__), self.difficulty, self._get_inactive_badges_on_board(self.data['board']))

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
        for counter in counters:
            for badge in badges:
                maybe_progress = counter.progress(badge, 0, None, self.difficulty, self._get_inactive_badges_on_board(self.get_next_level_board()))
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


