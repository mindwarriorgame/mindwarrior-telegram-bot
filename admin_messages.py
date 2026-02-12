from typing import Optional, List, TypedDict, Dict


class AdminMessageConfig(TypedDict):
    message_id: int
    messages_by_lang: Dict[str, str]


class AdminMessage(TypedDict):
    message_id: int
    message: str


DEFAULT_MESSAGES: List[AdminMessageConfig] = [
    {
        "message_id": 1,
        "messages_by_lang": {
            "ru": (
                "Дорогой пользователь!\n"
                "\n"
                "Рады вам сообщить, что вышла Android версия MindWarriod 🎉 ! Из плюшек:\n"
                "\n"
                " - Игра не требует интернета!\n"
                " - Не нужен аккаунт, регистрации, рекламы и прочей чепухи.\n"
                " - Ваша конфиденциальность на первом месте: мы не следим за вами и не собираем о вас информацию (да и как это сделать без интернета? 😉 ).\n"
                " - Нативные нотификации Android-а, никаких лагов и блокировок.\n"
                " - 100% бесплантая и open source.\n"
                "\n"
                "Доступна для скачивания в Googl Play Store: https://play.google.com/store/apps/details?id=com.mindwarrior.app"
            ),
            "en": (
                "Dear user!\n"
                "\n"
                "We’re happy to announce that the Android version of MindWarrior is out 🎉! Highlights:\n"
                "\n"
                " - The game doesn’t require internet!\n"
                " - No account, sign-up, ads, or other nonsense.\n"
                " - Your privacy comes first: we don’t track you or collect any information about you (and how could we without internet? 😉).\n"
                " - Native Android notifications — no lagging or blocking.\n"
                " - 100% free and open source.\n"
                "\n"
                "Available on the Google Play Store: https://play.google.com/store/apps/details?id=com.mindwarrior.app"
            ),
            "fr": (
                "Cher utilisateur !\n"
                "\n"
                "Nous sommes ravis de vous annoncer que la version Android de MindWarrior est sortie 🎉 ! Au programme :\n"
                "\n"
                " - Le jeu ne nécessite pas d’internet !\n"
                " - Pas besoin de compte, d’inscription, de pubs ni d’autres bêtises.\n"
                " - Votre confidentialité avant tout : nous ne vous suivons pas et ne collectons aucune information sur vous (et comment le faire sans internet ? 😉).\n"
                " - Notifications Android natives — aucun lag, aucun blocage.\n"
                " - 100% gratuit et open source.\n"
                "\n"
                "Disponible sur le Google Play Store : https://play.google.com/store/apps/details?id=com.mindwarrior.app"
            ),
            "es": (
                "¡Querido usuario!\n"
                "\n"
                "Nos alegra anunciar que ya salió la versión Android de MindWarrior 🎉. Ventajas:\n"
                "\n"
                " - ¡El juego no requiere internet!\n"
                " - No necesitas cuenta, registro, anuncios ni otras tonterías.\n"
                " - Tu privacidad es lo primero: no te rastreamos ni recopilamos información sobre ti (¿y cómo hacerlo sin internet? 😉).\n"
                " - Notificaciones nativas de Android — sin lags ni bloqueos.\n"
                " - 100% gratis y open source.\n"
                "\n"
                "Disponible en Google Play Store: https://play.google.com/store/apps/details?id=com.mindwarrior.app"
            ),
            "de": (
                "Liebe Nutzerin, lieber Nutzer!\n"
                "\n"
                "Wir freuen uns, euch mitzuteilen, dass die Android-Version von MindWarrior veröffentlicht ist 🎉! Highlights:\n"
                "\n"
                " - Das Spiel braucht kein Internet!\n"
                " - Kein Konto, keine Registrierung, keine Werbung und kein anderer Quatsch.\n"
                " - Deine Privatsphäre steht an erster Stelle: Wir tracken dich nicht und sammeln keine Informationen über dich (und wie sollte das ohne Internet gehen? 😉).\n"
                " - Native Android-Benachrichtigungen — keine Lags und keine Sperren.\n"
                " - 100% kostenlos und open source.\n"
                "\n"
                "Im Google Play Store verfügbar: https://play.google.com/store/apps/details?id=com.mindwarrior.app"
            ),
        },
    }
]



class AdminMessages:
    def __init__(self, messages: Optional[List[AdminMessageConfig]] = DEFAULT_MESSAGES) -> None:
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
