from typing import Optional, Tuple

"""
s2 badge can be used when s1 is needed
"""
class StarBadgeCounter:

    def _frequency(self, difficulty):
        if difficulty == 0 or difficulty == 1:
            return 3
        if difficulty == 2 or difficulty == 3:
            return 5
        if difficulty == 4:
            return 7

        return 5

    def on_game_started(self, active_play_time_secs: int, state: Optional[str], difficulty, badges_locked_on_board: [str]) -> Tuple[Optional[str], Optional[str]]:
        if "s0" in badges_locked_on_board:
            return None, "0," + str(self._frequency(difficulty))
        if "s1" in badges_locked_on_board:
            return None, "0," + str(self._frequency(difficulty) * 2)
        if "s2" in badges_locked_on_board:
            return None, "0," + str(self._frequency(difficulty) * 3)
        return None, "0,100000"

    def on_formula_updated(self, active_play_time_secs: int,  state: Optional[str], difficulty, badges_locked_on_board: [str]) -> Tuple[Optional[str], Optional[str]]:
        return None, state

    def on_prompt(self, active_play_time_secs: int, state: Optional[str], difficulty, badges_locked_on_board: [str])  -> Tuple[Optional[str], Optional[str]]:
        return None, state

    def on_penalty(self, active_play_time_secs: int, state: Optional[str], difficulty, badges_locked_on_board: [str]) -> Tuple[Optional[str], Optional[str]]:
        if state is None:
            game_started_result = self.on_game_started(active_play_time_secs, state, difficulty, badges_locked_on_board)
            state = game_started_result[1]

        if "skip_next" in state:
            return None, state

        return None, state + ",skip_next"

    def on_review(self, active_play_time_secs: int, state: Optional[str], difficulty, badges_locked_on_board: [str]) -> Tuple[Optional[str], Optional[str]]:
        if "s0" not in badges_locked_on_board and "s1" not in badges_locked_on_board and "s2" not in badges_locked_on_board:
            return self.on_game_started(active_play_time_secs, state, difficulty, badges_locked_on_board)

        if state is None:
            game_started_result = self.on_game_started(active_play_time_secs, state, difficulty, badges_locked_on_board)
            state = game_started_result[1]

        if "skip_next" in state:
            return None, state.replace(",skip_next", "")

        cnt, threshold = state.split(",")

        cnt = int(cnt) + 1
        threshold = int(threshold)

        if cnt >= threshold:
            give_away_star = self._find_smallest_star(badges_locked_on_board)
            badges_without_star = self._remove_star_from_board(badges_locked_on_board)
            game_started_result = self.on_game_started(active_play_time_secs, None, difficulty, badges_without_star)
            return give_away_star, game_started_result[1]

        return None, str(cnt) + "," + str(threshold)

    def _find_smallest_star(self, badges_locked_on_board: [str]):
        for candidate in ["s0", "s1", "s2"]:
            if candidate in badges_locked_on_board:
                return candidate

    def _remove_star_from_board(self, badges_locked_on_board: [str]):
        new_board = badges_locked_on_board.copy()
        for candidate in ["s0", "s1", "s2"]:
            if candidate in new_board:
                new_board.remove(candidate)
                return new_board

    def progress(self, for_badge, active_play_time_secs, state, difficulty, badges_locked_on_board: [str]):
        if for_badge != "s0" and for_badge != "s1" and for_badge != "s2":
            return None

        if state is None:
            game_started_result = self.on_game_started(active_play_time_secs, state, difficulty, badges_locked_on_board)
            state = game_started_result[1]

        min_on_board = self._find_smallest_star(badges_locked_on_board)
        if min_on_board != for_badge:
            return None

        cnt, threshold = state.split(",") if "skip_next" not in state else state.replace(",skip_next", "").split(",")
        cnt = int(cnt)
        threshold = int(threshold)

        return {
            "remaining_reviews": threshold - cnt,
            "challenge": "review_regularly_no_penalty",
            "badge": min_on_board,
            "progress_pct": min(cnt * 100 // threshold, 100)
        }
