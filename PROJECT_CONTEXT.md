# LLM Finetune Platform - Project Context Document

This document provides complete, structured context for any new developer or AI model joining the **LLM-Finetune-Platform** project. Read this entire document carefully before making changes to ensure you adhere to established patterns, understand current limitations, and build in the correct direction.

---

## 1️⃣ Project Overview

*   **What the project is:** A scalable backend platform for dynamic Large Language Model (LLM) fine-tuning, automated dataset management, and asynchronous model training.
*   **Main Objective:** To provide an infrastructure where users can upload training datasets, select model configurations (like LoRA parameters), and asynchronously trigger GPU-accelerated fine-tuning jobs.
*   **Problem Being Solved:** Abstracting away the complex infrastructure required for LLM training by providing a clean REST API, separating long-running GPU tasks from the main web server, and managing relational experiment data securely.
*   **Current Status:** Phase 0 (Environment), Phase 1 (Database), and Phase 2 (Dataset Upload/Storage) are **completed**. The platform can currently accept datasets, stream them securely to disk, and save records via SQLAlchemy. The actual Celery asynchronous training engine (Phase 3) is currently pending implementation.

---

## 2️⃣ System Architecture

*   **Overall Architecture:** A highly decoupled, asynchronous Backend architecture heavily reliant on a Publisher-Subscriber pattern for offloading heavy ML tasks.
*   **Layered API Design:** The web server strictly adheres to: `API (Routes) -> Service (Business Logic) -> Repository (Database Access) -> Storage/DB`.
*   **Major Components:**
    *   **FastAPI:** The core web server handling HTTP requests and schema validation.
    *   **PostgreSQL:** The primary relational database holding configuration and state.
    *   **Celery + Redis (Planned/Pending):** The distributed task queue and message broker to handle background CUDA operations.
    *   **File Storage System:** A local file handler that chunks multipart uploads and streams them directly to the `storage/datasets/` directory to prevent volatile memory bloat.
*   **Data Flow Example (Dataset Upload):**
    1.  Client sends `POST /datasets/upload` with a file.
    2.  `API Layer` injects DB dependency and calls `Service Layer`.
    3.  `Service Layer` passes file to `File Handler` which streams it to disk.
    4.  `Service Layer` passes file metadata to `Repository Layer`.
    5.  `Repository Layer` translates it to SQLAlchemy models, commits to Postgres, and returns the entity.
    6.  `API Layer` uses Pydantic to serialize the ORM entity into a JSON response.

---

## 3️⃣ Folder & File Structure

### 🛠️ Root Files
*   **`.env`**: Holds local environment variables (e.g., `DATABASE_URL`).
*   **`docker/docker-compose.yml`**: Configures Docker for the local PostgreSQL database (and eventually Redis/Celery).
*   **`requirements.txt`**: Standard python dependencies (FastAPI, PyTorch, Transformers, Celery, etc.).
*   **`PROJECT_OVERVIEW.md`**: High-level documentation.

### ⚙️ Core Application (`app/`)
*   **`main.py`**: The FastAPI application entry point. Registers routers.
*   **`api/deps.py`**: Manages explicit **Dependency Injection** (e.g., `get_db()`).
*   **`api/routes/`**: Contains FastAPI endpoint definitions (e.g., `datasets.py`, `training.py`).
*   **`schemas/`**: Pydantic models for request validation and response serialization.
*   **`services/`**: The "Brain" containing all business logic. Decoupled from HTTP and DB specifics.
*   **`repositories/`**: Handles all native SQLAlchemy `.add()`, `.commit()` logic. No SQL abstractions leave this layer.
*   **`utils/file_handler.py`**: Handles chunked binary file streaming directly to disk.

### 🗄️ Database Foundation (`app/db/`)
*   **`session.py`**: Initializes the SQLAlchemy Engine and `SessionLocal`.
*   **`base_class.py`**: Exposes the pure SQLAlchemy `Base = declarative_base()`.
*   **`base.py`**: Central hub importing all schemas for Alembic to auto-generate migrations.
*   **`models/`**: The core ORM entities (`user.py`, `dataset.py`, `model.py`, `experiment.py`, `training_job.py`, `dataset_metadata.py`).

### 🔀 Database Version Control (`alembic/`)
*   **`alembic.ini` & `env.py`**: Configuration for automated DB migrations based on `app/db/base.py`.

---

## 4️⃣ Features Implemented

*   **Database Infrastructure:** A fully relational PostgreSQL 15 database initialized via Docker, with automated schema generation running through Alembic.
*   **ORM Layer:** Six complete SQLAlchemy tables mapping the platform's core entities using UUIDs.
*   **Dataset Upload API:** Fully functional POST and GET routes for dataset ingestion. Includes Pydantic validation.
*   **Memory-Safe File Ingestion:** Files are streamed in chunks to `/storage/datasets/` bypassing in-memory loading to prevent crashes on large files.
*   **Dependency Injection:** A robust `get_db` injector that ensures isolated, request-scoped database sessions.

---

## 5️⃣ Pending Work / To-Do

*   **Phase 3: Core Training Engine (High Priority):** Implement the Celery background workers and Redis message queue to consume the datasets and trigger actual PyTorch/Transformers fine-tuning tasks using CUDA.
*   **Authentication Flow:** Implement JWT-based authentication mapped to the `users` table to secure the API routes (currently placeholder UUIDs are used).
*   **Inference Module:** After a model is trained, expose an API endpoint to load the custom LoRA weights and perform inference text generation.
*   **Experiment Tracking UI/API:** Routes to poll the current loss/accuracy metrics generated by the Celery workers.

---

## 6️⃣ Important Logic & Decisions

*   **UUIDs for Security:** Auto-incrementing integers are strictly forbidden as primary keys. We use PostgreSQL UUIDs to prevent sequential ID-pattern scraping attacks.
*   **Strict Layered Separation:** You must never write raw SQL queries in the `services` or `api` layer. The `repository` layer solely handles DB interactions.
*   **Memory Management:** Loading datasets entirely into memory via `.read()` is strictly forbidden. All file operations must use chunked streams to handle large CSV/TXT ML datasets gracefully.

---

## 7️⃣ AI / Prompt Logic

*Not explicitly applicable yet. The platform trains AI, it does not currently orchestrate chains of prompts via an LLM gateway.*

---

## 8️⃣ Configuration & Environment

*   **Required Dependencies:** `fastapi`, `sqlalchemy`, `pydantic`, `celery`, `redis`, `psycopg2-binary`, `transformers`, `torch`, `peft`.
*   **Environment Variables (`.env`):**
    *   `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/llm_db`
*   **Setup Requirements:** Must run `docker-compose up -d` from the `docker/` folder to spin up the required Postgres instance.

---

## 9️⃣ Database & Data Handling

*   **Database Structure (PostgreSQL):**
    *   **USERS**: Platform authentication.
    *   **DATASETS & DATASET_METADATA**: Tracks physical file paths and row counts.
    *   **MODELS**: Tracks base configurations (e.g., Llama-3, LoRA).
    *   **EXPERIMENTS**: The central nexus linking Users, Datasets, and Models. Stores raw tracking metrics.
    *   **TRAINING_JOBS**: Worker distribution tracking tables mapping async jobs to experiments.
*   **Data Flow Pattern:** SQLAlchemy ORM models are passed to Pydantic schemas using `from_attributes=True` for fast JSON serialization on API return.

---

## 🔟 Important Context for New Model (Critical Context)

*   **CRITICAL ASSUMPTION:** The actual ML training logic (Celery Workers) is **NOT** built yet. Do not hallucinate that the training pipeline is functional. If tasked with "fixing training", you will likely need to build the Celery integration from scratch.
*   **CONVENTION - Dependency Injection:** Whenever creating a new route that needs database access, you **MUST** inject the session using `db: Session = Depends(get_db)`. Do not instantiate connections manually inside functions.
*   **CONVENTION - Pydantic vs SQLAlchemy:** Be extremely careful not to confuse Pydantic validation schemas (in `app/schemas/`) with SQLAlchemy ORM models (in `app/db/models/`). They are separate entities mapped to each other.
*   **ARCHITECTURE PATTERN:** Never skip the Service layer. Even if a route is a simple CRUD GET operation, it must go: Route -> Service -> Repository.

---

## 1️⃣1️⃣ Additional Information (Informational Context)

*   **Historical Context:** The platform was designed to be a self-hostable alternative to managed fine-tuning platforms. Hardware costs dictated the need for extreme async isolation so the web server could run on a tiny instance while worker nodes handle the GPU load.
*   **Experimental Ideas:** There is a `GCP_GPU_Test_Pipeline.ipynb` notebook in the root directory. This is likely an experimental scratchpad used to validate hardware capability on cloud environments before integrating it into the Celery workers.
*   **Future Scope:** Once the core training engine is built, the architecture is designed to easily plug in an authentication gateway and a React frontend.

---

## 1️⃣2️⃣ Quick Onboarding Summary

You are working on a backend API built with **FastAPI** that acts as the control plane for fine-tuning Large Language Models. 

Right now, the system successfully allows users to upload datasets securely into a **PostgreSQL** database without crashing the server. Your next major objective is likely to implement the **Celery/Redis** asynchronous engine that will actually take those datasets and run heavy PyTorch training jobs in the background. Follow the strict `API -> Service -> Repository` architecture pattern, and always use UUIDs for database tables.
