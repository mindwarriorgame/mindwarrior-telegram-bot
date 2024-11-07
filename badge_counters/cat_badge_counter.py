from typing import Optional, Tuple


INTERVAL_SECS = 16 * 3600

"""
c2 badge can be used when c2 is needed
c0 is for penalty only (special case)
"""
class CatBadgeCounter:

    def _calculate_interval_secs(self, difficulty):
        koef = [0.5, 0.75, 1, 1.25, 1.5]
        return round(INTERVAL_SECS * koef[difficulty])

    def on_game_started(self, active_play_time_secs: int, state: Optional[str], difficulty, badges_locked_on_board: [str]) -> Tuple[Optional[str], Optional[str]]:
        return None, str(active_play_time_secs + self._calculate_interval_secs(difficulty))

    def on_formula_updated(self, active_play_time_secs: int,  state: Optional[str], difficulty, badges_locked_on_board: [str]) -> Tuple[Optional[str], Optional[str]]:
        return None, state

    def on_prompt(self, active_play_time_secs: int, state: Optional[str], difficulty, badges_locked_on_board: [str])  -> Tuple[Optional[str], Optional[str]]:
        if state is None:
            state = str(active_play_time_secs + self._calculate_interval_secs(difficulty))

        if "c1" in badges_locked_on_board:
            return None, state

        if "c2" in badges_locked_on_board:
            return None, str(active_play_time_secs + self._calculate_interval_secs(difficulty))

        return None, state


    def on_penalty(self, active_play_time_secs: int, state: Optional[str], difficulty, badges_locked_on_board: [str]) -> Tuple[Optional[str], Optional[str]]:
        if state is None:
            state = str(active_play_time_secs + self._calculate_interval_secs(difficulty))

        return "c0", str(active_play_time_secs + self._calculate_interval_secs(difficulty))

    def on_review(self, active_play_time_secs: int, state: Optional[str], difficulty, badges_locked_on_board: [str]) -> Tuple[Optional[str], Optional[str]]:
        if state is None:
            return None, str(active_play_time_secs + self._calculate_interval_secs(difficulty))

        fire_at_secs = int(state)

        if "c1" in badges_locked_on_board and fire_at_secs < active_play_time_secs:
            return "c1", str(active_play_time_secs + self._calculate_interval_secs(difficulty))

        if "c2" in badges_locked_on_board and fire_at_secs < active_play_time_secs:
            return "c2", str(active_play_time_secs + self._calculate_interval_secs(difficulty))

        return None, state

    def progress(self, for_badge, active_play_time_secs, state, difficulty, badges_locked_on_board: [str]):
        if for_badge != "c1" and for_badge != "c2":
            return None

        if state is None:
            state = str(active_play_time_secs + self._calculate_interval_secs(difficulty))

        fire_at_secs = int(state)
        secs_before_next_badge = max(fire_at_secs - active_play_time_secs, 0)
        secs_since_prev_badge = max(self._calculate_interval_secs(difficulty) - secs_before_next_badge, 0)

        if "c1" in badges_locked_on_board:
            if for_badge == "c1":
                return {
                    "remaining_time_secs": secs_before_next_badge,
                    "challenge": "review_regularly_no_penalty",
                    "badge": "c1",
                    "progress_pct": 100 * secs_since_prev_badge // self._calculate_interval_secs(difficulty)
                }

            if for_badge == "c2":
                return None

        if "c2" in badges_locked_on_board:
            if for_badge == "c1":
                return None

            if for_badge == "c2":
                return {
                    "remaining_time_secs": secs_before_next_badge,
                    "challenge": "review_regularly_no_prompt",
                    "badge": "c2",
                    "progress_pct": 100 * secs_since_prev_badge // self._calculate_interval_secs(difficulty)
                }