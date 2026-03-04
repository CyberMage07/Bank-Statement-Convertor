from celery import Celery

from app.core.config import settings

celery_app = Celery("findoc", broker=settings.redis_url, backend=settings.redis_url)


@celery_app.task(name="documents.process")
def process_document_task(document_id: str) -> dict:
    return {"document_id": document_id, "status": "processed"}
