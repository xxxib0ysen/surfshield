import os

server_url = "http://localhost:8000"

# 获取网站访问控制规则列表
rule_sync_endpoint = "/website_control/listGrouped"

# 同步间隔10min
sync_interval_minutes = 10

# 日志路径
log_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "intercept.log")

