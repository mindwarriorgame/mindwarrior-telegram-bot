from typing import Optional, Tuple



class CatBadgeCounter:

    def on_game_started(self, active_play_time_secs: int, state: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        return None, "pending_superhappy,0"

    def on_formula_updated(self, active_play_time_secs: int,  state: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        return None, state

    def on_prompt(self, active_play_time_secs: int, state: Optional[str])  -> Tuple[Optional[str], Optional[str]]:
        if state is None:
            return None, "pending_happy," + str(active_play_time_secs)

        if state.startswith("pending_superhappy"):
            return None, state.replace("pending_superhappy", "pending_happy")

        return None, state

    def on_penalty(self, active_play_time_secs: int, state: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        return "c0", None

    def on_review(self, active_play_time_secs: int, state: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        if state is None:
            return None, "pending_superhappy," + str(active_play_time_secs)

        split = state.split(",")
        time_passed = active_play_time_secs - int(split[1])

        if state.startswith("pending_happy") and time_passed > 16 * 3600:
            return "c1", "pending_superhappy," + str(active_play_time_secs)

        if state.startswith("pending_superhappy") and time_passed > 16 * 3600:
            return "c2", "pending_superhappy," + str(active_play_time_secs)

        return None, state