# JWT 创建与解析

from datetime import datetime, timedelta, timezone

import jwt

# 密钥配置
secret_key = "f2d2f32219afcfeece87ea66461e22c2d1432eb2f2f3a76692a4b1e0e47d75d4"
algorithm = "HS256"
access_token_expire_minutes= 60*2

# 生成 access token
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=access_token_expire_minutes))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt
