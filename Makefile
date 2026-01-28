.PHONY: list install install_dev lint run run_all tests run tests create_migration migrate downgrade
.DEFAULT_GOAL := list

list: ## Показать список всех команд
	@echo "Доступные команды:"
	@echo
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

install: ## Установка зависимостей
	uv sync

install_dev: ## Установка зависимостей для разработчиков
	uv sync --all-groups
	uv run pre-commit install

lint: ## Запуск автоматического форматирование кода
	pre-commit run --all-files

run: ## Запуск приложения
	uv run app
