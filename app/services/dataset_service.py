import os
from sqlalchemy.orm import Session
from app.repositories.dataset_repo import DatasetRepository
from app.utils.file_handler import save_file

class DatasetService:

    @staticmethod
    def upload_dataset(db: Session, file, user_id):
        file_path = save_file(file)

        # Get size using os.path.getsize to avoid issues where file cursor is mostly exhausted.
        size_bytes = os.path.getsize(file_path)

        dataset_data = {
            "user_id": user_id,
            "name": file.filename,
            "file_path": file_path,
            "format": file.filename.split(".")[-1] if "." in file.filename else "unknown",
            "status": "uploaded",
            "size_mb": size_bytes / (1024 * 1024),
        }

        dataset = DatasetRepository.create(db, dataset_data)

        return dataset

    @staticmethod
    def list_datasets(db: Session):
        return DatasetRepository.get_all(db)
