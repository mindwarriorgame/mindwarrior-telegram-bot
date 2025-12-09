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

    def on_game_started(self, active_play_time_secs: int, state: Optional[str], difficulty, badges_locked_on_board: list[str]) -> Tuple[Optional[str], Optional[str]]:
        return None, self._generate_state(0, active_play_time_secs, "game_started")

    def _get_cumulative_counter_secs(self, state: str) -> int:
        return int(float(state.split(",")[0].split("=")[1]))

    def _get_counter_last_updated(self, state: str) -> int:
        return int(float(state.split(",")[1].split("=")[1]))

    def _get_update_reason(self, state: str) -> str:
        return state.split(",")[2].split("=")[1]

    def _generate_state(self, cumulative_counter_secs: int, counter_last_updated: int, update_reason: str) -> str:
        return "cumulative_counter_secs=" + str(cumulative_counter_secs) + ",counter_last_updated=" + str(counter_last_updated) + ",update_reason=" + update_reason

    def on_formula_updated(self, active_play_time_secs: int,  state: Optional[str], difficulty, badges_locked_on_board: list[str]) -> Tuple[Optional[str], Optional[str]]:
        return None, state

    def on_prompt(self, active_play_time_secs: int, state: Optional[str], difficulty, badges_locked_on_board: list[str])  -> Tuple[Optional[str], Optional[str]]:
        if state is None:
            _, state = self.on_game_started(active_play_time_secs, state, difficulty, badges_locked_on_board)
        if state is None:
            raise Exception("should never happen, for typecasting")

        if "c1" in badges_locked_on_board:
            return None, state

        if "c2" in badges_locked_on_board:
            return None, self._generate_state(self._get_cumulative_counter_secs(state), active_play_time_secs, "prompt")

        return None, state


    def on_penalty(self, active_play_time_secs: int, state: Optional[str], difficulty, badges_locked_on_board: list[str]) -> Tuple[Optional[str], Optional[str]]:
        if state is None:
            _, state = self.on_game_started(active_play_time_secs, state, difficulty, badges_locked_on_board)
        if state is None:
            raise Exception("should never happen, for typecasting")

        return "c0" if difficulty >= 1 else None, self._generate_state(self._get_cumulative_counter_secs(state), active_play_time_secs, "penalty")

    def on_review(self, active_play_time_secs: int, state: Optional[str], difficulty, badges_locked_on_board: list[str]) -> Tuple[Optional[str], Optional[str]]:
        if state is None:
            return self.on_game_started(active_play_time_secs, state, difficulty, badges_locked_on_board)

        cumulative_counter_secs = self._get_cumulative_counter_secs(state)
        counter_last_updated = self._get_counter_last_updated(state)
        last_update_reason = self._get_update_reason(state)

        if "c1" in badges_locked_on_board:
            if last_update_reason == "penalty":
                return None, self._generate_state(cumulative_counter_secs, active_play_time_secs, "review")

            cumulative_counter_secs += active_play_time_secs - counter_last_updated
            if cumulative_counter_secs >= self._calculate_interval_secs(difficulty):
                return "c1", self._generate_state(0, active_play_time_secs, "review")

            return None, self._generate_state(cumulative_counter_secs, active_play_time_secs, "review")


        if "c2" in badges_locked_on_board:
            if last_update_reason == "prompt" or last_update_reason == "penalty":
                return None, self._generate_state(cumulative_counter_secs, active_play_time_secs, "review")

            cumulative_counter_secs += active_play_time_secs - counter_last_updated
            if cumulative_counter_secs >= self._calculate_interval_secs(difficulty):
                return "c2", self._generate_state(0, active_play_time_secs, "review")

            return None, self._generate_state(cumulative_counter_secs, active_play_time_secs, "review")

        return None, state

    def progress(self, for_badge, active_play_time_secs, state, difficulty, badges_locked_on_board: list[str]):
        if for_badge != "c1" and for_badge != "c2":
            return None

        if state is None:
            _, state = self.on_game_started(active_play_time_secs, state, difficulty, badges_locked_on_board)
        
        if state is None:
            raise Exception("should never happen (called on_game_started above), for typecasting")

        cumulative_counter_secs = self._get_cumulative_counter_secs(state)

        if "c1" in badges_locked_on_board:

            remaining_time_secs = max(self._calculate_interval_secs(difficulty) - cumulative_counter_secs, 0)
            progress_pct = 100 - 100 * remaining_time_secs // self._calculate_interval_secs(difficulty)

            if for_badge == "c1":
                return {
                    "remaining_time_secs": remaining_time_secs,
                    "challenge": "review_regularly_no_penalty",
                    "badge": "c1",
                    "progress_pct": progress_pct
                }

            if for_badge == "c2":
                return None

        if "c2" in badges_locked_on_board:

            remaining_time_secs = max(self._calculate_interval_secs(difficulty) - cumulative_counter_secs, 0)
            progress_pct = 100 - 100 * remaining_time_secs // self._calculate_interval_secs(difficulty)

            if for_badge == "c1":
                return None

            if for_badge == "c2":
                return {
                    "remaining_time_secs": remaining_time_secs,
                    "challenge": "review_regularly_no_prompt",
                    "badge": "c2",
                    "progress_pct": progress_pct
                }
