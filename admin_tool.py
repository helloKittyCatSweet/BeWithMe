#!/usr/bin/env python3
"""
管理员工具 - 审核亲属关系
Admin Tool - Relationship Verification
"""
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database import (
    get_db_session,
    get_pending_verifications,
    get_relationship_by_id,
    approve_relationship,
    reject_relationship
)


def display_relationship(rel):
    """显示关系详情"""
    print("\n" + "=" * 80)
    print(f"📋 关系 ID: {rel.id}")
    print(f"👤 用户 ID: {rel.user_id}")
    print(f"👥 亲属姓名: {rel.relative_name}")
    print(f"🔗 关系类型: {rel.relationship_type.value}")
    print(f"💀 是否已故: {'是' if rel.is_deceased else '否'}")
    if rel.birth_date:
        print(f"🎂 出生日期: {rel.birth_date.strftime('%Y-%m-%d')}")
    if rel.death_date:
        print(f"⚰️  去世日期: {rel.death_date.strftime('%Y-%m-%d')}")
    print(f"📝 使用目的: {rel.purpose}")
    if rel.additional_info:
        print(f"ℹ️  其他信息: {rel.additional_info}")
    if rel.verification_document:
        print(f"📄 验证文件: {rel.verification_document}")
    print(f"📅 申请时间: {rel.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"✅ 当前状态: {rel.verification_status.value}")
    print("=" * 80)


def main():
    """主函数"""
    print("""
╔════════════════════════════════════════╗
║   👨‍💼 Be With Me - Admin Tool      ║
║   亲属关系审核管理                   ║
╚════════════════════════════════════════╝
    """)
    
    with get_db_session() as db:
        # 获取待审核的关系列表
        pending = get_pending_verifications(db)
        
        if not pending:
            print("✅ 没有待审核的关系申请")
            return
        
        print(f"📊 当前有 {len(pending)} 个待审核的关系申请\n")
        
        for idx, rel in enumerate(pending, 1):
            print(f"\n【{idx}/{len(pending)}】")
            display_relationship(rel)
            
            # 询问管理员操作
            print("\n请选择操作:")
            print("  [a] 批准 (Approve)")
            print("  [r] 拒绝 (Reject)")
            print("  [s] 跳过 (Skip)")
            print("  [q] 退出 (Quit)")
            
            choice = input("\n👉 请输入: ").strip().lower()
            
            if choice == 'a':
                # 批准
                reviewer = input("审核人姓名: ").strip()
                if not reviewer:
                    reviewer = "admin"
                
                notes = input("审核备注（可选）: ").strip()
                
                try:
                    approve_relationship(
                        db=db,
                        relationship_id=rel.id,
                        reviewer=reviewer,
                        notes=notes if notes else None
                    )
                    print(f"\n✅ 关系 {rel.id} 已批准\n")
                except Exception as e:
                    print(f"\n❌ 批准失败: {e}\n")
            
            elif choice == 'r':
                # 拒绝
                reviewer = input("审核人姓名: ").strip()
                if not reviewer:
                    reviewer = "admin"
                
                reason = input("拒绝原因（必填）: ").strip()
                
                if reason:
                    try:
                        reject_relationship(
                            db=db,
                            relationship_id=rel.id,
                            reviewer=reviewer,
                            reason=reason
                        )
                        print(f"\n❌ 关系 {rel.id} 已拒绝\n")
                    except Exception as e:
                        print(f"\n❌ 拒绝失败: {e}\n")
                else:
                    print("\n⚠️  拒绝原因不能为空，跳过此记录\n")
            
            elif choice == 's':
                # 跳过
                print("\n⏭️  跳过此记录\n")
                continue
            
            elif choice == 'q':
                # 退出
                print("\n👋 退出管理工具\n")
                break
            
            else:
                print("\n⚠️  无效的选择，跳过此记录\n")
            
            # 询问是否继续
            if idx < len(pending):
                cont = input("继续审核下一个？(y/n): ").strip().lower()
                if cont != 'y':
                    break
        
        print("\n✅ 审核完成！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，退出程序")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
