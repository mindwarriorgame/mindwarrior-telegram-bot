import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine

from autopause_manager import detect_timezone, AutopauseManager


class AutopauseManagerTest(unittest.IsolatedAsyncioTestCase):

    @time_machine.travel("2022-04-21", tick=False)
    def test_detect_timezone_exact_name(self):
        self.assertEqual(detect_timezone("Australia/Sydney", 10 * 3600), "Australia/Sydney")
        pass

    @time_machine.travel("2022-04-21", tick=True)
    def test_detect_timezone_fuzzy(self):
        started = datetime.now().timestamp()
        self.assertEqual(detect_timezone("Oustralia/ Sydney", 10 * 3600), "Australia/Sydney")
        stopped = datetime.now().timestamp()
        diff = stopped - started
        pass

    @time_machine.travel("2022-04-21", tick=True)
    def test_update_datetime_correctly_recalculates_intervals(self):
        now = datetime.now(tz=ZoneInfo("Australia/Sydney"))
        self.assertEqual(now.astimezone(tz=ZoneInfo("Asia/Novosibirsk")).hour, 21)
        manager = AutopauseManager(None)

        manager.update(True, "novosibirsk", 7 * 3600, 22*60, (24 + 8) * 60)
        next_event = datetime.fromtimestamp(manager.get_next_autopause_event_at_timestamp(), tz=ZoneInfo("Australia/Sydney"))
        self.assertEqual(next_event.hour, 1)
        self.assertEqual(next_event.minute, 0)
        self.assertEqual(next_event.day, now.day)

        manager.update(True, "novosibirsk", 7 * 3600, 20*60, (24 + 8) * 60)
        next_event = datetime.fromtimestamp(manager.get_next_autopause_event_at_timestamp(), tz=ZoneInfo("Australia/Sydney"))

        self.assertEqual(next_event.hour, 11)
        self.assertEqual(next_event.minute, 0)
        self.assertEqual(next_event.day, now.day)



        pass