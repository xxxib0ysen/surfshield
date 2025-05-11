import os
import sys
from redis.client import Redis

version = "v0.0.9"

server_url = "http://47.116.126.88"
# server_url = "http://localhost:8000"

# 判断是否为打包后的运行环境
if getattr(sys, 'frozen', False):
    # 打包运行
    base_path = os.path.join(os.environ.get("ProgramData", "C:\\ProgramData"), "SurfShield")
else:
    # 本地运行
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs"))

os.makedirs(base_path, exist_ok=True)

# Redis 连接
redis_client = Redis(
    host="47.116.126.88",
    port=6379,
    password=None,
    decode_responses=True
)

rule_sync_endpoint = "/api/client/website_control/listGrouped"
process_sync_endpoint = "/api/client/process/list"
terminal_register_endpoint = "/api/client/register"

# 扫描周期（秒）
process_scan_interval = 5

# 路径配置
log_file_path = os.path.join(base_path, "intercept.log")
process_log_path = os.path.join(base_path, "process_log.log")
intercept_info_path = os.path.join(base_path, "intercept_info.json")
