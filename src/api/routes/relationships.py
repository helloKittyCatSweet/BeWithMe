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
    log_action
)

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
    reviewer_id: int,  # 实际应用中从 JWT token 获取并验证管理员权限
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
    
    # TODO: 验证 reviewer_id 是否为管理员
    # if not is_admin(reviewer_id):
    #     raise HTTPException(status_code=403, detail="需要管理员权限")
    
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
    reviewer_id: int,  # 实际应用中从 JWT token 获取并验证管理员权限
    db: Session = Depends(get_db)
):
    """
    获取待审核的关系列表（管理员功能）
    
    返回所有状态为 pending 的关系申请
    """
    # TODO: 验证 reviewer_id 是否为管理员
    # if not is_admin(reviewer_id):
    #     raise HTTPException(status_code=403, detail="需要管理员权限")
    
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
