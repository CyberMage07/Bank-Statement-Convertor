from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.document import ExportRequest, ParseDocumentResponse
from services.statement_parser import StatementParser

router = APIRouter()
parser = StatementParser()


@router.post("/parse-document", response_model=ParseDocumentResponse)
async def parse_document(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for parsing.")

    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(payload)
        tmp_path = Path(tmp.name)

    try:
        result = parser.parse_pdf(tmp_path)
        return ParseDocumentResponse(
            document_id=result.document_id,
            bank_name=result.bank_name,
            confidence_score=result.confidence_score,
            transactions=result.transactions,
            needs_review=result.needs_review,
        )
    finally:
        tmp_path.unlink(missing_ok=True)


@router.post("/exports/{document_id}")
def export_document(document_id: str, body: ExportRequest):
    return {
        "document_id": document_id,
        "export_format": body.export_format,
        "columns": body.columns,
        "status": "queued",
    }


@router.get("/health")
def health_check():
    return {"status": "ok"}
