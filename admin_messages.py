from typing import Optional, List, TypedDict, Dict


class AdminMessageConfig(TypedDict):
    message_id: int
    messages_by_lang: Dict[str, str]


class AdminMessage(TypedDict):
    message_id: int
    message: str


class AdminMessages:
    def __init__(self, messages: Optional[List[AdminMessageConfig]] = None) -> None:
        self._messages = messages or []

    def get_last_message_id(self) -> int:
        if not self._messages:
            return 0
        return max(message['message_id'] for message in self._messages)

    def get_pending_messages(self, last_sent_message_id: int, lang_code: Optional[str]) -> List[AdminMessage]:
        pending: List[AdminMessage] = []
        preferred_lang = lang_code or "en"
        for message in self._messages:
            if message['message_id'] <= last_sent_message_id:
                continue
            text = message['messages_by_lang'].get(preferred_lang)
            if text is None:
                text = message['messages_by_lang'].get("en")
            if text is None and message['messages_by_lang']:
                text = next(iter(message['messages_by_lang'].values()))
            if not text:
                continue
            pending.append({
                'message_id': message['message_id'],
                'message': text
            })
        return pending
