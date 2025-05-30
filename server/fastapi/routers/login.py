from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from utils.auth import get_current_user, get_permission_codes
from utils.connect import create_connection
from utils.log.log import write_log
from utils.response import success_response
from utils.security import verify_password
from utils.jwt_token import create_access_token

router = APIRouter()

# 登录接口，返回 JWT token
@router.post("/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # 查询用户
        sql = "select admin_id, admin_name, password, role_id, status from sys_admin where admin_name = %s"
        cursor.execute(sql, (form_data.username,))
        user = cursor.fetchone()

        # 用户不存在
        if not user:
            raise HTTPException(status_code=400, detail="账号不存在")

        # 密码校验失败
        if not verify_password(form_data.password, user["password"]):
            raise HTTPException(status_code=400, detail="密码错误")

        # 账号未启用
        if user["status"] != 1:
            raise HTTPException(status_code=403, detail="账号未启用")

        # 角色未启用
        role_sql = "select status from sys_role where role_id = %s"
        cursor.execute(role_sql, (user["role_id"],))
        role = cursor.fetchone()

        if not role:
            raise HTTPException(status_code=400, detail="角色不存在")

        if role["status"] != 1:
            perms = []
        else:
            perms = get_permission_codes(user["role_id"])

        # 创建 token
        token_data = {
            "sub": user["admin_name"],
            "admin_id": user["admin_id"],
            "role_id": user["role_id"],
            "perms": perms
        }
        access_token = create_access_token(token_data)

        write_log(
            admin_id=user["admin_id"],
            ip_address=request.client.host,
            module="登录",
            action="login",
            detail={"description": f"{user['admin_name']} 登录成功"}
        )

        return {"access_token": access_token, "token_type": "bearer", "permissions":perms}

    except Exception as e:
        raise HTTPException(status_code=500, detail="登录失败：" + str(e))

# 获取当前登录用户信息
@router.get("/user/me")
def read_current_user(current_user: dict = Depends(get_current_user)):
    return {
        "admin_id": current_user["admin_id"],
        "admin_name": current_user["admin_name"],
        "role_id": current_user["role_id"],
        "status": current_user["status"],
        "permissions": current_user["permissions"],
        "is_default_pwd": current_user["is_default_pwd"]
    }

@router.get("/ping")
async def ping():
    return success_response(message="pong")