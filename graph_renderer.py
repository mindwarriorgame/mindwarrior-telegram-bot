import statistics
from datetime import timedelta, datetime
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.dates import date2num

from history import HistoryRec
from lang_provider import Lang

PAUSED_COUNTER_HISTORY_NAME = "paused"
REVIEW_COUNTER_HISTORY_NAME = "review"

# This class was generated mostly by ChatGPT
class GraphRenderer:
    def render_graph(self, lang: Lang, history_recs: List[HistoryRec], difficulty_threshold_mins: int, difficulty_str: str, paused_at: Optional[datetime]):
        reviewed_timestamps = []
        paused_timestamps = []
        reviewed_min_values = []
        paused_min_values = []
        for rec in history_recs:
            if rec['counter_name'] == REVIEW_COUNTER_HISTORY_NAME:
                reviewed_timestamps.append(rec['event_datetime'])
                reviewed_min_values.append(rec['counter_stopped_duration_secs'] / 60)
            elif rec['counter_name'] == PAUSED_COUNTER_HISTORY_NAME:
                paused_timestamps.append(rec['event_datetime'])
                paused_min_values.append(rec['counter_stopped_duration_secs'] / 60)

        if paused_at is not None:
            paused_timestamps.append(datetime.now(tz=paused_at.tzinfo))
            paused_min_values.append((datetime.now(tz=paused_at.tzinfo) - paused_at).total_seconds() / 60)

        if len(reviewed_timestamps) == 0:
            return None

        time_data = pd.to_datetime(reviewed_timestamps)
        y_values = reviewed_min_values

        plt.figure(figsize=(10, 6))
        ax = plt.gca()
        ax.plot(time_data, y_values, label=lang.graph_header, marker='o')

        y_values_mean = statistics.mean(y_values)

        ax.axhline(y=difficulty_threshold_mins, color='r', linestyle='--', label=lang.graph_penalty_threshold.format(
            difficulty_threshold_mins=difficulty_threshold_mins,
            difficulty_str=difficulty_str
        ))
        ax.axhline(y=y_values_mean, color='g', linestyle='--', label=lang.graph_mean_threshold.format(mean_mins=int(y_values_mean)))

        for idx in range(0, len(paused_timestamps)):
            paused_end = paused_timestamps[idx]
            paused_min_value = paused_min_values[idx]
            paused_start = paused_end - timedelta(minutes=paused_min_value)
            ax.axvspan(date2num(paused_start), date2num(paused_end), color='gray', alpha=0.2, label=lang.graph_paused if idx == 0 else None)

        ax.set_xlabel(lang.graph_xlabel)
        ax.set_ylabel(lang.graph_ylabel)
        ax.set_title(lang.graph_header)
        ax.legend()
        ax.grid(True)

        start_of_week = datetime.now() - timedelta(days=6)
        end_of_week = datetime.now()
        ax.set_xlim(start_of_week, end_of_week)

        custom_labels = [lang.graph_xmin, '-5', '-4', '-3', '-2', '-1', lang.graph_xmax]
        positions = [
            start_of_week,
            end_of_week - timedelta(days=5),
            end_of_week - timedelta(days=4),
            end_of_week - timedelta(days=3),
            end_of_week - timedelta(days=2),
            end_of_week - timedelta(days=1),
            end_of_week
        ]
        ax.set_xticks(ticks=pd.to_datetime(positions))
        ax.set_xticklabels(custom_labels, rotation=45)

        ax_right = ax.twinx()
        ax_right.set_ylabel(lang.graph_ylabel)
        ax_right.set_yticks(ax.get_yticks())
        ax_right.set_ylim(ax.get_ylim())

        plt.tight_layout()

        random_fname = 'tmp_' + str(np.random.randint(100000, 900000)) + '.png'
        plt.savefig(random_fname, dpi=300)
        return random_fname
