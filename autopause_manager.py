import datetime
import json
from typing import TypedDict
from zoneinfo import ZoneInfo
from fuzzywuzzy import fuzz
import zoneinfo


class AutopauseConfig(TypedDict):
    is_enabled: bool
    start_at_mins_in_user_tz: int
    stop_at_mins_in_user_tz: int # may be more than 24 hours to indicate next day
    user_timezone: str # correct timezone string; use detect_timezone() to find it from user's input
    calculated_next_or_current_interval_start_at: int
    calculated_next_or_current_interval_stop_at: int

# Quite expensive operation, use only to sanitize user input
# utcoffset_secs is a positive offset (that is, Sydney's time is either +10*3600 or +11*3600)
def detect_timezone(tz_name: str, utcoffset_secs: int):
    try:
        return ZoneInfo(tz_name).key
    except:
        timezones = list(zoneinfo.available_timezones())
        timezones_by_offset_diff = {}
        min_diff = 10 * 3600
        for tz in timezones:
            offset = zoneinfo.ZoneInfo(tz).utcoffset(datetime.datetime.now()).total_seconds()
            offset_diff = abs(offset - utcoffset_secs)
            if offset_diff < min_diff:
                min_diff = offset_diff
            if timezones_by_offset_diff.get(offset_diff) is None:
                timezones_by_offset_diff[offset_diff] = [tz]
            else:
                timezones_by_offset_diff[offset_diff].append(tz)

        candidate_tzs = timezones_by_offset_diff[min_diff]
        found_tz = None
        found_tz_score = 0
        for tz in candidate_tzs:
            score = fuzz.ratio(tz, tz_name)
            if score > found_tz_score:
                found_tz = tz
                found_tz_score = score

        return found_tz


class AutopauseManager:
    def __init__(self, state):
        if state is not None:
            self.data = json.loads(state)
        else:
            self.data = {
                "is_enabled": False,
                "start_at_mins_in_user_tz": 0,
                "stop_at_mins_in_user_tz": 0,
                "timezone": "UTC",
                "utcoffset_secs" : 0
            }
        self._refresh_calculated_intervals()

    def serialize(self) -> str:
        return json.dumps(self.data)

    def update(self, is_enabled, user_tz_string, user_tz_offset_secs, start_at_mins_in_user_tz, stop_at_mins_in_user_tz):
        self.data["is_enabled"] = is_enabled
        if is_enabled:
            tz = detect_timezone(user_tz_string, user_tz_offset_secs)
            self.data["timezone"] = tz
            self.data["start_at_mins_in_user_tz"] = start_at_mins_in_user_tz
            self.data["stop_at_mins_in_user_tz"] = stop_at_mins_in_user_tz
            self._refresh_calculated_intervals()

    def get_next_autopause_event_at_timestamp(self):
        if not self.data["is_enabled"]:
            return None

        now_timestamp = int(datetime.datetime.now().timestamp())

        if now_timestamp < self.data["calculated_next_or_current_interval_start_at"]:
            return self.data["calculated_next_or_current_interval_start_at"]

        return self.data["calculated_next_or_current_interval_stop_at"]


    def _refresh_calculated_intervals(self):
        if not self.data["is_enabled"]:
            return

        tz = self.data["timezone"]

        start_timestamp = datetime.datetime.now().timestamp() - 24 * 3600 * 3
        now_timestamp = datetime.datetime.now().timestamp()
        now_in_tz = datetime.datetime.fromtimestamp(now_timestamp, ZoneInfo(tz))

        while True:
            beginning_of_day_in_tz = datetime.datetime.fromtimestamp(start_timestamp, ZoneInfo(tz)).replace(hour=0, minute=0, second=0, microsecond=0)
            beginning_of_next_day_in_tz = datetime.datetime.fromtimestamp(beginning_of_day_in_tz.timestamp() + 36 * 3600, ZoneInfo(tz)).replace(hour=0, minute=0, second=0, microsecond=0)

            interval_start_in_tz = beginning_of_day_in_tz + datetime.timedelta(minutes=self.data["start_at_mins_in_user_tz"])
            interval_stop_in_tz = ((beginning_of_day_in_tz + datetime.timedelta(minutes=self.data["stop_at_mins_in_user_tz"]))
                if self.data["stop_at_mins_in_user_tz"] < 24 * 60
                else (beginning_of_next_day_in_tz + datetime.timedelta(minutes=self.data["stop_at_mins_in_user_tz"] - 24 * 60)))

            if int(interval_start_in_tz.timestamp()) <= int(now_in_tz.timestamp()) <= int(interval_stop_in_tz.timestamp()):
                self.data["calculated_next_or_current_interval_start_at"] = int(interval_start_in_tz.timestamp())
                self.data["calculated_next_or_current_interval_stop_at"] = int(interval_stop_in_tz.timestamp())
                break

            if now_in_tz.day == beginning_of_day_in_tz.day:
                self.data["calculated_next_or_current_interval_start_at"] = int(interval_start_in_tz.timestamp())
                self.data["calculated_next_or_current_interval_stop_at"] = int(interval_stop_in_tz.timestamp())
                break

            start_timestamp += 20 * 3600










