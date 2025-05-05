import os
import logging
from logging.handlers import TimedRotatingFileHandler

from client.config import config

log_base_filename = os.path.join(config.base_path, "surfshield")

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