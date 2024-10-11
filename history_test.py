import datetime
import unittest

import time_machine

from history import add_timer_rec_to_history, get_timer_recs_from_history

class TestHistory(unittest.IsolatedAsyncioTestCase):

    def test_get_timer_recs_from_history_no_history(self):
        self.assertEqual(get_timer_recs_from_history(None), [])

    @time_machine.travel("2022-04-21", tick=False)
    def test_add_items(self):
        sess = add_timer_rec_to_history(None, {
            'counter_name': 'test',
            'counter_stopped_duration_secs': 10,
            'event_datetime': datetime.datetime.now()
        })

        traveller = time_machine.travel(datetime.datetime(2022, 4, 22).astimezone(datetime.timezone.utc), tick=False)
        traveller.start()
        sess = add_timer_rec_to_history(sess, {
            'counter_name': 'test2',
            'counter_stopped_duration_secs': 15,
            'event_datetime': datetime.datetime.now()
        })
        traveller.stop()

        self.assertEqual(get_timer_recs_from_history(sess), [
            {
                'counter_name': 'test',
                'counter_stopped_duration_secs': 10,
                'event_datetime': datetime.datetime(2022, 4, 21, 0, 0, 0).astimezone(datetime.timezone.utc)
            },
            {
                'counter_name': 'test2',
                'counter_stopped_duration_secs': 15,
                'event_datetime': datetime.datetime(2022, 4, 22, 0, 0, 0).astimezone(datetime.timezone.utc)
            }
        ])

    @time_machine.travel("2022-04-23", tick=False)
    def test_removes_old_items(self):
        sess = add_timer_rec_to_history(None, {
            'counter_name': 'test',
            'counter_stopped_duration_secs': 10,
            'event_datetime': datetime.datetime.now() - datetime.timedelta(days=18)
        })

        sess = add_timer_rec_to_history(sess, {
            'counter_name': 'test2',
            'counter_stopped_duration_secs': 15,
            'event_datetime': datetime.datetime(2022, 4, 22)
        })

        self.assertEqual(get_timer_recs_from_history(sess), [
            {
                'counter_name': 'test2',
                'counter_stopped_duration_secs': 15,
                'event_datetime': datetime.datetime(2022, 4, 22, 0, 0, 0).astimezone(datetime.timezone.utc)
            }
        ])
