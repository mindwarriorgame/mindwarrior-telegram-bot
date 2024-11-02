from typing import Optional, Tuple


INTERVAL_SECS = 16 * 3600

class CatBadgeCounter:

    def _calculate_interval_secs(self, difficulty):
        koef = [0.5, 0.75, 1, 1.25, 1.5]
        return round(INTERVAL_SECS * koef[difficulty])

    def on_game_started(self, active_play_time_secs: int, state: Optional[str], difficulty) -> Tuple[Optional[str], Optional[str]]:
        return None, "pending_happy," + str(active_play_time_secs + self._calculate_interval_secs(difficulty))

    def on_formula_updated(self, active_play_time_secs: int,  state: Optional[str], difficulty) -> Tuple[Optional[str], Optional[str]]:
        return None, state

    def on_prompt(self, active_play_time_secs: int, state: Optional[str], difficulty)  -> Tuple[Optional[str], Optional[str]]:
        if state is None:
            return None, "pending_happy," + str(active_play_time_secs + self._calculate_interval_secs(difficulty))

        if state.startswith("pending_superhappy"):
            return None, state.replace("pending_superhappy", "pending_happy")

        return None, state


    def on_penalty(self, active_play_time_secs: int, state: Optional[str], difficulty) -> Tuple[Optional[str], Optional[str]]:
        return "c0", "pending_happy," + str(active_play_time_secs + self._calculate_interval_secs(difficulty))

    def on_review(self, active_play_time_secs: int, state: Optional[str], difficulty) -> Tuple[Optional[str], Optional[str]]:
        if state is None:
            return None, "pending_happy," + str(active_play_time_secs + self._calculate_interval_secs(difficulty))

        split = state.split(",")
        fire_at_secs = int(split[1])

        if state.startswith("pending_happy") and fire_at_secs < active_play_time_secs:
            return "c1", "pending_superhappy," + str(active_play_time_secs + self._calculate_interval_secs(difficulty))

        if state.startswith("pending_superhappy") and fire_at_secs < active_play_time_secs:
            return "c2", "pending_superhappy," + str(active_play_time_secs + self._calculate_interval_secs(difficulty))

        return None, state

    def progress(self, for_badge, active_play_time_secs, state, difficulty):
        if for_badge != "c1" and for_badge != "c2":
            return None, -1

        if state is None:
            if for_badge == "c1":
                return [{
                    "remaining_time_secs": self._calculate_interval_secs(difficulty),
                    "challenge": "review_regularly_no_penalty",
                    "badge": "c1",
                    "progress_pct": 0
                }]
            if for_badge == "c2":
                return [
                    {
                        "remaining_time_secs": self._calculate_interval_secs(difficulty),
                        "challenge": "review_regularly_no_penalty",
                        "badge" : "c1",
                        "progress_pct": 0
                    },
                    {
                        "remaining_time_secs": self._calculate_interval_secs(difficulty),
                        "challenge": "review_regularly_no_prompt",
                        "badge": "c2",
                        "progress_pct": 0
                    }
                ]
        if state.startswith("pending_happy"):
            split = state.split(",")
            secs_before_next_badge = max(int(split[1]) - active_play_time_secs, 0)
            secs_since_prev_badge = max(self._calculate_interval_secs(difficulty) - secs_before_next_badge, 0)
            if for_badge == "c1":
                return [{
                    "remaining_time_secs": secs_before_next_badge,
                    "challenge": "review_regularly_no_penalty",
                    "badge": "c1",
                    "progress_pct": 100 * secs_since_prev_badge // self._calculate_interval_secs(difficulty)
                }]
            if for_badge == "c2":
                return [
                    {
                        "remaining_time_secs": secs_before_next_badge,
                        "challenge": "review_regularly_no_penalty",
                        "badge": "c1",
                        "progress_pct": 100 * secs_since_prev_badge // self._calculate_interval_secs(difficulty)
                    },
                    {
                        "remaining_time_secs": self._calculate_interval_secs(difficulty),
                        "challenge": "review_regularly_no_prompt",
                        "badge": "c2",
                        "progress_pct": 0
                    }
                ]
        if state.startswith("pending_superhappy"):
            split = state.split(",")

            secs_before_next_badge = max(int(split[1]) - active_play_time_secs, 0)
            secs_since_prev_badge = max(self._calculate_interval_secs(difficulty) - secs_before_next_badge, 0)

            if for_badge == "c1":
                return [
                    {
                        "remaining_time_secs": secs_before_next_badge,
                        "challenge": "review_regularly_no_penalty",
                        "badge": for_badge,
                        "progress_pct": 100 * secs_since_prev_badge // self._calculate_interval_secs(difficulty)
                    }
                ]

            if for_badge == "c2":
                return [
                    {
                        "remaining_time_secs": 0,
                        "challenge": "review_regularly_no_penalty",
                        "badge": "c1",
                        "progress_pct": 100
                    },
                    {
                        "remaining_time_secs": secs_before_next_badge,
                        "challenge": "review_regularly_no_prompt",
                        "badge": for_badge,
                        "progress_pct": 100 * secs_since_prev_badge // self._calculate_interval_secs(difficulty)
                    }
                ]