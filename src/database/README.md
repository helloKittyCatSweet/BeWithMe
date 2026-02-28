# 数据库模块结构说明

## 📁 目录结构

```
src/database/
├── __init__.py          # 模块导出（统一入口）
├── base.py              # 基础配置（Base, 枚举类型）
├── connection.py        # 数据库连接和会话管理
│
├── models/              # 数据模型（按功能分离）
│   ├── __init__.py
│   ├── user.py          # 用户模型
│   ├── relationship.py  # 亲属关系模型（核心验证表）
│   ├── voice_profile.py # 音色档案模型
│   ├── agent_profile.py # Agent 档案模型
│   ├── conversation.py  # 对话记录模型
│   ├── audit_log.py     # 审计日志模型
│   └── system_config.py # 系统配置模型
│
└── crud/                # CRUD 操作（按功能分离）
    ├── __init__.py
    ├── user.py          # 用户管理操作
    ├── relationship.py  # 关系管理操作
    ├── voice_profile.py # 音色档案操作
    ├── conversation.py  # 对话记录操作
    ├── audit.py         # 审计日志操作
    └── stats.py         # 统计查询操作
```

## 🎯 设计原则

### 1. 模块化分离
- **每个模型一个文件** - 更易于理解和维护
- **每个功能一个 CRUD 文件** - 职责清晰
- **统一导出** - 通过 `__init__.py` 提供简洁的导入接口

### 2. 清晰的职责划分
- `base.py` - 基础配置和枚举类型
- `connection.py` - 数据库连接管理
- `models/` - 纯数据模型定义
- `crud/` - 数据库操作逻辑

### 3. 易于测试和扩展
- 新增模型：在 `models/` 添加文件，更新 `models/__init__.py`
- 新增操作：在 `crud/` 添加文件，更新 `crud/__init__.py`
- 不影响其他模块

## 📦 使用方式

### 导入示例

```python
# 1. 导入基础类型
from src.database import Base, RelationshipType, VerificationStatus

# 2. 导入模型
from src.database import User, Relationship, VoiceProfile

# 3. 导入连接管理
from src.database import get_db, get_db_session, init_db

# 4. 导入 CRUD 操作
from src.database import (
    create_user,
    get_user_by_username,
    create_relationship,
    approve_relationship,
    get_system_stats
)

# 5. 或者导入整个模块
from src import database as db

user = db.create_user(session, ...)
stats = db.get_system_stats(session)
```

### 使用模式

#### FastAPI 路由中使用
```python
from fastapi import Depends
from sqlalchemy.orm import Session
from src.database import get_db, create_user, User

@router.post("/users")
def register_user(username: str, db: Session = Depends(get_db)):
    user = create_user(db, username=username, ...)
    return user
```

#### 独立脚本中使用
```python
from src.database import get_db_session, get_system_stats

with get_db_session() as db:
    stats = get_system_stats(db)
    print(stats)
```

## 🔧 维护指南

### 添加新模型

1. 在 `models/` 创建新文件（如 `models/new_model.py`）：
```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship as db_relationship
from ..base import Base

class NewModel(Base):
    __tablename__ = "new_models"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
```

2. 在 `models/__init__.py` 中导出：
```python
from .new_model import NewModel

__all__ = [..., "NewModel"]
```

3. 在 `src/database/__init__.py` 中导出：
```python
from .models import (..., NewModel)

__all__ = [..., "NewModel"]
```

### 添加新 CRUD 操作

1. 在 `crud/` 创建或修改文件（如 `crud/new_model.py`）：
```python
from sqlalchemy.orm import Session
from ..models import NewModel

def create_new_model(db: Session, name: str) -> NewModel:
    model = NewModel(name=name)
    db.add(model)
    db.commit()
    db.refresh(model)
    return model
```

2. 在 `crud/__init__.py` 中导出：
```python
from .new_model import create_new_model

__all__ = [..., "create_new_model"]
```

3. 在 `src/database/__init__.py` 中导出：
```python
from .crud import (..., create_new_model)

__all__ = [..., "create_new_model"]
```

## 📊 文件大小对比

### 重构前（单体文件）
```
models.py    - 256 lines
crud.py      - 300+ lines
```

### 重构后（模块化）
```
models/user.py           - 44 lines
models/relationship.py   - 52 lines
models/voice_profile.py  - 45 lines
models/agent_profile.py  - 47 lines
models/conversation.py   - 49 lines
models/audit_log.py      - 41 lines
models/system_config.py  - 24 lines

crud/user.py            - 95 lines
crud/relationship.py    - 161 lines
crud/voice_profile.py   - 100 lines
crud/conversation.py    - 105 lines
crud/audit.py           - 76 lines
crud/stats.py           - 77 lines
```

**优势：**
- ✅ 每个文件不超过 200 行
- ✅ 职责清晰，易于定位
- ✅ 修改一个模型不影响其他模型
- ✅ 便于代码审查和测试

## 🧪 测试

```bash
# 测试导入
python -c "from src.database import User, create_user, get_system_stats; print('✅ OK')"

# 测试数据库初始化
python init_database.py

# 测试管理工具
python admin_tool.py
```

## 🔄 迁移说明

如果需要回退到旧版本，备份文件位于：
- `src/database/models_old.py.bak`
- `src/database/crud_old.py.bak`

## 📚 相关文档

- [数据库设计文档](../../FAMILY_VERIFICATION.md)
- [API 接口文档](../api/routes/relationships.py)
- [管理员工具](../../admin_tool.py)
