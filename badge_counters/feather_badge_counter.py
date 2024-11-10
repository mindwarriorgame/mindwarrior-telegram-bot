from typing import Optional, Tuple

INTERVAL_SECS = 24 * 3600

class FeatherBadgeCounter:

    def _calculate_interval_secs(self, difficulty):
        koef = [0.5, 0.75, 1, 1.25, 1.5]
        return round(INTERVAL_SECS * koef[difficulty])

    def on_game_started(self, active_play_time_secs: int, state: Optional[str], difficulty, badges_locked_on_board: [str]) -> Tuple[Optional[str], Optional[str]]:
        if "f0" in badges_locked_on_board:
            return "f0", str(active_play_time_secs + self._calculate_interval_secs(difficulty))
        return None, str(active_play_time_secs + self._calculate_interval_secs(difficulty))

    def on_formula_updated(self, active_play_time_secs: int,  state: Optional[str], difficulty, badges_locked_on_board: [str]) -> Tuple[Optional[str], Optional[str]]:
        if "f0" not in badges_locked_on_board:
            return None, state

        if state is None:
            return None, str(active_play_time_secs + self._calculate_interval_secs(difficulty))

        time_to_fire = int(state)
        if time_to_fire < active_play_time_secs:
            return "f0", str(active_play_time_secs + self._calculate_interval_secs(difficulty))

        return None, state

    def on_prompt(self, active_play_time_secs: int, state: Optional[str], difficulty, badges_locked_on_board: [str])  -> Tuple[Optional[str], Optional[str]]:
        return None, state

    def on_penalty(self, active_play_time_secs: int, state: Optional[str], difficulty, badges_locked_on_board: [str]) -> Tuple[Optional[str], Optional[str]]:
        return None, state

    def on_review(self, active_play_time_secs: int, state: Optional[str], difficulty, badges_locked_on_board: [str]) -> Tuple[Optional[str], Optional[str]]:
        return None, state

    def progress(self, for_badge, active_play_time_secs, state, difficulty, badges_locked_on_board: [str]):
        if for_badge != "f0":
            return None

        if "f0" not in badges_locked_on_board:
            return None

        if state is None:
            state = str(active_play_time_secs + self._calculate_interval_secs(difficulty))

        time_to_fire = int(state)

        time_left = max(time_to_fire - active_play_time_secs, 0)
        time_passed = max(self._calculate_interval_secs(difficulty) - time_left, 0)

        return {
            "remaining_time_secs": time_left,
            "challenge": "update_formula",
            "badge": "f0",
            "progress_pct": min(100 * time_passed // self._calculate_interval_secs(difficulty), 100)
        }