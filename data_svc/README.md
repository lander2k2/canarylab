# Canary Lab Data Service

This mock service is used for canary deployment simulations.  It does two important things:

1. Optionally simulates unhealthy conditions:

    * Intermittent 500 responses

    * Intermittent slow responses (5 seconds)

2. Exposes prometheus metrics that can be used to detect these unhealthy conditions.

## Build Instructions

Building the v1 and v2 images as follows will produce images that are functionally identical but will return different version numbers to requests made to the `/version` URI.

    $ export IMAGE_REPO=quay.io/myimages/canary_data_svc
    $ echo "v1" > VERSION
    $ export IMAGE_TAG=$(cat VERSION)
    $ make

    $ echo "v2" > VERSION
    $ export IMAGE_TAG=$(cat VERSION)
    $ make

