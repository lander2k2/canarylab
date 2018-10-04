import argparse
import json
import requests

def check_performance(prometheus_addr, version, threshold):

    print('------- Performance Check -------')

    base_addr = 'http://{}/api/v1/query'.format(prometheus_addr)

    success_addr = '{}?query=canary_http_success_total'.format(base_addr)
    success_response = requests.get(success_addr)

    total_success = 0
    for result in success_response.json()['data']['result']:
        if result['metric']['pod'][:21] == 'canarylab-data-svc-{}'.format(version):
            total_success += int(result['value'][1])

    print('Total success: {}'.format(total_success))


    perf_addr = '{}?query=canary_response_duration_bucket'.format(base_addr)
    perf_response = requests.get(perf_addr)

    under_1000 = 0
    for result in perf_response.json()['data']['result']:
        if result['metric']['pod'][:21] == 'canarylab-data-svc-{}'.format(version):
            if result['metric']['le'] == '1000':
                under_1000 += int(result['value'][1])

    print('Under threshold: {}'.format(under_1000))

    if float(under_1000)/float(total_success) < threshold:
        return False
    else:
        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check prometheus metrics for poor performance')
    parser.add_argument('prometheus_addr', help='IP address or DNS name of prometheus server')
    parser.add_argument('performance_threshold', type=float, help='Proportion of responses required to be 1000ms or less')
    parser.add_argement('--version', default='v2', help='Workload version to check')
    args = parser.parse_args()

    ok = check_performance(args.prometheus_addr, args.version, args.performance_threshold)
    if not ok:
        print('Performance threshold violated!')
    else:
        print('Everything is fine')

