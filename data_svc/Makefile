default: release

release: bin image push clean

bin:
	GOOS=linux GOARCH=amd64 go build -o data-svc data_service.go

image:
	test -n "$(IMAGE_REPO)"  # must set $$IMAGE_REPO env var
	test -n "$(IMAGE_TAG)"  # must set $$IMAGE_TAG env var
	docker build --tag ${IMAGE_REPO}:${IMAGE_TAG} .

push:
	test -n "$(IMAGE_REPO)"  # must set $$IMAGE_REPO env var
	test -n "$(IMAGE_TAG)"  # must set $$IMAGE_TAG env var
	docker push ${IMAGE_REPO}:${IMAGE_TAG}

clean:
	rm data-svc

