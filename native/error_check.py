import argparse
import json
import requests


def check_errors(prometheus_addr, version, threshold):

    print('---------- Error Check ----------')

    base_addr = 'http://{}/api/v1/query'.format(prometheus_addr)

    error_addr = '{}?query=canary_http_errors_total'.format(base_addr)
    error_response = requests.get(error_addr)

    total_errors = 0
    for result in error_response.json()['data']['result']:
        if result['metric']['pod'][:21] == 'canarylab-data-svc-{}'.format(version):
            total_errors += int(result['value'][1])

    print('Total errors: {}'.format(total_errors))

    success_addr = '{}?query=canary_http_success_total'.format(base_addr)
    success_response = requests.get(success_addr)

    total_success = 0
    for result in success_response.json()['data']['result']:
        if result['metric']['pod'][:21] == 'canarylab-data-svc-{}'.format(version):
            total_success += int(result['value'][1])

    print('Total success: {}'.format(total_success))

    if float(total_errors)/float(total_success) > threshold:
        return False
    else:
        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check prometheus metrics for excesssive errors')
    parser.add_argument('prometheus_addr', help='IP address or DNS name of prometheus server')
    parser.add_argument('error_threshold', type=float, help='Proportion of errors deemed unacceptable')
    parser.add_argement('--version', default='v2', help='Workload version to check')
    args = parser.parse_args()

    ok = check_errors(args.prometheus_addr, args.version, args.error_threshold)
    if not ok:
        print('Error threshold violated!')
    else:
        print('Everything is fine')

