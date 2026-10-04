from pathlib import Path

from app.database import Base, engine, get_db
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.agent import agent
from app.database import Base, engine, get_db
from app.models import Document, DocumentChunk, User, DocumentShare
from app.services.document_processor import (
    extract_text_from_pdf,
    chunk_pages,
)
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import FAISSVectorStore
from app.auth import (
    create_access_token,
    hash_password,
    verify_password,
    get_current_user_id,
)

app = FastAPI(
    title="Knowledge-Based Decision Intelligence Agent",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables if they do not already exist
Base.metadata.create_all(bind=engine)


DOCUMENTS_DIR = (
    Path(__file__).resolve().parents[2] / "data" / "documents"
)

INDEX_DIR = (
    Path(__file__).resolve().parents[2] / "data" / "index"
)

FAISS_INDEX_PATH = INDEX_DIR / "knowledge.faiss"
FAISS_METADATA_PATH = INDEX_DIR / "metadata.json"

embedding_service = EmbeddingService()

def load_vector_store():
    if not FAISS_INDEX_PATH.exists() or not FAISS_METADATA_PATH.exists():
        raise HTTPException(
            status_code=400,
            detail="No document index has been built yet.",
        )

    return FAISSVectorStore.load(
        str(FAISS_INDEX_PATH),
        str(FAISS_METADATA_PATH),
    )

def rebuild_vector_index(db: Session):
    chunks = (
        db.query(DocumentChunk)
        .join(Document)
        .order_by(DocumentChunk.id)
        .all()
    )

    if not chunks:
        if FAISS_INDEX_PATH.exists():
            FAISS_INDEX_PATH.unlink()

        if FAISS_METADATA_PATH.exists():
            FAISS_METADATA_PATH.unlink()

        return

    texts = []

    for chunk in chunks:
        document = db.query(Document).filter(
            Document.id == chunk.document_id
        ).first()

        if document is None:
            continue

        pages = extract_text_from_pdf(document.storage_path)

        page_text = next(
            (
                page["text"]
                for page in pages
                if page["page_number"] == chunk.page_number
            ),
            None,
        )

        if page_text is None:
            continue

        chunk_text = page_text[
            chunk.start_offset:chunk.end_offset
        ]

        texts.append({
            "chunk_id": chunk.id,
            "text": chunk_text,
        })

    if not texts:
        return

    embeddings = embedding_service.embed_documents(
        [item["text"] for item in texts]
    )

    vector_store = FAISSVectorStore(
        dimension=embeddings.shape[1]
    )

    vector_store.add_embeddings(
        embeddings,
        [item["chunk_id"] for item in texts],
    )

    vector_store.save(
        str(FAISS_INDEX_PATH),
        str(FAISS_METADATA_PATH),
    )
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str

class ShareDocumentRequest(BaseModel):
    user_id: int


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

@app.post("/register")
def register_user(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )

    user = User(
        email=request.email,
        password_hash=hash_password(
            request.password
        ),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "email": user.email,
    }
@app.post("/login")
def login_user(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if user is None or not verify_password(
        request.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
    }

@app.post("/documents/{document_id}/share")
def share_document(
    document_id: int,
    request: ShareDocumentRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    # Check that the document exists and belongs to the current user
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.owner_id == current_user_id,
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found or you are not the owner",
        )

    # Check that the target user exists
    target_user = (
        db.query(User)
        .filter(User.id == request.user_id)
        .first()
    )

    if target_user is None:
        raise HTTPException(
            status_code=404,
            detail="User to share with does not exist",
        )

    # Don't allow sharing with yourself
    if request.user_id == current_user_id:
        raise HTTPException(
            status_code=400,
            detail="Document already belongs to you",
        )

    # Check if already shared
    existing_share = (
        db.query(DocumentShare)
        .filter(
            DocumentShare.document_id == document_id,
            DocumentShare.user_id == request.user_id,
        )
        .first()
    )

    if existing_share:
        raise HTTPException(
            status_code=400,
            detail="Document is already shared with this user",
        )

    share = DocumentShare(
        document_id=document_id,
        user_id=request.user_id,
    )

    db.add(share)
    db.commit()
    db.refresh(share)

    return {
        "message": "Document shared successfully",
        "document_id": document_id,
        "shared_with_user_id": request.user_id,
    }

@app.post("/documents/{filename}/ingest")
def ingest_document(
    filename: str,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    file_path = DOCUMENTS_DIR / filename

    if not file_path.exists() or file_path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=404, detail="PDF not found")

    existing_document = (
        db.query(Document)
        .filter(
            Document.filename == filename,
            Document.owner_id == current_user_id,
        )
        .first()
    )

    if existing_document:
        raise HTTPException(
            status_code=400,
            detail="Document already exists for this user",
        )

    pages = extract_text_from_pdf(str(file_path))

    document = Document(
        filename=filename,
        storage_path=str(file_path),
        owner_id=current_user_id,
    )

    db.add(document)
    db.flush()

    chunks = chunk_pages(pages)

    db_chunks = []

    for chunk in chunks:
        db_chunk = DocumentChunk(
            document_id=document.id,
            page_number=chunk["page_number"],
            chunk_order=chunk["chunk_order"],
            start_offset=chunk["start_offset"],
            end_offset=chunk["end_offset"],
        )

        db.add(db_chunk)
        db.flush()

        db_chunks.append(db_chunk)

    texts = [chunk["text"] for chunk in chunks]

    embeddings = embedding_service.embed_documents(texts)

    if FAISS_INDEX_PATH.exists() and FAISS_METADATA_PATH.exists():
        vector_store = FAISSVectorStore.load(
            str(FAISS_INDEX_PATH),
            str(FAISS_METADATA_PATH),
        )
    else:
        vector_store = FAISSVectorStore(
            dimension=embeddings.shape[1]
        )

    chunk_ids = [chunk.id for chunk in db_chunks]

    vector_store.add_embeddings(
        embeddings,
        chunk_ids,
    )

    vector_store.save(
        str(FAISS_INDEX_PATH),
        str(FAISS_METADATA_PATH),
    )

    db.commit()

    return {
        "message": "Document ingested successfully",
        "document_id": document.id,
        "filename": filename,
        "owner_id": current_user_id,
        "pages": len(pages),
        "chunks": len(chunks),
        "embedding_dimension": embeddings.shape[1],
        "embedding_count": len(embeddings),
        "indexed_vectors": vector_store.index.ntotal,
    }

@app.get("/documents/{filename}/preview")
def preview_document(
    filename: str,
):
    file_path = DOCUMENTS_DIR / filename

    if not file_path.exists() or file_path.suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=404,
            detail="PDF not found",
        )

    pages = extract_text_from_pdf(
        str(file_path)
    )

    chunks = chunk_pages(pages)

    return {
        "filename": filename,
        "pages": len(pages),
        "chunks": len(chunks),
        "sample_chunks": chunks[:3],
    }

@app.post("/search")
def search_documents(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    vector_store = load_vector_store()

    query_embedding = embedding_service.embed_query(request.query)

    # Retrieve extra candidates because some may be inaccessible
    candidate_k = max(request.top_k * 5, 20)

    results = vector_store.search(
        query_embedding,
        top_k=candidate_k,
    )

    retrieved_chunks = []

    for result in results:
        chunk = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.id == result["chunk_id"])
            .first()
        )

        if chunk is None:
            continue

        document = (
            db.query(Document)
            .filter(Document.id == chunk.document_id)
            .first()
        )

        if document is None:
            continue

        # Permission check:
        # User can access the document if they own it
        # OR it has been shared with them.
        has_access = (
            document.owner_id == current_user_id
            or db.query(DocumentShare)
            .filter(
                DocumentShare.document_id == document.id,
                DocumentShare.user_id == current_user_id,
            )
            .first()
            is not None
        )

        if not has_access:
            continue

        pages = extract_text_from_pdf(document.storage_path)

        page_text = next(
            (
                page["text"]
                for page in pages
                if page["page_number"] == chunk.page_number
            ),
            None,
        )

        if page_text is None:
            continue

        text = page_text[
            chunk.start_offset:chunk.end_offset
        ]

        retrieved_chunks.append(
            {
                "chunk_id": chunk.id,
                "document_id": document.id,
                "filename": document.filename,
                "page_number": chunk.page_number,
                "score": result["score"],
                "text": text,
            }
        )

        # Stop once we have enough authorized results
        if len(retrieved_chunks) >= request.top_k:
            break

    return {
        "query": request.query,
        "results": retrieved_chunks,
    }

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported",
        )

    filename = Path(file.filename).name
    file_path = DOCUMENTS_DIR / filename

    # Prevent overwriting an existing file
    existing_document = (
        db.query(Document)
        .filter(
            Document.filename == filename,
            Document.owner_id == current_user_id,
        )
        .first()
    )

    if existing_document:
        raise HTTPException(
            status_code=400,
            detail="You already have a document with this filename",
        )

    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

    contents = await file.read()

    with open(file_path, "wb") as output_file:
        output_file.write(contents)

    # Reuse our existing ingestion pipeline
    return ingest_document(
        filename=filename,
        db=db,
        current_user_id=current_user_id,
    )

@app.get("/documents")
def list_documents(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    documents = (
        db.query(Document)
        .filter(Document.owner_id == current_user_id)
        .order_by(Document.created_at.desc())
        .all()
    )

    return {
        "documents": [
            {
                "id": document.id,
                "filename": document.filename,
                "created_at": document.created_at.isoformat(),
            }
            for document in documents
        ]
    }

@app.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.owner_id == current_user_id,
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    file_path = Path(document.storage_path)

    # Delete database record.
    # DocumentChunk records are deleted through the relationship
    # cascade configured in models.py.
    db.delete(document)
    db.commit()

    # Delete the original PDF.
    if file_path.exists():
        file_path.unlink()

    rebuild_vector_index(db)

    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
    }

@app.post("/agent")
def ask_agent(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    vector_store = load_vector_store()

    query_embedding = embedding_service.embed_query(request.query)

    candidate_k = max(request.top_k * 5, 20)

    results = vector_store.search(
        query_embedding,
        top_k=candidate_k,
    )

    evidence = []

    for result in results:
        chunk = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.id == result["chunk_id"])
            .first()
        )

        if chunk is None:
            continue

        document = (
            db.query(Document)
            .filter(Document.id == chunk.document_id)
            .first()
        )

        if document is None:
            continue

        has_access = (
            document.owner_id == current_user_id
            or db.query(DocumentShare)
            .filter(
                DocumentShare.document_id == document.id,
                DocumentShare.user_id == current_user_id,
            )
            .first()
            is not None
        )

        if not has_access:
            continue

        pages = extract_text_from_pdf(document.storage_path)

        page_text = next(
            (
                page["text"]
                for page in pages
                if page["page_number"] == chunk.page_number
            ),
            None,
        )

        if page_text is None:
            continue

        text = page_text[
            chunk.start_offset:chunk.end_offset
        ]

        evidence.append(
            {
                "chunk_id": chunk.id,
                "document_id": document.id,
                "filename": document.filename,
                "page_number": chunk.page_number,
                "score": result["score"],
                "text": text,
            }
        )

        if len(evidence) >= request.top_k:
            break

    result = agent.invoke(
        {
            "question": request.query,
            "evidence": evidence,
            "answer": "",
            "sufficient_evidence": False,
        }
    )

    return {
        "question": request.query,
        "answer": result["answer"],
        "evidence": evidence,
    }