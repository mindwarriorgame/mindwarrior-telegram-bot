import json
from datetime import datetime, timedelta, timezone
from typing import TypedDict, Optional

def default(obj):
    if isinstance(obj, datetime):
        return { '_isoformat': obj.astimezone(timezone.utc).isoformat() }
    raise TypeError('...')

def object_hook(obj):
    _isoformat = obj.get('_isoformat')
    if _isoformat is not None:
        return datetime.fromisoformat(_isoformat)
    return obj

class CounterData(TypedDict):
    is_active: bool
    total_seconds_intermediate: int
    last_total_seconds_updated: datetime

class Counter:

    def __init__(self, data_serialized: Optional[str]):
        self._data: CounterData = self._deserialize_data(data_serialized)
        self.refresh()

    def serialize(self):
        self.refresh()
        return self._serialize_data(self._data)

    def reset(self):
        self._data['is_active'] = False
        self._data['last_total_seconds_updated'] = datetime.now(tz=timezone.utc)
        self._data['total_seconds_intermediate'] = 0
        self.refresh()

    def get_total_seconds(self) -> float:
        self.refresh()
        return self._data['total_seconds_intermediate']

    def is_active(self) -> bool:
        self.refresh()
        return self._data['is_active']

    def resume(self):
        self.refresh()
        self._data['is_active'] = True
        return self

    def pause(self):
        self.refresh()
        self._data['is_active'] = False
        return self

    def refresh(self):
        if self._data['is_active']:
            self._data['total_seconds_intermediate'] += (datetime.now(tz=timezone.utc) - self._data['last_total_seconds_updated']).total_seconds()

        self._data['last_total_seconds_updated'] = datetime.now(tz=timezone.utc)

    def _deserialize_data(self, counter_data_serialized):
        if counter_data_serialized is None or counter_data_serialized == '':
            return {
                'is_active': False,
                'total_seconds_intermediate': 0,
                'last_total_seconds_updated': datetime.now(tz=timezone.utc)
            }
        return CounterData(**json.loads(counter_data_serialized, object_hook=object_hook))

    def _serialize_data(self, counter_data):
        return json.dumps(counter_data, default=default)

    def move_time_back(self, n_minutes):
        self._data['last_total_seconds_updated'] -= timedelta(minutes=n_minutes)