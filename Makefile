docker_build:
	docker build -t journald-2-cloudwatch -f Dockerfile .

docker_build_test: docker_build
	docker build -t journald-2-cloudwatch-test -f Dockerfile.test .

docker_test: docker_build_test
	CODECOV_TMP=$${CODECOV_TMP:-$$(mktemp -d)}; \
	docker run --rm \
	  -v "$$PWD:/jd2cw:ro" \
	  -v "$$CODECOV_TMP:/tmp/codecov" \
	  -e AWS_DEFAULT_REGION=eu-west-1 \
	  -e AWS_ACCESS_KEY_ID=abc \
	  -e AWS_SECRET_ACCESS_KEY=abc \
	  -w $$CODECOV_TMP \
	  journald-2-cloudwatch-test
	docker run --rm journald-2-cloudwatch

lint:
	flake8 ./

isort:
	isort -c --diff ./

fisort:
	isort -rc ./
