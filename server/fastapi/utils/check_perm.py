from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import DecodeError, ExpiredSignatureError
from utils.jwt_token import secret_key, algorithm

# 提取 token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# 权限校验依赖项
def check_permission(required_perm: str):
    # 验证器函数
    def verifier(token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])

            perms = payload.get("perms", [])
            # 检查是否包含指定权限
            if required_perm not in perms:
                raise HTTPException(status_code=403, detail="您暂无访问权限，请联系管理员授权")
        except (DecodeError, ExpiredSignatureError):
            # token 无效或已过期
            raise HTTPException(status_code=403, detail="权限校验失败")
    return verifier
