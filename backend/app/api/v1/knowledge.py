from pathlib import Path
import shutil
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Request,
    UploadFile,
)

from app.core.dependencies import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/knowledge",
    tags=["Financial Knowledge"],
)


# -----------------------------------------
# Upload PDF to RAG knowledge base
# -----------------------------------------

@router.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(
        get_current_user
    ),
):
   
    # 1. Validate file type

    if not file.filename:
        raise ValueError(
            "No file was provided."
        )

    if not file.filename.lower().endswith(
        ".pdf"
    ):
        raise ValueError(
            "Only PDF files are supported."
        )

    # 2. Create upload directory
    upload_dir = Path(
        "data/uploads"
    )

    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    document_name = Path(file.filename.replace("\\", "/")).name
    if not document_name or document_name in {".", ".."}:
        raise ValueError("Invalid file name.")

    # Keep the original safe name for citations, while using a unique local
    # temporary path so uploads cannot collide or escape the upload directory.
    file_path = upload_dir / f"{uuid4().hex}_{document_name}"

    # -----------------------------------------
    # 3. Save uploaded PDF
    # -----------------------------------------

    with file_path.open("wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer,
        )

    try:

        # -----------------------------------------
        # 4. Create RAG service
        # -----------------------------------------

        rag_service = request.app.state.ai_runtime.get_rag_service()

        # -----------------------------------------
        # 5. Ingest document
        # -----------------------------------------

        result = rag_service.ingest_pdf(
            file_path=str(file_path),
            document_name=document_name,
            user_id=current_user.id,
        )

        return result

    finally:

        # -----------------------------------------
        # 6. Remove uploaded temporary file
        # -----------------------------------------

        if file_path.exists():

            file_path.unlink()
