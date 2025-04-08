# 当前用户获取与验证
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
import jwt
from jwt import ExpiredSignatureError, DecodeError

from utils.connect import create_connection
from utils.jwt_token import secret_key, algorithm

# 提取 token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# 获取当前用户
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="身份认证失败",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 解码 token
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username = payload.get("sub")
        admin_id = payload.get("admin_id")
        role_id = payload.get("role_id")
        permissions = payload.get("perms", [])

        if not username or not admin_id or not role_id:
            raise credentials_exception

    except DecodeError:
        raise credentials_exception
    except ExpiredSignatureError:
        raise credentials_exception

    try:
        # 查询用户信息
        conn = create_connection()
        cursor = conn.cursor()
        sql = "select admin_id, admin_name, role_id, status from sys_admin where admin_name = %s"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            raise credentials_exception

        return {
            "admin_id": user["admin_id"],
            "admin_name": user["admin_name"],
            "role_id": user["role_id"],
            "status": user["status"],
            "permissions": permissions
        }

    except Exception:
        raise credentials_exception

# 根据角色id获取权限码
def get_permission_codes(role_id: int) -> list:
    conn = create_connection()
    cursor = conn.cursor()
    sql = """
        select p.perm_code
        from sys_role_permission rp
        join sys_permission p on rp.perm_id = p.perm_id
        where rp.role_id = %s
    """
    cursor.execute(sql, (role_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row['perm_code'] for row in rows]
