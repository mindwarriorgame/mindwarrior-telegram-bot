import json
from typing import TypedDict, Optional

from badge_counters.cat_badge_counter import CatBadgeCounter
from badge_counters.feather_badge_counter import FeatherBadgeCounter
from badge_counters.star_badge_counter import StarBadgeCounter
from badge_counters.time_badge_counter import TimeBadgeCounter


class UserBadgesData(TypedDict):
    badges_counter: dict[str, int]
    badges_state: dict[str, str]

class BadgesManager:

    def __init__(self, badges_serialized):
        if badges_serialized is None or badges_serialized == "":
            self.data = UserBadgesData(badges_counter={}, badges_state={})
        else:
            self.data = UserBadgesData(**json.loads(badges_serialized))


    def on_game_started(self, active_play_time_secs: float) -> Optional[str]:
        return self._chain_badge_counters("on_game_started", int(active_play_time_secs))

    def on_formula_updated(self, active_play_time_secs: float) -> Optional[str]:
        return self._chain_badge_counters("on_formula_updated", int(active_play_time_secs))

    def on_prompt(self, active_play_time_secs: float) -> Optional[str]:
        return self._chain_badge_counters("on_prompt", int(active_play_time_secs))

    def on_penalty(self, active_play_time_secs: float) -> Optional[str]:
        return self._chain_badge_counters("on_penalty", int(active_play_time_secs))

    def on_review(self, active_play_time_secs: float) -> Optional[str]:
        return self._chain_badge_counters("on_review", int(active_play_time_secs), True)

    def _chain_badge_counters(self, method_name, active_play_time_secs: int, terminate_if_found = False) -> Optional[str]:
        counters = [
            CatBadgeCounter(),
            TimeBadgeCounter(),
            StarBadgeCounter(),
            FeatherBadgeCounter()
        ]

        badge_to_return = None
        for counter in counters:
            state = None
            if self.data["badges_state"].get(counter.__class__.__name__) is not None:
                state = self.data["badges_state"][counter.__class__.__name__]

            method = getattr(counter, method_name)
            badge, new_state = method(active_play_time_secs, state)
            self.data["badges_state"][counter.__class__.__name__] = new_state

            if badge is not None and badge_to_return is None:
                self.data["badges_counter"][badge] = self.data["badges_counter"].get(badge, 0) + 1
                badge_to_return = badge
                if terminate_if_found:
                    return badge_to_return

        return badge_to_return

    def serialize(self) -> str:
        return json.dumps(self.data)