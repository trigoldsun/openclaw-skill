#!/usr/bin/env python3
"""
User Permission Manager

批量用户权限管理工具
- 按角色批量授予/撤销系统权限
- 配置数据权限范围
- 生成操作日志和审计报告
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional


class PermissionManager:
    """用户权限管理器"""
    
    def __init__(self):
        self.operation_log = []
        
    def log_operation(self, op_name: str, purpose: str, result: str, details: dict = None):
        """记录操作到审计日志"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation_name": op_name,
            "purpose": purpose,
            "result": result,
            "details": details or {}
        }
        self.operation_log.append(entry)
        return entry
    
    def list_roles(self, role_filter: str = None) -> List[Dict]:
        """
        获取角色列表
        
        :param role_filter: 可选过滤器 (admin, user, manager 等)
        :return: 角色列表 [{"id": str, "name": str, "description": str}]
        """
        # 示例：模拟从数据库查询
        all_roles = [
            {"id": "role_admin", "name": "超级管理员", "description": "系统管理员"},
            {"id": "role_dept_manager", "name": "部门经理", "description": "部门管理者"},
            {"id": "role_user", "name": "普通用户", "description": "普通员工"},
            {"id": "role_analyst", "name": "数据分析师", "description": "数据分析人员"},
            {"id": "role_auditor", "name": "审计员", "description": "审计人员"}
        ]
        
        if role_filter:
            filtered = [r for r in all_roles if role_filter.lower() in r["name"].lower()]
            return filtered
        
        return all_roles
    
    def grant_system_permissions(
        self, 
        role_id: str, 
        permissions: List[Dict], 
        operation_purpose: str = "批量授权"
    ) -> Dict:
        """
        授予系统权限
        
        :param role_id: 角色 ID
        :param permissions: 权限列表 [{"resource_type": str, "resource_id": str, "actions": [...]}]
        :param operation_purpose: 操作目的描述
        :return: 授权结果
        """
        before_state = self._get_role_permissions(role_id, "system")
        
        # 模拟授予权限逻辑
        granted_count = len(permissions)
        
        after_state = self._get_role_permissions(role_id, "system")
        
        result = self.log_operation(
            op_name="grant_system_permissions",
            purpose=operation_purpose,
            result=f"成功授予 {granted_count} 个系统权限",
            details={
                "role_id": role_id,
                "permissions_granted": permissions,
                "before": before_state,
                "after": after_state
            }
        )
        
        return {
            "success": True,
            "granted_count": granted_count,
            "log_entry": result
        }
    
    def revoke_system_permissions(
        self, 
        role_id: str, 
        permission_ids: List[str], 
        operation_purpose: str = "批量撤销"
    ) -> Dict:
        """
        撤销系统权限
        
        :param role_id: 角色 ID
        :param permission_ids: 要撤销的权限 ID 列表
        :param operation_purpose: 操作目的描述
        :return: 撤销结果
        """
        revoked_count = len(permission_ids)
        
        result = self.log_operation(
            op_name="revoke_system_permissions",
            purpose=operation_purpose,
            result=f"成功撤销 {revoked_count} 个系统权限",
            details={
                "role_id": role_id,
                "permissions_revoked": permission_ids
            }
        )
        
        return {
            "success": True,
            "revoked_count": revoked_count,
            "log_entry": result
        }
    
    def set_data_permission(
        self, 
        role_id: str, 
        scope_level: str, 
        department_ids: List[str] = None,
        record_filters: Dict = None,
        hidden_fields: List[str] = None,
        operation_purpose: str = "配置数据权限"
    ) -> Dict:
        """
        设置数据权限
        
        :param role_id: 角色 ID
        :param scope_level: 数据范围级别 (all, dept_sub, dept, own, custom)
        :param department_ids: 自定义范围时的部门 ID 列表
        :param record_filters: 记录过滤条件
        :param hidden_fields: 隐藏字段列表
        :param operation_purpose: 操作目的描述
        :return: 配置结果
        """
        data_permission = {
            "scope_level": scope_level,
            "department_ids": department_ids or [],
            "record_filters": record_filters or {},
            "hidden_fields": hidden_fields or []
        }
        
        result = self.log_operation(
            op_name="set_data_permission",
            purpose=operation_purpose,
            result=f"数据权限已设置为：{self._scope_level_to_chinese(scope_level)}",
            details={
                "role_id": role_id,
                "data_permission": data_permission
            }
        )
        
        return {
            "success": True,
            "data_permission": data_permission,
            "log_entry": result
        }
    
    def batch_authorize_roles(
        self, 
        role_assignments: List[Dict], 
        operator: str = "system",
        reason: str = ""
    ) -> Dict:
        """
        批量授权多个角色
        
        :param role_assignments: 角色授权配置列表
        :param operator: 操作用户
        :param reason: 变更原因
        :return: 批量授权汇总报告
        """
        total_affected = 0
        changes_summary = []
        
        for assignment in role_assignments:
            role_id = assignment["role_id"]
            role_name = assignment.get("role_name", role_id)
            
            # 处理系统权限
            if "add_system_permissions" in assignment:
                self.grant_system_permissions(
                    role_id, 
                    assignment["add_system_permissions"],
                    operation_purpose=f"{operator}: {reason}"
                )
            
            if "remove_system_permissions" in assignment:
                self.revoke_system_permissions(
                    role_id,
                    assignment["remove_system_permissions"],
                    operation_purpose=f"{operator}: {reason}"
                )
            
            # 处理数据权限
            if "data_scope_level" in assignment:
                self.set_data_permission(
                    role_id,
                    assignment["data_scope_level"],
                    assignment.get("department_ids"),
                    assignment.get("record_filters"),
                    assignment.get("hidden_fields"),
                    operation_purpose=f"{operator}: {reason}"
                )
            
            total_affected += 1
            changes_summary.append({
                "role_id": role_id,
                "role_name": role_name,
                "updated_at": datetime.now().isoformat()
            })
        
        report = self.log_operation(
            op_name="batch_authorize_roles",
            purpose=f"批量授权 {len(role_assignments)} 个角色 - {reason}",
            result=f"成功影响 {total_affected} 个角色",
            details={
                "operator": operator,
                "reason": reason,
                "roles_affected": changes_summary
            }
        )
        
        return {
            "success": True,
            "total_affected": total_affected,
            "changes": changes_summary,
            "audit_report": report
        }
    
    def get_audit_log(self, limit: int = 50) -> List[Dict]:
        """获取操作日志"""
        return self.operation_log[-limit:]
    
    def _get_role_permissions(self, role_id: str, perm_type: str) -> Any:
        """模拟获取角色当前权限（实际应查询数据库）"""
        return {"mock": "current_state"}
    
    def _scope_level_to_chinese(self, level: str) -> str:
        """转换数据范围级别为中文"""
        mapping = {
            "all": "全部数据",
            "dept_sub": "本部门及以下",
            "dept": "仅本部门",
            "own": "仅本人",
            "custom": "自定义"
        }
        return mapping.get(level, level)


# CLI usage example
if __name__ == "__main__":
    pm = PermissionManager()
    
    print("=== 用户权限管理系统 ===\n")
    
    # 1. 显示所有角色
    roles = pm.list_roles()
    print(f"【角色列表】共 {len(roles)} 个角色:")
    for r in roles:
        print(f"  - {r['id']}: {r['name']}")
    
    # 2. 示例：为部门经理授予权限
    print("\n=== 示例操作 ===")
    pm.batch_authorize_roles([
        {
            "role_id": "role_dept_manager",
            "role_name": "部门经理",
            "add_system_permissions": [
                {"resource_type": "menu", "resource_id": "MENU_USER_MGT", "actions": ["view", "create", "update"]},
                {"resource_type": "module", "resource_id": "MODULE_WORKFLOW", "actions": ["view", "approve"]}
            ],
            "data_scope_level": "dept_sub",
            "department_ids": ["dept_001", "dept_002"]
        }
    ], operator="admin_user", reason="新组织架构调整")
    
    # 3. 查看操作日志
    print("\n=== 最近操作日志 ===")
    for entry in pm.get_audit_log(3):
        print(f"[{entry['timestamp']}] {entry['operation_name']}")
        print(f"  目的：{entry['purpose']}")
        print(f"  结果：{entry['result']}\n")
