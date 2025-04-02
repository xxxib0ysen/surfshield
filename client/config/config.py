import os

server_url = "http://localhost:8000"

# 获取网站访问控制规则列表
rule_sync_endpoint = "/website_control/listGrouped"

# 获取进程控制规则列表
process_sync_endpoint = "/process/list"

# 同步间隔10min
sync_interval_minutes = 10

# 进程扫描周期（秒）
process_scan_interval = 1

# 日志路径
log_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "intercept.log")

# 进程拦截模块日志路径
process_log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "process_log.log")
