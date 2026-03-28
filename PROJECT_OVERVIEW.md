# LLM-Finetune-Platform 🚀

## Executive Summary
This document provides a comprehensive overview of the LLM-Finetune-Platform's architecture, current development state, how data flows through the system, and the purpose of every deployed file.

Currently, we have successfully completed **Phase 0 (Environment Setup)**, **Phase 1 (Database Implementation)**, and **Phase 2 (Dataset Module)**. The system now features a robust PostgreSQL database natively tracking machine learning models and a fully functional API that uploads, stores, and validates training datasets seamlessly.

---

## 🌊 How Data Flows (The Architecture)

We strictly follow a layered, decoupled software architecture: `API → Service → Repository → Storage/DB`. 

Here is exactly what happens when a User uploads a dataset:
1. **API Layer (`app/api/routes/datasets.py`)**: 
   - Receives the raw HTTP `POST /datasets/upload` request containing the physical multi-part `UploadFile`.
   - Injects a fresh Database Session seamlessly via `app.api.deps.get_db`.
   - Forwards the file to the Service layer securely.
2. **Service Layer (`app/services/dataset_service.py`)**: 
   - Acts as the "Brain" handling all Business Logic. 
   - It intercepts the file, calls the File Handler logic to physically stream it to disk, analyzes the exact file-size securely, and builds the Python dictionary mapping the dataset metadata.
3. **Storage Handler (`app/utils/file_handler.py`)**: 
   - Saves the raw binary dataset natively to the machine's disk under `storage/datasets/` avoiding volatile memory bloat and returns the absolute `file_path`.
4. **Repository Layer (`app/repositories/dataset_repo.py`)**: 
   - The Service layer hands the metadata dictionary directly to the Repository.
   - The Repository bridges the Python dictionary directly into a SQLAlchemy `Dataset` model mapping and invokes `.add()` and `.commit()` natively pushing it into the Postgres Database.
5. **Schema Validation (`app/schemas/dataset.py`)**:
   - The API layer intercepts the returned database model, securely formats it through Pydantic (using `from_attributes = True`), and returns a typed serialized JSON response back to the client!

---

## 📂 Folder & File Structure Breakdown

### 🛠️ Root Configuration & Core
* **`.env`**: Holds private environment variables like the `DATABASE_URL` securely connecting to Postgres.
* **`docker/docker-compose.yml`**: Docker deployment configuration capable of spinning up an isolated PostgreSQL 15 instance via port `5432`.
* **`app/main.py`**: The primary execution file for the FastAPI server (`uvicorn app.main:app`). Exposes routes and registers our `datasets.router`.
* **`app/core/config.py`**: Centralizes application configuration securely leveraging `python-dotenv`.
* **`app/api/deps.py`**: Manages explicit **Dependency Injection**. Home to `get_db()` which provisions database connection sessions (`SessionLocal`) to API endpoints per-request dynamically closing them when finished!

### 🗄️ Database Foundation (`app/db/`)
* **`session.py`**: Initializes the SQLAlchemy Engine, defining `SessionLocal` binding dynamically to Postgres connection strings.
* **`base_class.py`**: Exposes the pure SQLAlchemy `Base = declarative_base()` avoiding circular imports while routing ORM objects securely.
* **`base.py`**: Acts as the central hub importing all model schemas dynamically. (Alembic consumes this file natively to run auto-generated schema migrations).

### 🧩 Core Machine Learning ORM Models (`app/db/models/`)
*Every model utilizes Postgres `UUID` (Universally Unique Identifiers) securely mapping objects preventing sequential ID-pattern scraping techniques.*
* **`user.py`** -> `users` table: Base platform authentication tracking mapped globally cross-tables.
* **`dataset.py`** -> `datasets` table: Represents physical uploaded files tied to users, calculated MB sizes, formats, and status flags.
* **`dataset_metadata.py`** -> `dataset_metadata` table: Associates physical dataset intricacies tracking explicit row counts and validation split floats globally avoiding bulk dataset bloat.
* **`model.py`** -> `models` table: Tracks LLM-specific parameters defining exact base models (e.g., Llama-3), active Low-Rank Adapters (LoRAs), and quantizations securely.
* **`experiment.py`** -> `experiments` table: The central nexus linking Users, Datasets, and Models. Stores raw tracking metrics, hyperparameter JSONs, live accuracies, schemas and dynamic operational run states!
* **`training_job.py`** -> `training_jobs` table: Worker distribution tracking tables mapping asynchronous jobs tied explicitly to allocated instances mapping dynamic GPU hardware types while parsing physical job logs securely.

### ⚙️ Dataset Module Components (Phase 2 Built)
* **`app/api/routes/datasets.py`**: Exposes `POST /upload` returning JSON responses and `GET /` retrieving lists of all existing datasets logically.
* **`app/schemas/dataset.py`**: Pydantic models verifying exact response data shape returned to end-users (enforcing parameters natively like `id: UUID`, `size_mb: float`).
* **`app/services/dataset_service.py`**: Explicit business logic binding uploaded files, processing algorithms, and database bridging interfaces robustly holding state separate from the API presentation layer.
* **`app/repositories/dataset_repo.py`**: Database controller strictly managing specific Postgres `.add()` queries directly mapped against the SQLAlchemy representation removing SQL abstractions cleanly!.
* **`app/utils/file_handler.py`**: Safely streams `UploadFile` chunks dynamically allocating and creating chunked `.txt`, `.csv` inside `/storage/datasets/`.

### 🔀 Database Version Control (`alembic/`)
* **`alembic.ini`**, **`alembic/env.py`**, & **`alembic/versions/`**: Dynamically maps and auto-generates timestamped script histories automating structural Postgres schemas securely!

---

## ⏭️ Architecture Roadmap
We are fully scheduled to advance to **Phase 3: Training System (CORE ENGINE)** which implements scalable distributed background tasks utilizing Celery and Redis queuing nodes enabling explicit ML Fine-tuning tasks natively!
