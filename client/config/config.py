import os

from redis.client import Redis

# server_url = "http://47.116.126.88"
server_url = "http://localhost:8000"

# Redis 连接信息
redis_client = Redis(
    host="localhost",
    port=6379,
    password=None,
    decode_responses=True
)

# 获取网站访问控制规则列表
rule_sync_endpoint = "/api/client/website_control/listGrouped"

# 获取进程控制规则列表
process_sync_endpoint = "/api/client/process/list"

# 终端注册接口地址
terminal_register_endpoint = "/api/client/register"

# 进程扫描周期（秒）
process_scan_interval = 600

# 日志路径
log_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "intercept.log")

# 进程拦截模块日志路径
process_log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "process_log.log")


