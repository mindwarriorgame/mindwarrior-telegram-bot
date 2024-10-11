import json
from datetime import datetime, timezone
from typing import TypedDict, Optional, List


def object_parser(obj):
    if isinstance(obj, datetime):
        return { '_isoformat': obj.astimezone(timezone.utc).isoformat() }
    raise TypeError('...')

def object_hook(obj):
    _isoformat = obj.get('_isoformat')
    if _isoformat is not None:
        return datetime.fromisoformat(_isoformat)
    return obj


class HistoryRec(TypedDict):
    counter_name: str
    counter_stopped_duration_secs: int
    event_datetime: datetime

def _deserialize_session(serialized_session: Optional[str]) -> List[HistoryRec]:
    if serialized_session is None or serialized_session == '':
        return []
    return json.loads(serialized_session, object_hook=object_hook)


def _serialize_session(session):
    return json.dumps(session, default=object_parser)


def _invalidate_old_items(session: List[HistoryRec]):
    return [item for item in session if (datetime.now(tz=timezone.utc) - item['event_datetime']).days < 7]


def add_timer_rec_to_history(serialized_session: Optional[str], history_rec: HistoryRec) -> str:
    session = _deserialize_session(serialized_session)
    history_rec['event_datetime'] = history_rec['event_datetime'].astimezone(timezone.utc)
    session.append(history_rec)
    _invalidate_old_items(session)
    return _serialize_session(session)


def get_timer_recs_from_history(serialized_session: Optional[str]) -> List[HistoryRec]:
    return _invalidate_old_items(_deserialize_session(serialized_session))
