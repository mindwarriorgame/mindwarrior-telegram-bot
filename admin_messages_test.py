import unittest

from admin_messages import AdminMessages


class AdminMessagesTest(unittest.IsolatedAsyncioTestCase):

    def test_get_last_message_id_empty(self):
        messages = AdminMessages()
        self.assertEqual(messages.get_last_message_id(), 0)

    def test_get_last_message_id_returns_max(self):
        messages = AdminMessages([
            {'message_id': 10, 'messages_by_lang': {'en': 'A'}},
            {'message_id': 3, 'messages_by_lang': {'en': 'B'}},
            {'message_id': 7, 'messages_by_lang': {'en': 'C'}},
        ])
        self.assertEqual(messages.get_last_message_id(), 10)

    def test_get_pending_messages_language_fallbacks(self):
        messages = AdminMessages([
            {'message_id': 1, 'messages_by_lang': {'en': 'Hello', 'es': 'Hola'}},
            {'message_id': 2, 'messages_by_lang': {'es': 'Solo'}},
            {'message_id': 3, 'messages_by_lang': {'en': '', 'fr': 'Salut'}},
            {'message_id': 4, 'messages_by_lang': {'fr': 'Bonjour'}},
            {'message_id': 5, 'messages_by_lang': {}},
        ])

        pending = messages.get_pending_messages(1, 'es')
        self.assertEqual(pending, [
            {'message_id': 2, 'message': 'Solo'},
            {'message_id': 4, 'message': 'Bonjour'},
        ])

    def test_get_pending_messages_default_language(self):
        messages = AdminMessages([
            {'message_id': 1, 'messages_by_lang': {'en': 'Hello', 'es': 'Hola'}},
            {'message_id': 2, 'messages_by_lang': {'es': 'Solo'}},
            {'message_id': 3, 'messages_by_lang': {'en': '', 'fr': 'Salut'}},
            {'message_id': 4, 'messages_by_lang': {'fr': 'Bonjour'}},
            {'message_id': 5, 'messages_by_lang': {}},
        ])

        pending = messages.get_pending_messages(0, None)
        self.assertEqual(pending, [
            {'message_id': 1, 'message': 'Hello'},
            {'message_id': 2, 'message': 'Solo'},
            {'message_id': 4, 'message': 'Bonjour'},
        ])
