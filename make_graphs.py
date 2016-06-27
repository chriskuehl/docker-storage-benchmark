#!/usr/bin/env python3
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from test import NUM_INSTANCES
from test import STORAGE_DRIVERS
from test import all_tests


def all_test_types():
    return {
        '.'.join(f.strip('.').split('.')[0:1])
        for f in os.listdir('results')
        if not f.startswith('.')
    }


def average_from_file(path):
    try:
        with open(path) as f:
            lines = [float(line) for line in f.readlines()]
        return min(lines)
    except FileNotFoundError:
        return 0


def main(argv=None):
    width = 1
    for test in all_tests():
        fig = Figure(figsize=(10, 5))
        FigureCanvasAgg(fig)  # why do i have to do this?
        ax = fig.add_subplot(1, 1, 1)
        x = np.array([float(i)*(len(STORAGE_DRIVERS)+1) for i in range(len(NUM_INSTANCES))])
        bars = []

        for driver, color in zip(STORAGE_DRIVERS, 'mbcg'):
            means = []
            for num_instances in NUM_INSTANCES:
                means.append(average_from_file(os.path.join(
                    'results',
                    '{}.{}.{}'.format(test, num_instances, driver),
                )))

            bars.append(ax.bar(x, means, width, color=color))
            x += width

        ax.set_title(test)
        ax.set_xlabel('num parallel processes' + ' ' * 90)  # lol
        ax.set_ylabel('seconds for completion')
        ax.set_xticklabels(NUM_INSTANCES)
        ax.set_xticks(x - 1.5)

        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.3, box.width, box.height * 0.7])
        ax.legend((bar[0] for bar in bars), STORAGE_DRIVERS,
                bbox_to_anchor=(1, -0.1),
              fancybox=True, shadow=True, ncol=5)

        fig.savefig(os.path.join('graphs', test + '.png'))


if __name__ == '__main__':
    sys.exit(main())
