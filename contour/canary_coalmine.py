#!/usr/bin/env python2

import argparse
import time

from subprocess import call
from termcolor import colored

from error_check import check_errors
from performance_check import check_performance


def check_health(prometheus_addr, version,
                 error_threshold, performance_threshold):

    errors_ok = check_errors(prometheus_addr, version, error_threshold)
    if not errors_ok:
        return False, 'Error threshold violated!'

    performance_ok = check_performance(prometheus_addr, version, performance_threshold)
    if not performance_ok:
        return False, 'Performance threshold violated!'

    return True, ''


def rollout(stage):

    manifest = 'canary-ingressroute-{}.yaml'.format(stage)
    call(['kubectl', 'apply', '-f', manifest])


def rollback():

    call(['kubectl', 'apply', '-f', 'canary-ingressroute-0.yaml'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Shove a canary down the coalmine')
    parser.add_argument('prometheus_addr', help='IP address or DNS name of prometheus server')
    parser.add_argument('--error_threshold', type=float, default=0.1,
                        help='Proportion of errors deemed unacceptable')
    parser.add_argument('--performance_threshold', type=float, default=0.9,
                        help='Proportion of responses required to be 1000ms or less')
    args = parser.parse_args()

    # Ensure v1 is healthy
    healthy, message = check_health(args.prometheus_addr, 'v1',
                                    args.error_threshold, args.performance_threshold)
    if healthy:
        print colored('==> v1 confirmed healthy', 'green')
    else:
        print colored('==> v1 unhealthy: {}'.format(message), 'red')
        print colored('==> aborting', 'red')
        exit(1)

    # Perform incremental roll out of v2
    stages = ["5", "40", "100"]  # must correspond to manifest labels, e.g. canary-deploy-5.yaml
    while len(stages) > 0:
        current_stage = stages.pop(0)
        rollout(current_stage)
        print colored('==> {}% of traffic now going to v2'.format(current_stage), 'green')

        print colored('==> pausing for 40s before health check...', 'green')
        time.sleep(40)

        healthy, message = check_health(args.prometheus_addr, 'v2',
                                        args.error_threshold, args.performance_threshold)
        if healthy:
            print colored('==> v2 confirmed healthy', 'green')
        else:
            print colored('==> v2 unhealthy: {}'.format(message), 'red')
            rollback()
            print colored('==> canary deployment rolled back', 'red')
            exit(1)

    print colored('==> canary deployment complete', 'green')

