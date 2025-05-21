# Настройка Проекта

## Docker Setup

- Всегда переименовывайте сети в секции `networks` на `project_net`.
- Используйте только `project_net` для всех сетей в файле `docker-compose.yaml`.

## Environment Setup

1.  **Создайте виртуальное окружение**:
    ```bash
    python -m venv .venv
    ```
2.  **Активируйте виртуальное окружение**:
    -   Windows (Git Bash/PowerShell):
        ```bash
        source .venv/Scripts/activate
        ```
    -   Linux/macOS:
        ```bash
        source .venv/bin/activate
        ```
3.  **Инициализируйте `uv`** (если используете `uv` как пакетный менеджер):
    ```bash
    uv init
    ```
4.  **Отредактируйте `pyproject.toml`**, добавив необходимые зависимости в секцию `[project.dependencies]`.
5.  **Установите зависимости** (если используете `uv`):
    ```bash
    uv sync
    ```
    (Примечание: `uv sync` работает с `pyproject.toml` напрямую).
