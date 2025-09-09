[创建 Function App MSI 用户并赋权限](#create-function-app-msi-user)

---

### <a name="create-function-app-msi-user"></a>创建 Function App MSI 用户并赋权限

```sql
-- 在目标数据库中创建 Azure AD 用户（对应 Function App 的 MSI）
CREATE USER [func-api-jwthyf3r6tdis] FROM EXTERNAL PROVIDER;

-- 给该用户赋读权限
ALTER ROLE db_datareader ADD MEMBER [func-api-jwthyf3r6tdis];

-- 如果需要写权限，也可以赋写权限
ALTER ROLE db_datawriter ADD MEMBER [func-api-jwthyf3r6tdis];
```

### SQL Server 中已经通过 Azure AD（MSI）创建的用户

## 查询数据库用户
```sql
-- 列出所有数据库用户
-- EXTERNAL_USER：通过 Azure AD/Managed Identity 创建的用户
-- EXTERNAL_GROUP：Azure AD 组
-- SQL_USER：普通 SQL 用户
SELECT name, type_desc
FROM sys.database_principals
WHERE type_desc IN ('SQL_USER', 'EXTERNAL_USER', 'EXTERNAL_GROUP');

```

## 查看角色成员
```sql
-- 查询数据库角色及成员
SELECT dp.name AS DatabaseRoleName, mp.name AS MemberName
FROM sys.database_role_members drm
JOIN sys.database_principals dp ON drm.role_principal_id = dp.principal_id
JOIN sys.database_principals mp ON drm.member_principal_id = mp.principal_id
WHERE mp.type_desc = 'EXTERNAL_USER';
```

## 查询 Azure AD 登录（在 master 数据库）
```sql
-- 列出 Azure AD 登录
SELECT name, type_desc
FROM sys.server_principals
WHERE type_desc = 'EXTERNAL_USER';
```