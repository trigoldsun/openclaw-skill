#!/usr/bin/env python3
"""
User Permission Manager

Batch user permission management tool:
- Batch grant/revoke system permissions by role
- Configure data permission scopes
- Generate operation logs and audit reports
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional


class PermissionManager:
    """User permission manager"""
    
    def __init__(self):
        self.operation_log = []
        
    def log_operation(self, op_name: str, purpose: str, result: str, details: dict = None):
        """Record operation to audit log"""
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
        Get role list
        
        :param role_filter: Optional filter (admin, user, manager, etc.)
        :return: Role list [{"id": str, "name": str, "description": str}]
        """
        # Example: Simulate query from database
        all_roles = [
            {"id": "role_admin", "name": "Super Administrator", "description": "System Administrator"},
            {"id": "role_dept_manager", "name": "Department Manager", "description": "Department Manager"},
            {"id": "role_user", "name": "Regular User", "description": "Regular Employee"},
            {"id": "role_analyst", "name": "Data Analyst", "description": "Data Analysis Staff"},
            {"id": "role_auditor", "name": "Auditor", "description": "Audit Staff"}
        ]
        
        if role_filter:
            filtered = [r for r in all_roles if role_filter.lower() in r["name"].lower()]
            return filtered
        
        return all_roles
    
    def grant_system_permissions(
        self, 
        role_id: str, 
        permissions: List[Dict], 
        operation_purpose: str = "Batch Authorization"
    ) -> Dict:
        """
        Grant system permissions
        
        :param role_id: Role ID
        :param permissions: Permission list [{"resource_type": str, "resource_id": str, "actions": [...]}]
        :param operation_purpose: Operation purpose description
        :return: Authorization result
        """
        before_state = self._get_role_permissions(role_id, "system")
        
        # Simulate granting permissions logic
        granted_count = len(permissions)
        
        after_state = self._get_role_permissions(role_id, "system")
        
        result = self.log_operation(
            op_name="grant_system_permissions",
            purpose=operation_purpose,
            result=f"Successfully granted {granted_count} system permissions",
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
        operation_purpose: str = "Batch Revocation"
    ) -> Dict:
        """
        Revoke system permissions
        
        :param role_id: Role ID
        :param permission_ids: List of permission IDs to revoke
        :param operation_purpose: Operation purpose description
        :return: Revocation result
        """
        revoked_count = len(permission_ids)
        
        result = self.log_operation(
            op_name="revoke_system_permissions",
            purpose=operation_purpose,
            result=f"Successfully revoked {revoked_count} system permissions",
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
        operation_purpose: str = "Configure Data Permission"
    ) -> Dict:
        """
        Set data permissions
        
        :param role_id: Role ID
        :param scope_level: Data scope level (all, dept_sub, dept, own, custom)
        :param department_ids: Department ID list for custom scope
        :param record_filters: Record filter conditions
        :param hidden_fields: Hidden field list
        :param operation_purpose: Operation purpose description
        :return: Configuration result
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
            result=f"Data permission set to: {self._scope_level_description(scope_level)}",
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
        Batch authorize multiple roles
        
        :param role_assignments: Role authorization configuration list
        :param operator: Operator user
        :param reason: Change reason
        :return: Batch authorization summary report
        """
        total_affected = 0
        changes_summary = []
        
        for assignment in role_assignments:
            role_id = assignment["role_id"]
            role_name = assignment.get("role_name", role_id)
            
            # Handle system permissions
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
            
            # Handle data permissions
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
            purpose=f"Batch authorize {len(role_assignments)} roles - {reason}",
            result=f"Successfully affected {total_affected} roles",
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
        """Get operation log"""
        return self.operation_log[-limit:]
    
    def _get_role_permissions(self, role_id: str, perm_type: str) -> Any:
        """Simulate getting current role permissions (should query database in production)"""
        return {"mock": "current_state"}
    
    def _scope_level_description(self, level: str) -> str:
        """Convert data scope level to English description"""
        mapping = {
            "all": "All Data",
            "dept_sub": "This Department and Sub-departments",
            "dept": "This Department Only",
            "own": "Own Data Only",
            "custom": "Custom"
        }
        return mapping.get(level, level)


# CLI usage example
if __name__ == "__main__":
    pm = PermissionManager()
    
    print("=== User Permission Management System ===\n")
    
    # 1. Show all roles
    roles = pm.list_roles()
    print(f"[Role List] Total {len(roles)} roles:")
    for r in roles:
        print(f"  - {r['id']}: {r['name']}")
    
    # 2. Example: Grant permissions for department manager
    print("\n=== Example Operation ===")
    pm.batch_authorize_roles([
        {
            "role_id": "role_dept_manager",
            "role_name": "Department Manager",
            "add_system_permissions": [
                {"resource_type": "menu", "resource_id": "MENU_USER_MGT", "actions": ["view", "create", "update"]},
                {"resource_type": "module", "resource_id": "MODULE_WORKFLOW", "actions": ["view", "approve"]}
            ],
            "data_scope_level": "dept_sub",
            "department_ids": ["dept_001", "dept_002"]
        }
    ], operator="admin_user", reason="New organizational structure adjustment")
    
    # 3. View operation log
    print("\n=== Recent Operation Log ===")
    for entry in pm.get_audit_log(3):
        print(f"[{entry['timestamp']}] {entry['operation_name']}")
        print(f"  Purpose: {entry['purpose']}")
        print(f"  Result: {entry['result']}\n")
