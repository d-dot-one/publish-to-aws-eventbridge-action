.DEFAULT_GOAL := all

audit_dependencies:
	pipenv lock -r > requirements.txt | pipenv run safety check --full-report --stdin

#
# container build
#
publish_build:
	docker stop publish_to_sns || true
	docker build -t publish_to_sns:latest .
	docker image prune -f
	docker run -d --name publish_to_sns -it publish_to_sns:latest

coverage_base:
	pipenv run coverage run --omit "*/tests*" --data-file=tests/badges/coverage/coverage-report -m pytest -v --benchmark-autosave --benchmark-save=tests --junitxml=tests/badges/tests/test-report.xml --html=tests/badges/tests/test-report.html --self-contained-html

coverage_badge_data:
	pipenv run coverage xml --omit "*/tests*" --data-file=tests/badges/coverage/coverage-report -o tests/badges/coverage/coverage.xml

coverage_report:
	pipenv run coverage html --data-file=tests/badges/coverage/coverage-report -d tests/badges/coverage/

coverage_badge:
	pipenv run genbadge coverage -i tests/badges/coverage/coverage.xml -o tests/badges/coverage.svg

flake8:
	pipenv run flake8 . --statistics --tee --count --output-file tests/badges/flake8/flake8stats.txt --exclude .benchmarks,.github,.idea,.mypy_cache,.pytest_cache,build,egg-info,logs,tests,*.html,*.css --exit-zero --format=html --htmldir=tests/badges/flake8 --max-line-length 100 --benchmark

flake8_badge:
	pipenv run genbadge flake8 -i tests/badges/flake8/flake8stats.txt -o tests/badges/flake8.svg

isort:
	pipenv run isort .

lint_dockerfile:
	docker run --rm -i hadolint/hadolint < Dockerfile

mypy:
	pipenv run mypy --install-types --non-interactive .

pylint:
	pipenv run pylint .

test:
	pipenv run pytest

test_regen:
	pipenv run pytest -x --force-regen

tests_badge:
	pipenv run genbadge tests -i tests/badges/tests/test-report.xml -o tests/badges/tests.svg

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
## macros
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
audit: audit_dependencies

badges: coverage coverage_badge_data coverage_badge flake8 flake8_badge tests_badge

coverage: coverage_base coverage_badge_data coverage_report coverage_badge

lint: isort flake8 pylint mypy

tests: test

all: lint audit tests badges

build_all: publish_build
