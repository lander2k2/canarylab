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


def rollout(v1_replicas, v2_replicas):

    v1_replicas = str(int(v1_replicas) - 1)
    v2_replicas = str(int(v2_replicas) + 1)

    call([
        'kubectl', 'scale', 'deploy/canarylab-data-svc-v1',
        '--replicas', v1_replicas
    ])

    call([
        'kubectl', 'scale', 'deploy/canarylab-data-svc-v2',
        '--replicas', v2_replicas
    ])

    return v1_replicas, v2_replicas


def rollback(total_replicas):

    call([
        'kubectl', 'scale', 'deploy/canarylab-data-svc-v1',
        '--replicas', total_replicas
    ])

    call([
        'kubectl', 'scale', 'deploy/canarylab-data-svc-v2',
        '--replicas', '0'
    ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Shove a canary down the coalmine')
    parser.add_argument('prometheus_addr', help='IP address or DNS name of prometheus server')
    parser.add_argument('total_replicas', help='Total number of pod replicas for workload')
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
    active_v1 = args.total_replicas
    active_v2 = 0
    while int(active_v1) > 0:
        active_v1, active_v2 = rollout(active_v1, active_v2)
        print colored('==> v2 scaled up, v1 scaled down', 'green')

        print colored('==> pausing for 20s before health check...', 'green')
        time.sleep(20)

        healthy, message = check_health(args.prometheus_addr, 'v2',
                                        args.error_threshold, args.performance_threshold)
        if healthy:
            print colored('==> v2 confirmed healthy', 'green')
        else:
            print colored('==> v2 unhealthy: {}'.format(message), 'red')
            rollback(args.total_replicas)
            print colored('==> canary deployment rolled back', 'red')
            exit(1)

    print colored('==> canary deployment complete', 'green')

