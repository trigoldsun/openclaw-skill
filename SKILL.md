---
name: user-permissions
description: Comprehensive user permission management system. Use when managing user roles, assigning system permissions (application-level access), or configuring data permissions (database/record-level access). Supports batch authorization by role across two dimensions: system permissions (API routes, menu access, functional modules) and data permissions (data scope, department isolation, custom filters). Always describe operation names and purposes for audit trail.
---

# User Permissions Management System

## Overview

This skill enables comprehensive user permission management across **two dimensions**:
1. **System Permissions** - Application-level access control (API routes, menus, functional modules)
2. **Data Permissions** - Data-level access control (data scope, department isolation, record filters)

All operations must include operation name and purpose description for audit trail.

## Operation Logging Requirement

**Always report:**
- **Operation Name:** What action is being performed
- **Purpose:** Why this action is needed
- **Result:** Outcome of the operation

Example format:
```
### 1️⃣ 角色列表查询
- **操作名：** `list_roles()` 
- **目的：** 获取系统中所有角色及对应 ID，用于后续批量授权
- **结果：** 查询成功，共返回 5 个角色
```

## Two-Dimension Permission Model

### Dimension 1: System Permissions (系统权限)

Controls application-level functionality access:

| Permission Type | Description | Examples |
|----------------|-------------|----------|
| API Routes | Backend endpoint access | `/api/users/*`, `/admin/settings` |
| Menu Items | Frontend navigation visibility | Dashboard, User Management, Reports |
| Functional Modules | Feature toggles | Export, Delete, Approve, Audit Logs |
| UI Components | Interface element visibility | Buttons, Forms, Tables |

**Permission Levels:**
- `view` - Read only access
- `create` - Can create new records
- `update` - Can modify existing records
- `delete` - Can delete records
- `manage` - Full administrative access

### Dimension 2: Data Permissions (数据权限)

Controls data-level scope and filtering:

| Permission Type | Description | Examples |
|----------------|-------------|----------|
| Data Scope | Range of visible data | All, Department, Custom |
| Department Isolation | Organizational level filtering | Own dept, Sub-depts, All org |
| Record Filters | SQL WHERE conditions | `created_by = {user_id}` |
| Field-Level Access | Column visibility | Hide sensitive fields |

**Data Scope Levels:**
- **全部数据 (Full)** - Access all data in system
- **本部门及以下 (Dept & Sub-dept)** - Current dept and child departments
- **仅本部门 (Own Dept)** - Only current department
- **仅本人 (Own)** - Only records created by self
- **自定义 (Custom)** - Specific records/departments selected manually

## Batch Authorization Workflow

### Pre-operation Checklist
Before any batch authorization, verify:
1. ✅ Role IDs are valid and exist in system
2. ✅ Target permissions exist and are active
3. ✅ No conflicting permissions for same role+resource
4. ✅ Operator has administrative privileges

### Standard Authorization Flow

#### Phase 1: Preparation
1. **验证角色列表** - Confirm target roles exist
2. **收集权限清单** - Gather required system and data permissions
3. **生成授权计划** - Create batch operation plan

#### Phase 2: Execution
1. **授予系统权限** - Apply system permission grants
2. **配置数据权限** - Set data scope and filters
3. **验证应用结果** - Test actual access levels

#### Phase 3: Confirmation
1. **输出授权报告** - Document what was changed
2. **生成操作日志** - Create audit trail entry

## Role-Based Permission Templates

Use these templates as starting points:

### Administrator Role
```
System Permissions:
- view, create, update, delete, manage → ALL resources

Data Permissions:
- Data Scope: 全部数据
- Department Isolation: All organization
```

### Department Manager Role
```
System Permissions:
- view, update → User Management (own dept)
- view, approve → Workflow Approval
- manage → Department Settings

Data Permissions:
- Data Scope: 本部门及以下
- Department Isolation: Own dept + sub-depts
```

### Regular User Role
```
System Permissions:
- view, create → Self-service modules
- update → Personal profile only

Data Permissions:
- Data Scope: 仅本人
- Department Isolation: Own only
```

## Reporting Format for Each Operation

When performing permission operations, always use this structure:

```
## [Step Number] · [Operation Name]

**目的：** [Why you're doing this]

**操作细节：**
- Input: [Parameters/Arguments]
- Process: [What actions taken]
- Output: [Results/Changes made]

**审计记录：**
- Timestamp: [Time]
- Operator: [Who executed]
- Change Log: [Before → After]
```

## Resources (optional)

Create only the resource directories this skill actually needs. Delete this section if no resources are required.

### scripts/
Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.

**Examples from other skills:**
- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py` - utilities for PDF manipulation
- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing

**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by Codex for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to inform Codex's process and thinking.

**Examples from other skills:**
- Product management: `communication.md`, `context_building.md` - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Codex should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within the output Codex produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---

**Not every skill requires all three types of resources.**
