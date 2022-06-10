docker_test:
	# docker-compose run --rm app sh -c "pytest --cov=."
	docker-compose run --rm app sh -c "pytest"

docker_migrate:
	docker-compose run --rm app sh -c "python manage.py migrate"

start_docker:
	docker-compose up

stop_docker:
	docker-compose down

gaa:
	git add -A

gs:
	git status

psh:
	git push