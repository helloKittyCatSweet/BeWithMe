"""
亲属关系验证 API 路由
Relationship Verification API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import os
import shutil
import json

from ...database import (
    get_db,
    create_relationship,
    get_user_relationships,
    get_relationship_by_id,
    approve_relationship,
    reject_relationship,
    check_relationship_valid,
    get_pending_verifications,
    RelationshipType,
    VerificationStatus,
    log_action,
    create_verification_document,
    get_documents_by_relationship,
    delete_document,
)
from ..auth import get_current_admin

router = APIRouter()


# ============ Pydantic 模型 ============

class RelationshipCreate(BaseModel):
    relative_name: str
    relationship_type: RelationshipType
    purpose: str
    birth_date: Optional[datetime] = None
    death_date: Optional[datetime] = None
    additional_info: Optional[str] = None


class RelationshipResponse(BaseModel):
    id: int
    user_id: int
    relative_name: str
    relationship_type: RelationshipType
    is_deceased: bool
    verification_status: VerificationStatus
    purpose: str
    verification_document: Optional[str]
    verified_at: Optional[datetime]
    verified_by: Optional[str]
    reviewer_notes: Optional[str]
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class VerificationAction(BaseModel):
    action: str  # "approve" or "reject"
    reviewer: str
    notes: Optional[str] = None


# ============ API 端点 ============

@router.post("/register", response_model=RelationshipResponse)
async def register_relationship(
    relationship: RelationshipCreate,
    user_id: int,  # 实际应用中从 JWT token 获取
    db: Session = Depends(get_db)
):
    """
    注册亲属关系
    
    用户需要声明与要克隆声音的亲属的关系
    """
    try:
        new_relationship = create_relationship(
            db=db,
            user_id=user_id,
            relative_name=relationship.relative_name,
            relationship_type=relationship.relationship_type,
            purpose=relationship.purpose,
            birth_date=relationship.birth_date,
            death_date=relationship.death_date,
            additional_info=relationship.additional_info
        )
        
        return new_relationship
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{relationship_id}/upload-document")
async def upload_verification_document(
    relationship_id: int,
    user_id: int,  # 实际应用中从 JWT token 获取
    document: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传验证文件
    
    用户需要上传户口本、死亡证明等文件证明亲属关系
    """
    # 获取关系记录
    relationship_record = get_relationship_by_id(db, relationship_id)
    
    if not relationship_record:
        raise HTTPException(status_code=404, detail="关系记录不存在")
    
    # 验证用户权限
    if relationship_record.user_id != user_id:
        log_action(db, user_id, "unauthorized_document_upload", "Relationship", 
                   relationship_id, success=False, error_message="User mismatch")
        raise HTTPException(status_code=403, detail="无权上传此关系的文件")
    
    # 创建上传目录
    upload_dir = "data/verification_documents"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 保存文件
    file_extension = os.path.splitext(document.filename)[1]
    file_path = os.path.join(upload_dir, f"rel_{relationship_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_extension}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(document.file, buffer)
        
        # 更新数据库记录
        relationship_record.verification_document = file_path
        db.commit()
        
        log_action(db, user_id, "document_uploaded", "Relationship", relationship_id,
                   details=f"Uploaded {document.filename}")
        
        return {
            "status": "success",
            "relationship_id": relationship_id,
            "document_path": file_path,
            "message": "验证文件上传成功"
        }
    
    except Exception as e:
        log_action(db, user_id, "document_upload_failed", "Relationship", 
                   relationship_id, success=False, error_message=str(e))
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.post("/{relationship_id}/upload-documents")
async def upload_multiple_verification_documents(
    relationship_id: int,
    user_id: int,  # 实际应用中从 JWT token 获取
    documents: List[UploadFile] = File(...),
    document_types: Optional[str] = Form(None),  # JSON string of document types
    descriptions: Optional[str] = Form(None),  # JSON string of descriptions
    db: Session = Depends(get_db)
):
    """
    上传多个验证文件
    
    支持一次上传多个文件（如户口本、死亡证明、身份证等）
    """
    # 获取关系记录
    relationship_record = get_relationship_by_id(db, relationship_id)
    
    if not relationship_record:
        raise HTTPException(status_code=404, detail="关系记录不存在")
    
    # 验证用户权限
    if relationship_record.user_id != user_id:
        log_action(db, user_id, "unauthorized_document_upload", "Relationship", 
                   relationship_id, success=False, error_message="User mismatch")
        raise HTTPException(status_code=403, detail="无权上传此关系的文件")
    
    # 创建上传目录
    upload_dir = "data/verification_documents"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 解析文档类型和描述（如果提供）
    doc_types_list = []
    descriptions_list = []
    
    if document_types:
        try:
            doc_types_list = json.loads(document_types)
        except:
            doc_types_list = []
    
    if descriptions:
        try:
            descriptions_list = json.loads(descriptions)
        except:
            descriptions_list = []
    
    uploaded_files = []
    failed_files = []
    
    for idx, document in enumerate(documents):
        try:
            # 验证文件大小（最大 10MB）
            content = await document.read()
            file_size = len(content)
            
            if file_size > 10 * 1024 * 1024:  # 10MB
                failed_files.append({
                    "filename": document.filename,
                    "error": "文件大小超过 10MB 限制"
                })
                continue
            
            # 保存文件
            file_extension = os.path.splitext(document.filename)[1]
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            file_path = os.path.join(
                upload_dir, 
                f"rel_{relationship_id}_{timestamp}_{idx}{file_extension}"
            )
            
            with open(file_path, "wb") as buffer:
                buffer.write(content)
            
            # 获取文档类型和描述
            doc_type = doc_types_list[idx] if idx < len(doc_types_list) else None
            description = descriptions_list[idx] if idx < len(descriptions_list) else None
            
            # 创建数据库记录
            doc_record = create_verification_document(
                db=db,
                relationship_id=relationship_id,
                user_id=user_id,
                filename=document.filename,
                file_path=file_path,
                file_size=file_size,
                file_type=document.content_type or "application/octet-stream",
                document_type=doc_type,
                description=description
            )
            
            uploaded_files.append({
                "id": doc_record.id,
                "filename": document.filename,
                "file_path": file_path,
                "file_size": file_size,
                "document_type": doc_type
            })
            
            # 重置文件指针
            await document.seek(0)
            
        except Exception as e:
            failed_files.append({
                "filename": document.filename,
                "error": str(e)
            })
    
    # 记录审计日志
    log_action(
        db, user_id, "multiple_documents_uploaded", "Relationship", 
        relationship_id,
        details=f"Uploaded {len(uploaded_files)} files, {len(failed_files)} failed"
    )
    
    return {
        "status": "success" if uploaded_files else "partial_success",
        "relationship_id": relationship_id,
        "uploaded_count": len(uploaded_files),
        "failed_count": len(failed_files),
        "uploaded_files": uploaded_files,
        "failed_files": failed_files,
        "message": f"成功上传 {len(uploaded_files)} 个文件" + (f"，{len(failed_files)} 个失败" if failed_files else "")
    }


@router.get("/{relationship_id}/documents")
async def get_relationship_documents(
    relationship_id: int,
    user_id: int,  # 实际应用中从 JWT token 获取
    db: Session = Depends(get_db)
):
    """获取某个关系的所有验证文档"""
    # 获取关系记录
    relationship_record = get_relationship_by_id(db, relationship_id)
    
    if not relationship_record:
        raise HTTPException(status_code=404, detail="关系记录不存在")
    
    # 验证用户权限
    if relationship_record.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权查看此关系的文件")
    
    # 获取文档列表
    documents = get_documents_by_relationship(db, relationship_id)
    
    return {
        "relationship_id": relationship_id,
        "document_count": len(documents),
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "file_size": doc.file_size,
                "file_type": doc.file_type,
                "document_type": doc.document_type,
                "description": doc.description,
                "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None
            }
            for doc in documents
        ]
    }


@router.delete("/{relationship_id}/documents/{document_id}")
async def delete_verification_document(
    relationship_id: int,
    document_id: int,
    user_id: int,  # 实际应用中从 JWT token 获取
    db: Session = Depends(get_db)
):
    """删除验证文档"""
    from ...database.crud.verification_document import get_document_by_id
    
    # 获取文档记录
    doc = get_document_by_id(db, document_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 验证文档属于指定关系
    if doc.relationship_id != relationship_id:
        raise HTTPException(status_code=400, detail="文档不属于该关系")
    
    # 验证用户权限
    if doc.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权删除此文档")
    
    # 删除物理文件
    try:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except Exception as e:
        log_action(db, user_id, "document_file_delete_failed", "VerificationDocument",
                   document_id, success=False, error_message=str(e))
    
    # 删除数据库记录
    success = delete_document(db, document_id)
    
    if success:
        log_action(db, user_id, "document_deleted", "VerificationDocument", document_id)
        return {"status": "success", "message": "文档已删除"}
    else:
        raise HTTPException(status_code=500, detail="删除失败")


@router.get("/list", response_model=List[RelationshipResponse])
async def list_user_relationships(
    user_id: int,  # 实际应用中从 JWT token 获取
    status: Optional[VerificationStatus] = None,
    db: Session = Depends(get_db)
):
    """
    获取用户的所有亲属关系记录
    
    可选参数 status 用于筛选特定状态的记录
    """
    relationships = get_user_relationships(db, user_id, status)
    return relationships


@router.get("/{relationship_id}", response_model=RelationshipResponse)
async def get_relationship_detail(
    relationship_id: int,
    user_id: int,  # 实际应用中从 JWT token 获取
    db: Session = Depends(get_db)
):
    """获取关系详情"""
    relationship = get_relationship_by_id(db, relationship_id)
    
    if not relationship:
        raise HTTPException(status_code=404, detail="关系记录不存在")
    
    # 验证用户权限（除非是管理员）
    if relationship.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权查看此记录")
    
    return relationship


@router.get("/{relationship_id}/status")
async def check_relationship_status(
    relationship_id: int,
    user_id: int,  # 实际应用中从 JWT token 获取
    db: Session = Depends(get_db)
):
    """
    检查关系验证状态
    
    用于在进行声音克隆前确认关系是否已验证
    """
    relationship = get_relationship_by_id(db, relationship_id)
    
    if not relationship:
        raise HTTPException(status_code=404, detail="关系记录不存在")
    
    if relationship.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权查看此记录")
    
    is_valid = check_relationship_valid(db, relationship_id)
    
    return {
        "relationship_id": relationship_id,
        "relative_name": relationship.relative_name,
        "verification_status": relationship.verification_status.value,
        "is_valid": is_valid,
        "verified_at": relationship.verified_at,
        "expires_at": relationship.expires_at,
        "can_clone_voice": is_valid
    }


@router.post("/{relationship_id}/verify", response_model=RelationshipResponse)
async def verify_relationship(
    relationship_id: int,
    action: VerificationAction,
    reviewer_id: int,
    admin_user=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    审核关系（管理员功能）
    
    管理员审核用户提交的亲属关系
    action: "approve" 或 "reject"
    """
    relationship = get_relationship_by_id(db, relationship_id)
    
    if not relationship:
        raise HTTPException(status_code=404, detail="关系记录不存在")
    
    if admin_user.id != reviewer_id:
        raise HTTPException(status_code=403, detail="reviewer_id mismatch")
    
    try:
        if action.action == "approve":
            updated_relationship = approve_relationship(
                db=db,
                relationship_id=relationship_id,
                reviewer=action.reviewer,
                notes=action.notes
            )
            message = "关系审核通过"
        
        elif action.action == "reject":
            if not action.notes:
                raise HTTPException(status_code=400, detail="拒绝时必须提供原因")
            
            updated_relationship = reject_relationship(
                db=db,
                relationship_id=relationship_id,
                reviewer=action.reviewer,
                reason=action.notes
            )
            message = "关系审核拒绝"
        
        else:
            raise HTTPException(status_code=400, detail="无效的操作，必须是 'approve' 或 'reject'")
        
        return updated_relationship
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/pending", response_model=List[RelationshipResponse])
async def get_pending_relationships(
    reviewer_id: int,
    admin_user=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取待审核的关系列表（管理员功能）
    
    返回所有状态为 pending 的关系申请
    """
    if admin_user.id != reviewer_id:
        raise HTTPException(status_code=403, detail="reviewer_id mismatch")
    
    pending = get_pending_verifications(db)
    return pending


@router.delete("/{relationship_id}")
async def delete_relationship(
    relationship_id: int,
    user_id: int,  # 实际应用中从 JWT token 获取
    db: Session = Depends(get_db)
):
    """
    删除关系记录
    
    用户可以删除自己的待审核或已拒绝的关系记录
    """
    relationship = get_relationship_by_id(db, relationship_id)
    
    if not relationship:
        raise HTTPException(status_code=404, detail="关系记录不存在")
    
    if relationship.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权删除此记录")
    
    # 已通过审核的记录不允许删除（需联系管理员）
    if relationship.verification_status == VerificationStatus.APPROVED:
        raise HTTPException(status_code=400, detail="已审核通过的记录不能删除，请联系管理员")
    
    # 删除关联的验证文件
    if relationship.verification_document and os.path.exists(relationship.verification_document):
        try:
            os.remove(relationship.verification_document)
        except Exception as e:
            print(f"删除文件失败: {e}")
    
    # 删除记录
    log_action(db, user_id, "relationship_deleted", "Relationship", relationship_id)
    db.delete(relationship)
    db.commit()
    
    return {
        "status": "success",
        "message": "关系记录已删除"
    }


# 注意：区块链保存功能已移至前端，前端直接调用智能合约
