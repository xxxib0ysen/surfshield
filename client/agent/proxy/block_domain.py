import sys
import os
import json
from mitmproxy import http

# 添加 client 根路径
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from client.agent.control.log import log_block
from client.agent.control import rule_matcher
from client.config.config import get_runtime_path
from client.config.logger import logger

# ✅ 加载规则文件（由主程序写入）
try:
    rule_path = get_runtime_path("rules.json")
    if os.path.exists(rule_path):
        with open(rule_path, "r", encoding="utf-8") as f:
            rules = json.load(f)
            rule_matcher.set_rules(rules)
            logger.info(f"[MITM] 已加载规则文件，共 {len(rules)} 条")
    else:
        logger.warning(f"[MITM] 规则文件不存在：{rule_path}")
except Exception as e:
    logger.error(f"[MITM] 规则文件加载失败: {e}", exc_info=True)

# ✅ 拦截逻辑
class DomainBlocker:
    def __init__(self):
        logger.info("[MITM] 拦截模块已加载")

    def request(self, flow: http.HTTPFlow):
        try:
            host = flow.request.host.lower()
            logger.info(f"[MITM] 收到请求：{host}")

            matched = rule_matcher.is_blocked(host)
            logger.info(f"[MITM] 匹配结果：{matched}")

            if matched:
                logger.info(f"[MITM]  拦截：{host}")
                log_block(flow.request.scheme, host)
                flow.response = http.Response.make(
                    403, b"Blocked by admin !!!", {"Content-Type": "text/plain"}
                )
            else:
                logger.info(f"[MITM] 放行：{host}")
        except Exception as e:
            logger.error(f"[MITM] 拦截处理异常：{e}", exc_info=True)

addons = [DomainBlocker()]