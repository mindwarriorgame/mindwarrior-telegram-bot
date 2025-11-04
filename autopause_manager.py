import datetime
import json
from typing import TypedDict, Optional
from zoneinfo import ZoneInfo
from fuzzywuzzy import fuzz
import zoneinfo


class AutopauseConfig(TypedDict):
    is_enabled: bool
    start_at_mins_in_user_tz: Optional[int]
    stop_at_mins_in_user_tz: Optional[int] # may be more than 24 hours to indicate next day
    user_timezone: Optional[str] # correct timezone string; use detect_timezone() to figure it out from user's input

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
            tz_utc_offset = zoneinfo.ZoneInfo(tz).utcoffset(datetime.datetime.now())
            if tz_utc_offset is None:
                continue 
            offset = tz_utc_offset.total_seconds()
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
                "start_at_mins_in_user_tz": None,
                "stop_at_mins_in_user_tz": None,
                "timezone": None,
            }
        self._calculate_next_interval_timestamps()

    def serialize(self) -> str:
        return json.dumps(self.data)

    def update(self, is_enabled, user_tz_string, user_tz_offset_secs, start_at_str, stop_at_str):
        self.data["is_enabled"] = is_enabled
        if is_enabled:
            start_at_mins_in_user_tz = int(start_at_str.split(":")[0]) * 60 + int(start_at_str.split(":")[1])
            stop_at_mins_in_user_tz = int(stop_at_str.split(":")[0]) * 60 + int(stop_at_str.split(":")[1])
            if stop_at_mins_in_user_tz < start_at_mins_in_user_tz:
                stop_at_mins_in_user_tz += 24 * 60
            tz = detect_timezone(user_tz_string, user_tz_offset_secs)
            self.data["timezone"] = tz
            self.data["start_at_mins_in_user_tz"] = start_at_mins_in_user_tz
            self.data["stop_at_mins_in_user_tz"] = stop_at_mins_in_user_tz
            return self._calculate_next_interval_timestamps()
        else:
            self.data["timezone"] = None
            self.data["start_at_mins_in_user_tz"] = None
            self.data["stop_at_mins_in_user_tz"] = None

        return None, None

    def get_next_autopause_event_at_timestamp(self):
        if not self.data["is_enabled"]:
            return None
        start_ts, stop_ts = self._calculate_next_interval_timestamps()
        if not start_ts:
            return None

        now_timestamp = int(datetime.datetime.now().timestamp())

        if now_timestamp < start_ts:
            return start_ts

        return stop_ts

    def is_in_interval(self, timestamp):
        if not self.data["is_enabled"]:
            return False
        start_ts, stop_ts = self._calculate_next_interval_timestamps()
        if not start_ts:
            return None

        return start_ts <= timestamp <= stop_ts

    def get_wakep_time(self):
        if self.data["stop_at_mins_in_user_tz"] is None:
            return None

        return self._get_user_time(self.data['stop_at_mins_in_user_tz'])

    def get_bed_time(self):
        if self.data["start_at_mins_in_user_tz"] is None:
            return None

        return self._get_user_time(self.data['start_at_mins_in_user_tz'])

    def _calculate_next_interval_timestamps(self):
        if not self.data["is_enabled"]:
            return None, None

        tz = self.data["timezone"]

        iter_timestamp = datetime.datetime.now().timestamp() - 24 * 3600 * 3
        now_timestamp = datetime.datetime.now().timestamp()
        now_in_tz = datetime.datetime.fromtimestamp(now_timestamp, ZoneInfo(tz))

        while True:
            beginning_of_day_in_tz = datetime.datetime.fromtimestamp(iter_timestamp, ZoneInfo(tz)).replace(hour=0, minute=0, second=0, microsecond=0)
            beginning_of_next_day_in_tz = datetime.datetime.fromtimestamp(beginning_of_day_in_tz.timestamp() + 36 * 3600, ZoneInfo(tz)).replace(hour=0, minute=0, second=0, microsecond=0)

            interval_start_in_tz = beginning_of_day_in_tz + datetime.timedelta(minutes=self.data["start_at_mins_in_user_tz"])
            interval_stop_in_tz = ((beginning_of_day_in_tz + datetime.timedelta(minutes=self.data["stop_at_mins_in_user_tz"]))
                if self.data["stop_at_mins_in_user_tz"] < 24 * 60
                else (beginning_of_next_day_in_tz + datetime.timedelta(minutes=self.data["stop_at_mins_in_user_tz"] - 24 * 60)))

            if int(now_in_tz.timestamp()) <= int(interval_stop_in_tz.timestamp()):
                return int(interval_start_in_tz.timestamp()), int(interval_stop_in_tz.timestamp())

            iter_timestamp += 20 * 3600

    def is_enabled(self):
        if not self.data["is_enabled"]:
            return False
        return self.data["is_enabled"]

    def _get_user_time(self, time_in_mins):
        ret = ""
        at_mins = (time_in_mins - 24 * 60) if time_in_mins >= 24 * 60 else time_in_mins
        hours = at_mins // 60
        mins = at_mins % 60
        if hours < 10:
            ret += "0"
        ret += str(hours) + ":"
        if mins < 10:
            ret += "0"
        ret += str(mins)
        return ret
        pass










