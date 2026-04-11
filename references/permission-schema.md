# Permission Data Schema

This document defines the standard data structures for user permission management.

## System Permission Object

```json
{
  "resource_type": "api|menu|module|component",
  "resource_id": "string - unique identifier",
  "resource_name": "string - human readable name",
  "actions": ["view", "create", "update", "delete", "manage"]
}
```

### Field Descriptions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| resource_type | string | Category of resource | `"api"`, `"menu"`, `"module"`, `"component"` |
| resource_id | string | Unique identifier | `"/api/users/*"`, `"MENU_USERS_MGT"` |
| resource_name | string | Display name | `"用户管理"`, `"API 接口"` |
| actions | array | Allowed action permissions | `["view", "create", "update"]` |

## Data Permission Object

```json
{
  "scope_level": "all|dept_sub|dept|own|custom",
  "department_ids": ["array of dept IDs if custom"],
  "record_filters": {
    "field": "created_by",
    "operator": "=",
    "value_template": "{user_id}"
  },
  "hidden_fields": ["field1", "field2"]
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| scope_level | string | Data visibility level |
| department_ids | array | Dept IDs for custom scope (optional) |
| record_filters | object | SQL WHERE condition template |
| hidden_fields | array | Fields to hide from view |

### Scope Level Values

| Value | Meaning | Description |
|-------|---------|-------------|
| `all` | 全部数据 | Access all system data |
| `dept_sub` | 本部门及以下 | Current dept + all sub-departments |
| `dept` | 仅本部门 | Only current department |
| `own` | 仅本人 | Only records created by self |
| `custom` | 自定义 | Specific departments selected manually |

## Role Permission Assignment Object

```json
{
  "role_id": "string - role identifier",
  "role_name": "string - display name",
  "system_permissions": [
    // Array of System Permission Objects
  ],
  "data_permissions": {
    // Single Data Permission Object
  }
}
```

## Batch Authorization Request

```json
{
  "operation_name": "string - operation identifier",
  "purpose": "string - reason for this batch",
  "target_roles": [
    {
      "role_id": "string",
      "role_name": "string",
      "add_system_permissions": [],
      "remove_system_permissions": [],
      "data_scope_level": "string",
      "override_data_permissions": boolean
    }
  ],
  "audit_info": {
    "operator": "string",
    "timestamp": "ISO-8601",
    "reason": "string"
  }
}
```

## Response Format

```json
{
  "success": boolean,
  "changes_made": {
    "roles_affected": number,
    "permissions_granted": number,
    "permissions_revoked": number
  },
  "details": [
    {
      "role_id": "string",
      "role_name": "string",
      "system_changes": [],
      "data_changes": {}
    }
  ],
  "errors": []
}
```
