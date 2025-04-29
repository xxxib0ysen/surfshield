import os
import logging
from logging.handlers import TimedRotatingFileHandler

# 日志目录
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)

# 日志文件基础名
log_base_filename = os.path.join(log_dir, "surfshield")

# 创建日志器
logger = logging.getLogger("client_logger")
logger.setLevel(logging.DEBUG)

# 创建按天轮转的处理器
handler = TimedRotatingFileHandler(
    filename=log_base_filename,
    when="midnight",
    interval=1,
    backupCount=3,
    encoding="utf-8",
    utc=False
)

# 日志输出格式
formatter = logging.Formatter(
    fmt='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)

# 加入日志器
logger.addHandler(handler)