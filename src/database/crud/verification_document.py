"""
验证文档 CRUD 操作
Verification Document CRUD Operations
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..models.verification_document import VerificationDocument


def create_verification_document(
    db: Session,
    relationship_id: int,
    user_id: int,
    filename: str,
    file_path: str,
    file_size: int,
    file_type: str,
    document_type: Optional[str] = None,
    description: Optional[str] = None
) -> VerificationDocument:
    """创建验证文档记录"""
    doc = VerificationDocument(
        relationship_id=relationship_id,
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_type,
        document_type=document_type,
        description=description
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_document_by_id(db: Session, document_id: int) -> Optional[VerificationDocument]:
    """根据ID获取文档"""
    return db.query(VerificationDocument).filter(VerificationDocument.id == document_id).first()


def get_documents_by_relationship(
    db: Session,
    relationship_id: int
) -> List[VerificationDocument]:
    """获取某个关系的所有验证文档"""
    return db.query(VerificationDocument).filter(
        VerificationDocument.relationship_id == relationship_id
    ).order_by(VerificationDocument.uploaded_at.desc()).all()


def get_documents_by_user(
    db: Session,
    user_id: int,
    limit: int = 100
) -> List[VerificationDocument]:
    """获取用户上传的所有文档"""
    return db.query(VerificationDocument).filter(
        VerificationDocument.user_id == user_id
    ).order_by(VerificationDocument.uploaded_at.desc()).limit(limit).all()


def delete_document(db: Session, document_id: int) -> bool:
    """删除文档记录"""
    doc = get_document_by_id(db, document_id)
    if doc:
        db.delete(doc)
        db.commit()
        return True
    return False


def get_document_stats(db: Session, relationship_id: int) -> dict:
    """获取某个关系的文档统计"""
    docs = get_documents_by_relationship(db, relationship_id)
    total_size = sum(doc.file_size or 0 for doc in docs)
    
    return {
        "total_documents": len(docs),
        "total_size": total_size,
        "document_types": list(set(doc.document_type for doc in docs if doc.document_type))
    }
