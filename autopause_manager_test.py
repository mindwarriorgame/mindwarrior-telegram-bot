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

    @time_machine.travel("2022-04-21", tick=True)
    def test_in_interval(self):
        now = datetime.now(tz=ZoneInfo("Australia/Sydney"))
        self.assertEqual(now.astimezone(tz=ZoneInfo("Asia/Novosibirsk")).hour, 21)
        manager = AutopauseManager(None)
        manager.update(True, "Asia/Novosibirsk", 7 * 3600, 22*60, (24 + 8) * 60)

        self.assertFalse(manager.is_in_interval(datetime.now().timestamp()))
        self.assertTrue(manager.is_in_interval(datetime.now().timestamp() + 3 * 3600))
        self.assertFalse(manager.is_in_interval(datetime.now().timestamp() + 12 * 3600))

    @time_machine.travel("2022-04-21", tick=True)
    def test_serialize_deserialize(self):
        now = datetime.now(tz=ZoneInfo("Australia/Sydney"))
        self.assertEqual(now.astimezone(tz=ZoneInfo("Asia/Novosibirsk")).hour, 21)
        manager = AutopauseManager(None)
        manager.update(True, "Asia/Novosibirsk", 7 * 3600, 22*60, (24 + 8) * 60)

        serialized = manager.serialize()
        manager2 = AutopauseManager(serialized)
        self.assertFalse(manager2.is_in_interval(datetime.now().timestamp()))
        self.assertTrue(manager2.is_in_interval(datetime.now().timestamp() + 3 * 3600))

    def test_get_wakeup_time(self):
        manager = AutopauseManager(None)

        self.assertEqual(manager.get_wakep_time(), None)

        manager.update(True, "Asia/Novosibirsk", 7 * 3600, 22*60, (24 + 8) * 60 + 30)
        self.assertEqual(manager.get_wakep_time(), "08:30")

        manager.update(True, "Asia/Novosibirsk", 7 * 3600, 22*60, (24 + 18) * 60)
        self.assertEqual(manager.get_wakep_time(), "18:00")

        manager.update(True, "Asia/Novosibirsk", 7 * 3600, 22*60, 8 * 60)
        self.assertEqual(manager.get_wakep_time(), "08:00")

        manager.update(True, "Asia/Novosibirsk", 7 * 3600, 22*60, 18 * 60)
        self.assertEqual(manager.get_wakep_time(), "18:00")

        manager.update(True, "Asia/Novosibirsk", 7 * 3600, 22*60, 0 * 60)
        self.assertEqual(manager.get_wakep_time(), "00:00")

    def test_get_bed_time(self):
        manager = AutopauseManager(None)

        self.assertEqual(manager.get_bed_time(), None)

        manager.update(True, "Asia/Novosibirsk", 7 * 3600, 22*60, (24 + 8) * 60 + 30)
        self.assertEqual(manager.get_bed_time(), "22:00")

        manager.update(True, "Asia/Novosibirsk", 7 * 3600, 3*60 + 25, (24 + 18) * 60)
        self.assertEqual(manager.get_bed_time(), "03:25")
