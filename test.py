#!/usr/bin/env python3
# Instructions to run tests:
#   1. Create the docker image: docker build -t benchmark .
#   2. Copy the test directory out (for the non-docker tests):
#      $ docker create benchmark
#      $ docker create <the id>:/test /test-master
#   3. Create a local "tree-of-files" for the "read-file-tree-mounted" test
#      $ cp -r /test-master/tree-of-files .
#   4. Run tests: ./test.py
#
#   You'll have to repeat #1 for each for new storage driver since the
#   "benchmark" image will disappear.
#
# TODO: make these instructions more automatic
import os
import re
import subprocess
import sys
import time
from functools import lru_cache


NUM_RUNS_PER_TEST = 10
NUM_INSTANCES = (1, 5, 10, 50, 100)
STORAGE_DRIVERS = ('aufs', 'overlay', 'overlay2', 'no-docker-ext4')


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


def run_tests(tests, in_docker=True, num_runs=NUM_RUNS_PER_TEST, num_instances_scenarios=NUM_INSTANCES):
    for run in range(num_runs):
        for num_instances in num_instances_scenarios:
            for test in tests:
                test_name = '{test}.{num_instances}.{storage_driver}'.format(
                    test=test,
                    num_instances=num_instances,
                    storage_driver=docker_storage_driver() if in_docker else 'no-docker-ext4',
                )
                print('running test: {}'.format(test_name))

                if not in_docker:
                    subprocess.check_call(('rm', '-rf', '/test'))
                    subprocess.check_call(('cp', '-r', '/test-master', '/test'))

                assert len(running_containers()) == 0
                start = time.time()
                procs = [
                    subprocess.Popen(
                        (
                            (
                                'docker', 'run', '--rm',
                                '-v', '{}:/mnt:ro'.format(os.getcwd()),
                                'benchmark',
                            ) if in_docker else ()
                        ) +
                        (
                            '/mnt/test-several-times',
                            str(num_instances),
                            '/mnt/tests/{}'.format(test),
                        ),
                    )
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
    run_tests(all_tests(), in_docker=True)


if __name__ == '__main__':
    sys.exit(main())
