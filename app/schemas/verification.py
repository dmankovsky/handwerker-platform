from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class DocumentType(str, Enum):
    """Types of verification documents"""
    BUSINESS_LICENSE = "business_license"
    HANDWERKSKAMMER_CERTIFICATE = "handwerkskammer_certificate"
    INSURANCE_CERTIFICATE = "insurance_certificate"
    ID_CARD = "id_card"
    TAX_CERTIFICATE = "tax_certificate"
    OTHER = "other"


class DocumentUploadResponse(BaseModel):
    """Response after uploading a document"""
    id: int
    document_type: str
    filename: str
    file_size: int
    uploaded_at: datetime
    verified: bool

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    """Document details response"""
    id: int
    craftsman_profile_id: int
    document_type: str
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    uploaded_at: datetime
    verified: bool
    verified_at: Optional[datetime]
    verified_by: Optional[int]
    notes: Optional[str]

    class Config:
        from_attributes = True


class DocumentVerificationRequest(BaseModel):
    """Request to verify a document (admin only)"""
    verified: bool
    notes: Optional[str] = None


class VerificationStatusResponse(BaseModel):
    """Craftsman verification status"""
    profile_id: int
    is_verified: bool
    handwerkskammer_number: Optional[str]
    documents_count: int
    verified_documents_count: int
    pending_verification: bool
    verification_date: Optional[datetime]
