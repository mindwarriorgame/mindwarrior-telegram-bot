from typing import Optional, Tuple


class StarBadgeCounter:

    def on_game_started(self, active_play_time_secs: int, state: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        return None, "0"

    def on_formula_updated(self, active_play_time_secs: int,  state: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        return None, state

    def on_prompt(self, active_play_time_secs: int, state: Optional[str])  -> Tuple[Optional[str], Optional[str]]:
        return None, state

    def on_penalty(self, active_play_time_secs: int, state: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        return None, "0"

    def on_review(self, active_play_time_secs: int, state: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        if state is None:
            state = "0"

        cnt = int(state)
        cnt += 1
        if cnt == 3:
            return "s0", str(cnt)
        if cnt == 6:
            return "s1", str(cnt)
        if (cnt % 9) == 0:
            return "s2", str(cnt)

        return None, str(cnt)
