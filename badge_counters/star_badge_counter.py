from typing import Optional, Tuple

"""
s2 badge can be used when s1 is needed
"""
class StarBadgeCounter:

    def _frequency(self, difficulty):
        if difficulty == 0 or difficulty == 1:
            return 2
        if difficulty == 2 or difficulty == 3:
            return 3
        if difficulty == 4:
            return 4

        return 5

    def on_game_started(self, active_play_time_secs: int, state: Optional[str], difficulty) -> Tuple[Optional[str], Optional[str]]:
        return None, "0"

    def on_formula_updated(self, active_play_time_secs: int,  state: Optional[str], difficulty) -> Tuple[Optional[str], Optional[str]]:
        return None, state

    def on_prompt(self, active_play_time_secs: int, state: Optional[str], difficulty)  -> Tuple[Optional[str], Optional[str]]:
        return None, state

    def on_penalty(self, active_play_time_secs: int, state: Optional[str], difficulty) -> Tuple[Optional[str], Optional[str]]:
        return None, "0"

    def on_review(self, active_play_time_secs: int, state: Optional[str], difficulty) -> Tuple[Optional[str], Optional[str]]:
        if state is None:
            state = "0"

        cnt = int(state)
        cnt += 1

        thres_s0 = self._frequency(difficulty)
        thres_s1 = self._frequency(difficulty) * 2
        thres_s2 = self._frequency(difficulty) * 3

        if (cnt % thres_s2) == 0:
            return "s2", str(cnt)
        if (cnt % thres_s2) == thres_s1:
            return "s1", str(cnt)
        if (cnt % thres_s2) == thres_s0:
            return "s0", str(cnt)

        return None, str(cnt)

    def progress(self, for_badge, active_play_time_secs, state, difficulty):
        if for_badge != "s0" and for_badge != "s1" and for_badge != "s2":
            return None

        cnt = 0
        if state is not None:
            cnt = int(state)

        thres_s0 = self._frequency(difficulty)
        thres_s1 = self._frequency(difficulty) * 2
        thres_s2 = self._frequency(difficulty) * 3

        if for_badge == "s0":
            return [{
                "remaining_reviews": thres_s0 - (cnt % thres_s0),
                "challenge": "review_regularly_no_penalty",
                "badge": "s0",
                "progress_pct": 100 * (cnt % thres_s0) // thres_s0
            }]


        if for_badge == "s1":
            if (cnt % thres_s2) < thres_s1:
                return [{
                    "remaining_reviews": thres_s1 - (cnt % thres_s2),
                    "challenge": "review_regularly_no_penalty",
                    "badge": "s1",
                    "progress_pct": (cnt % thres_s2) * 100 // thres_s1
                }]

            return [{
                "remaining_reviews": thres_s2 - (cnt % thres_s2),
                "challenge": "review_regularly_no_penalty",
                "badge": "s1",
                "progress_pct": 100 * (cnt % thres_s2) // thres_s2
            }]

        if for_badge == "s2":

            return [{
                "remaining_reviews": thres_s2 - (cnt % thres_s2),
                "challenge": "review_regularly_no_penalty",
                "badge": "s2",
                "progress_pct": 100 * (cnt % thres_s2) // thres_s2
            }]