.PHONY: run dev test format coverage docker

run:
	python -m app

dev:
	FLASK_ENV=development python -m app

test:
	pytest -q

format:
	black app

coverage:
	coverage run -m pytest && coverage html && python -c "import webbrowser; webbrowser.open('htmlcov/index.html')"

docker:
	docker compose up --build
