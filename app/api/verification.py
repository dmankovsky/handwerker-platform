import os
import aiofiles
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.craftsman import CraftsmanProfile, Document, DocumentType
from app.schemas.verification import (
    DocumentUploadResponse,
    DocumentResponse,
    DocumentVerificationRequest,
    VerificationStatusResponse,
)
from app.api.dependencies import get_current_active_user
from app.core.config import settings

router = APIRouter(prefix="/api/verification", tags=["Verification"])

# Allowed document file types
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


async def save_upload_file(upload_file: UploadFile, destination: str) -> int:
    """Save uploaded file and return file size"""
    file_size = 0
    async with aiofiles.open(destination, 'wb') as out_file:
        while content := await upload_file.read(1024 * 1024):  # Read 1MB chunks
            file_size += len(content)
            await out_file.write(content)
    return file_size


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_verification_document(
    document_type: DocumentType,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload verification document
    (Craftsmen only)
    """
    if current_user.role != UserRole.CRAFTSMAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only craftsmen can upload verification documents"
        )

    # Get craftsman profile
    result = await db.execute(
        select(CraftsmanProfile).where(CraftsmanProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Craftsman profile not found"
        )

    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Create documents directory if it doesn't exist
    docs_dir = os.path.join(settings.UPLOAD_DIR, "documents", str(profile.id))
    os.makedirs(docs_dir, exist_ok=True)

    # Generate unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{document_type.value}_{timestamp}{file_ext}"
    file_path = os.path.join(docs_dir, filename)

    # Save file
    file_size = await save_upload_file(file, file_path)

    # Check file size
    if file_size > MAX_FILE_SIZE:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Create document record
    document = Document(
        craftsman_id=profile.id,
        document_type=document_type,
        filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type or "application/octet-stream",
        verified=False
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    return DocumentUploadResponse(
        id=document.id,
        document_type=document.document_type.value,
        filename=document.filename,
        file_size=document.file_size,
        uploaded_at=document.uploaded_at,
        verified=document.verified
    )


@router.get("/documents", response_model=List[DocumentResponse])
async def get_my_documents(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all verification documents for current craftsman
    (Craftsmen only)
    """
    if current_user.role != UserRole.CRAFTSMAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only craftsmen can view their documents"
        )

    result = await db.execute(
        select(CraftsmanProfile).where(CraftsmanProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Craftsman profile not found"
        )

    result = await db.execute(
        select(Document)
        .where(Document.craftsman_id == profile.id)
        .order_by(Document.uploaded_at.desc())
    )
    documents = result.scalars().all()

    return [DocumentResponse.from_orm(doc) for doc in documents]


@router.get("/status", response_model=VerificationStatusResponse)
async def get_verification_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get verification status for current craftsman
    (Craftsmen only)
    """
    if current_user.role != UserRole.CRAFTSMAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only craftsmen can check verification status"
        )

    result = await db.execute(
        select(CraftsmanProfile).where(CraftsmanProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Craftsman profile not found"
        )

    # Count documents
    result = await db.execute(
        select(Document).where(Document.craftsman_id == profile.id)
    )
    documents = result.scalars().all()

    documents_count = len(documents)
    verified_documents_count = sum(1 for doc in documents if doc.verified)
    pending_verification = documents_count > 0 and verified_documents_count < documents_count

    return VerificationStatusResponse(
        profile_id=profile.id,
        is_verified=profile.is_verified,
        handwerkskammer_number=profile.handwerkskammer_number,
        documents_count=documents_count,
        verified_documents_count=verified_documents_count,
        pending_verification=pending_verification,
        verification_date=profile.verified_at
    )


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a verification document
    (Craftsmen only - can only delete unverified documents)
    """
    if current_user.role != UserRole.CRAFTSMAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only craftsmen can delete documents"
        )

    result = await db.execute(
        select(CraftsmanProfile).where(CraftsmanProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Craftsman profile not found"
        )

    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.craftsman_id == profile.id
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    if document.verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete verified documents"
        )

    # Delete file from filesystem
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    # Delete database record
    await db.delete(document)
    await db.commit()

    return {"message": "Document deleted successfully"}


# Admin endpoints

@router.get("/admin/pending", response_model=List[dict])
async def get_pending_verifications(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get craftsmen pending verification
    (Admin only)
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Get profiles with documents but not verified
    result = await db.execute(
        select(CraftsmanProfile)
        .where(CraftsmanProfile.is_verified == False)
        .offset(skip)
        .limit(limit)
    )
    profiles = result.scalars().all()

    pending_list = []
    for profile in profiles:
        # Get documents count
        result = await db.execute(
            select(Document).where(Document.craftsman_id == profile.id)
        )
        documents = result.scalars().all()

        if documents:  # Only include if has documents
            pending_list.append({
                "profile_id": profile.id,
                "company_name": profile.company_name,
                "user_email": profile.user.email,
                "handwerkskammer_number": profile.handwerkskammer_number,
                "documents_count": len(documents),
                "verified_documents": sum(1 for doc in documents if doc.verified),
                "created_at": profile.created_at
            })

    return pending_list


@router.put("/admin/documents/{document_id}/verify", response_model=DocumentResponse)
async def verify_document(
    document_id: int,
    verification_data: DocumentVerificationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify or reject a document
    (Admin only)
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    document.verified = verification_data.verified
    document.verified_at = datetime.utcnow() if verification_data.verified else None
    document.verified_by = current_user.id if verification_data.verified else None
    document.notes = verification_data.notes

    # Check if all documents are verified, then verify profile
    result = await db.execute(
        select(Document).where(Document.craftsman_id == document.craftsman_id)
    )
    all_documents = result.scalars().all()

    if all(doc.verified for doc in all_documents) and len(all_documents) > 0:
        # Verify profile
        result = await db.execute(
            select(CraftsmanProfile).where(CraftsmanProfile.id == document.craftsman_id)
        )
        profile = result.scalar_one_or_none()
        if profile:
            profile.is_verified = True
            profile.verified_at = datetime.utcnow()

    await db.commit()
    await db.refresh(document)

    return DocumentResponse.from_orm(document)


@router.get("/admin/craftsman/{profile_id}/documents", response_model=List[DocumentResponse])
async def get_craftsman_documents_admin(
    profile_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all documents for a specific craftsman
    (Admin only)
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    result = await db.execute(
        select(Document)
        .where(Document.craftsman_id == profile_id)
        .order_by(Document.uploaded_at.desc())
    )
    documents = result.scalars().all()

    return [DocumentResponse.from_orm(doc) for doc in documents]
