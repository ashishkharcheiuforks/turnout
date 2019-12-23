up:
	docker-compose up

build:
	docker-compose build

makemigrations:
	docker-compose exec server python manage.py makemigrations

migrate:
	docker-compose exec server python manage.py migrate

shell:
	docker-compose exec server /bin/bash

clientshell:
	docker-compose exec client /bin/bash

lint:
	docker-compose exec server bash -c "autoflake \
		--remove-unused-variables --remove-all-unused-imports --ignore-init-module-imports --in-place --recursive --exclude /*/migrations/* /app/ && \
		isort --recursive --skip migrations /app/ && black --exclude /*/migrations/* /app/"

ecrpush:
	scripts/local_ecr_push.sh