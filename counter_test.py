import unittest
from time import sleep

from counter import Counter

class CounterTest(unittest.IsolatedAsyncioTestCase):

    def test_new_counter_starts_paused(self):
        counter = Counter(None)
        self.assertFalse(counter.is_active())
        self.assertEqual(counter.get_total_seconds(), 0)

    def test_unpause_counter(self):
        counter = Counter(None)
        counter.resume()
        self.assertTrue(counter.is_active())
        self.assertGreater(counter.get_total_seconds(), 0)

    def test_pause_counter(self):
        counter = Counter(None)
        counter.resume()
        sleep(0.1)
        counter.pause()
        self.assertFalse(counter.is_active())
        at_1 = counter.get_total_seconds()
        at_2 = counter.get_total_seconds()
        self.assertEqual(at_1, at_2)
        counter.resume()
        sleep(0.1)
        at_3 = counter.get_total_seconds()
        self.assertGreater(at_3, at_2)

    def test_serialize_unserialise(self):
        counter = Counter(None)
        counter.resume()
        sleep(0.1)
        counter.pause()
        data = counter.serialize()
        counter2 = Counter(data)
        self.assertFalse(counter2.is_active())
        self.assertEqual(counter.get_total_seconds(), counter2.get_total_seconds())
        self.assertGreater(counter.get_total_seconds(), 0)