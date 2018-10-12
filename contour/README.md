# Contour Canary Deployments

The manifests and scripts here can be used to run through canary deployments using native K8s resources.  The key concern is being able to detect unhealthy conditions in the new version (v2) and roll back.  The workload emits metrics that are used for this purpose and is able to simulate failure conditions.

## Setup
Deploy contour:

    $ kubectl apply -f contour.yaml

Deploy prometheus operator:

    $ kubectl apply -f prom-operator.yaml

Add the URL to your contour ingress to each of the `canary-ingressroute` manifests.  If you're using a type LoadBalancer in AWS, for example, you can put the DNS name of the ELB assigned (see `kubectl get svc -n heptio-contour contour`).

Create canary deployment and service monitor:

    $ kubectl apply -f canary-deploy.yaml
    $ kubectl apply -f canary-ingressroute-0.yaml
    $ kubectl apply -f canary-svcmon.yaml

Deploy Prometheus instance:

    $ kubectl apply -f prom-rbac.yaml
    $ kubectl apply -f prom.yaml

Start sending traffic:

    $ while true; do curl [contour address]/version; sleep 0.2; done;

## Canary Deployment Simulations

### Failure: Excessive Errors

In this example, the v2 version will be started with a flag that cause it to return intermitent 500 errors.  This will be detected and the deployment rolled back.

1. Open `canary-deploy.yaml` and uncomment the line `command: ["/data-svc", "error"]` on the canarylab-data-svc-v2 deployment.

2. Apply the change

        $ kubectl apply -f canary-deploy.yaml

3. Determine the address to use for Prometheus.

4. Start the simulation:

        $ python canary_coalmine.py [prometheus address]

### Failure: Poor Performance

In this example, the v2 version will be started with a flag that causes intermittent slow responses.  This will be detected and the deployment rolled back.

1. Open `canary-deploy.yaml` and uncomment the line `command: ["/data-svc", "slow"]` on the canarylab-data-svc-v2 deployment.

2. Apply the change

        $ kubectl apply -f canary-deploy.yaml

3. Determine the address to use for Prometheus.

4. Start the simulation:

        $ python canary_coalmine.py [prometheus address]

## Success

In this example, the v2 version will be started in default mode and will behave properly.  No problems will be detected and the canary deployment will successful roll out.

1. Open `canary-deploy.yaml` and ensure that both `command` lines are commented out on the canarylab-data-svc-v2 deployment.

2. Apply the change

        $ kubectl apply -f canary-deploy.yaml

3. Determine the address to use for Prometheus.

4. Start the simulation:

        $ python canary_coalmine.py [prometheus address]


