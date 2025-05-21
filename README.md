# FastAPI Naive

Fast API application template with a clean layered architecture.

## Architecture

The application follows a clean layered architecture pattern:

```mermaid
graph TD
    A[API] --> S[Services]
    A --> DTO[DTO]
    S --> D[DAO]
    S --> DTO
    D --> SC[Schemas]
    D --> DTO
    DTO -.-> ALL[Available to all layers]

    classDef api fill:#f96,stroke:#333,stroke-width:2px;
    classDef srv fill:#9cf,stroke:#333,stroke-width:2px;
    classDef dao fill:#9fc,stroke:#333,stroke-width:2px;
    classDef schema fill:#fcf,stroke:#333,stroke-width:2px;
    classDef dto fill:#ff9,stroke:#333,stroke-width:2px;
    
    class A api;
    class S srv;
    class D dao;
    class SC schema;
    class DTO dto;
```

### Layer Description

- **API Layer**: Обрабатывает HTTP-запросы и ответы
- **Services Layer**: Содержит бизнес-логику приложения
- **DAO (Data Access Object) Layer**: Управляет операциями с базой данных
- **Schemas Layer**: Определяет модели SQLAlchemy для базы данных
- **DTO Layer**: Определяет модели Pydantic для передачи данных между слоями

## Setup Instructions

### Docker Setup
- Always rename networks in `networks` section to `project_net`
- Use only `project_net` for all networks in the file

### Environment Setup
- Create virtual environment with `python -m venv .venv`
- After creating the environment, run `uv init`
- Edit your `pyproject.toml` with necessary dependencies
- Run `uv sync` to install dependencies
