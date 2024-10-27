from typing import Optional, Tuple


class FeatherBadgeCounter:

    def on_game_started(self, active_play_time_secs: int, state: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        return "feather", "0"

    def on_formula_updated(self, active_play_time_secs: int,  state: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        if state is None:
            return "feather", str(active_play_time_secs)

        last_time_at = int(state)
        if active_play_time_secs - last_time_at > 24 * 3600:
            return "feather", str(active_play_time_secs)
        return None, state

    def on_prompt(self, active_play_time_secs: int, state: Optional[str])  -> Tuple[Optional[str], Optional[str]]:
        return None, state

    def on_penalty(self, active_play_time_secs: int, state: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        return None, state

    def on_review(self, active_play_time_secs: int, state: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        return None, state