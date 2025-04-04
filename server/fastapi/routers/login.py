# 登录接口
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from utils.auth import get_current_user
from utils.connect import create_connection
from utils.security import verify_password
from utils.jwt_token import create_access_token
from datetime import timedelta

router = APIRouter()

# 登录接口，返回 JWT token
@router.post("/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # 查询用户
        sql = "select admin_id, admin_name, password, role_id, status from sys_admin where admin_name = %s"
        cursor.execute(sql, (form_data.username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        # 用户不存在
        if not user:
            raise HTTPException(status_code=400, detail="账号不存在")

        # 密码校验失败
        if not verify_password(form_data.password, user["password"]):
            raise HTTPException(status_code=400, detail="密码错误")

        # 账号未启用
        if user["status"] != 1:
            raise HTTPException(status_code=403, detail="账号未启用")

        # 创建 token
        token_data = {
            "sub": user["admin_name"],
            "admin_id": user["admin_id"],
            "role_id": user["role_id"]
        }
        access_token = create_access_token(token_data, timedelta(minutes=30))

        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(status_code=500, detail="登录失败：" + str(e))

# 获取当前登录用户信息
@router.get("/user/me")
def read_current_user(current_user: dict = Depends(get_current_user)):
    return {
        "admin_id": current_user["admin_id"],
        "admin_name": current_user["admin_name"],
        "role_id": current_user["role_id"],
        "status": current_user["status"]
    }