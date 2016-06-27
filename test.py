#!/usr/bin/env python3
import os
import re
import subprocess
import sys
import time
from functools import lru_cache


NUM_RUNS_PER_TEST = 5
NUM_INSTANCES = (1, 5, 10, 50, 100)
STORAGE_DRIVERS = ('aufs', 'overlay', 'overlay2')


def running_containers():
    output = subprocess.check_output(('docker', 'ps', '-q')).strip()
    if output:
        return output.split(b'\n')
    return []


def write_result(test_name, result):
    os.makedirs('results', exist_ok=True)
    with open(os.path.join('results', test_name), 'a') as f:
        print(result, file=f)


@lru_cache()
def docker_storage_driver():
    docker_info = subprocess.check_output(('docker', 'info'))
    m = re.search(b'^Storage Driver: (.+?)$', docker_info, re.MULTILINE)
    assert m, docker_info
    return m.group(1).decode('utf8')


def run_tests(tests, num_runs=NUM_RUNS_PER_TEST, num_instances_scenarios=NUM_INSTANCES):
    for run in range(num_runs):
        for num_instances in num_instances_scenarios:
            for test in tests:
                test_name = '{test}.{num_instances}.{storage_driver}'.format(
                    test=test,
                    num_instances=num_instances,
                    storage_driver=docker_storage_driver(),
                )
                print('running test: {}'.format(test_name))

                assert len(running_containers()) == 0
                start = time.time()
                procs = [
                    subprocess.Popen(
                        (
                            'docker', 'run', '--rm',
                            '-v', '{}:/mnt:ro'.format(os.getcwd()),
                            'benchmark',
                            '/mnt/test-several-times',
                            str(num_instances),
                            '/mnt/tests/{}'.format(test),
                        ),
                    )
#                    for _ in range(num_instances)
                ]

                while procs:
                    proc = procs.pop()
                    assert proc.wait() == 0, proc.returncode

                duration = time.time() - start
                assert len(running_containers()) == 0
                print('Took {} seconds.'.format(duration))

                write_result(test_name, duration)


def all_tests():
    return sorted(test for test in os.listdir('tests') if not test.startswith('.'))


def main(argv=None):
    run_tests(all_tests())


if __name__ == '__main__':
    sys.exit(main())
