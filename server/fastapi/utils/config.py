import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Config:
    # 数据库
    MYSQL_HOST: str = os.getenv("MYSQL_HOST")
    MYSQL_USER: str = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB: str = os.getenv("MYSQL_DB")

    # JWT 配置
    secret_key = "surfshield-jwt"
    token_expiration = 60 * 60  * 12
    token_fresh_expiration = 60 * 60 * 24