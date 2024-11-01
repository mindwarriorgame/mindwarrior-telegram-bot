from typing import Optional, Tuple


INTERVAL_SECS = 16 * 3600;

class CatBadgeCounter:

    def on_game_started(self, active_play_time_secs: int, state: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        return None, "pending_superhappy," + str(active_play_time_secs + INTERVAL_SECS)

    def on_formula_updated(self, active_play_time_secs: int,  state: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        return None, state

    def on_prompt(self, active_play_time_secs: int, state: Optional[str])  -> Tuple[Optional[str], Optional[str]]:
        if state is None:
            return None, "pending_happy," + str(active_play_time_secs + INTERVAL_SECS)

        if state.startswith("pending_superhappy"):
            return None, state.replace("pending_superhappy", "pending_happy")

        return None, state


    def on_penalty(self, active_play_time_secs: int, state: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        return "c0", None

    def on_review(self, active_play_time_secs: int, state: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        if state is None:
            return None, "pending_superhappy," + str(active_play_time_secs + INTERVAL_SECS)

        split = state.split(",")
        fire_at_secs = int(split[1])

        if state.startswith("pending_happy") and fire_at_secs < active_play_time_secs:
            return "c1", "pending_superhappy," + str(active_play_time_secs + INTERVAL_SECS)

        if state.startswith("pending_superhappy") and fire_at_secs < active_play_time_secs:
            return "c2", "pending_superhappy," + str(active_play_time_secs + INTERVAL_SECS)

        return None, state

    def progress(self, for_badge, active_play_time_secs, state):
        if for_badge != "c1" and for_badge != "c2":
            return None, -1

        if state is None:
            if for_badge == "c1":
                return [{
                    "remaining_time_secs": INTERVAL_SECS,
                    "challenge": "review_regularly_no_penalty",
                    "badge": "c1"
                }], 0
            if for_badge == "c2":
                return [
                    {
                        "remaining_time_secs": INTERVAL_SECS,
                        "challenge": "review_regularly_no_penalty",
                        "badge" : "c1",
                    },
                    {
                        "remaining_time_secs": INTERVAL_SECS,
                        "challenge": "review_regularly_no_prompt",
                        "badge": "c2"
                    }
                ], 0
        if state.startswith("pending_happy"):
            split = state.split(",")
            secs_before_next_badge = max(int(split[1]) - active_play_time_secs, 0)
            secs_since_prev_badge = max(INTERVAL_SECS - secs_before_next_badge, 0)
            if for_badge == "c1":
                return [{
                    "remaining_time_secs": secs_before_next_badge,
                    "challenge": "review_regularly_no_penalty",
                    "badge": "c1"
                }], 100 * secs_since_prev_badge // INTERVAL_SECS
            if for_badge == "c2":
                return [
                    {
                        "remaining_time_secs": secs_before_next_badge,
                        "challenge": "review_regularly_no_penalty",
                        "badge": "c1"
                    },
                    {
                        "remaining_time_secs": INTERVAL_SECS,
                        "challenge": "review_regularly_no_prompt",
                        "badge": "c2"
                    }
                ], 100 * (secs_since_prev_badge + INTERVAL_SECS) // (2 * INTERVAL_SECS)
        if state.startswith("pending_superhappy"):
            split = state.split(",")

            secs_before_next_badge = max(int(split[1]) - active_play_time_secs, 0)
            secs_since_prev_badge = max(INTERVAL_SECS - secs_before_next_badge, 0)

            return [
                {
                    "remaining_time_secs": secs_before_next_badge,
                    "challenge": "review_regularly_no_penalty" if for_badge == "c1" else "review_regularly_no_prompt",
                    "badge": for_badge
                }
            ], 100 * secs_since_prev_badge // INTERVAL_SECS