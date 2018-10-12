# Native Kubernetes Canary Deployments

The manifests and scripts here can be used to run through canary deployments using native K8s resources.  The key concern is being able to detect unhealthy conditions in the new version (v2) and roll back.  The workload emits metrics that are used for this purpose and is able to simulate failure conditions.

## Setup
Deploy prometheus operator:

    $ kubectl apply -f prom-operator.yaml

Create canary deployment and service monitor:

    $ kubectl apply -f canary-deploy.yaml
    $ kubectl apply -f canary-svcmon.yaml

Deploy Prometheus instance:

    $ kubectl apply -f prom-rbac.yaml
    $ kubectl apply -f prom.yaml

Start sending traffic:

    $ kubectl apply -f https://raw.githubusercontent.com/lander2k2/crashcart/master/crashcart-po.yaml
    $ kubectl exec -it crashcart bash
    # while true; do curl canarylab-data-svc:8080/version; sleep 0.2; done;

## Canary Deployment Simulations

### Failure: Excessive Errors

In this example, the v2 version will be started with a flag that cause it to return intermitent 500 errors.  This will be detected and the deployment rolled back.

1. Open `canary-deploy.yaml` and uncomment the line `command: ["/data-svc", "error"]` on the canarylab-data-svc-v2 deployment.

2. Apply the change

        $ kubectl apply -f canary-deploy.yaml

3. Determine the address to use for Prometheus.  If using `prom.yaml` unchanged, it will be `[worker ip]:30900`.

4. Start the simulation:

        $ python canary_coalmine.py [prometheus address] 4

### Failure: Poor Performance

In this example, the v2 version will be started with a flag that causes intermittent slow responses.  This will be detected and the deployment rolled back.

1. Open `canary-deploy.yaml` and uncomment the line `command: ["/data-svc", "slow"]` on the canarylab-data-svc-v2 deployment.

2. Apply the change

        $ kubectl apply -f canary-deploy.yaml

3. Determine the address to use for Prometheus.  If using `prom.yaml` unchanged, it will be `[worker ip]:30900`.

4. Start the simulation:

        $ python canary_coalmine.py [prometheus address] 4

## Success

In this example, the v2 version will be started in default mode and will behave properly.  No problems will be detected and the canary deployment will successful roll out.

1. Open `canary-deploy.yaml` and ensure that both `command` lines are commented out on the canarylab-data-svc-v2 deployment.

2. Apply the change

        $ kubectl apply -f canary-deploy.yaml

3. Determine the address to use for Prometheus.  If using `prom.yaml` unchanged, it will be `[worker ip]:30900`.

4. Start the simulation:

        $ python canary_coalmine.py [prometheus address] 4


