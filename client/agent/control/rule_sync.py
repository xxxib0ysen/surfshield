import json
import requests
from client.config import config
from client.agent.control import rule_matcher
from client.logs.logger import logger

global_rules = []

# 同步规则数据（仅启用类型与规则）
def sync_rules():
    global global_rules
    try:
        url = config.server_url + config.rule_sync_endpoint
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            rules = []
            for group in data.get("data", []):
                if group.get("type_status") == 1:
                    for rule in group.get("rules", []):
                        if rule.get("status") == 1:
                            rules.append(rule.get("website_url"))
            global_rules = rules
            rule_matcher.set_rules(global_rules)   # 匹配规则
            logger.info(f"[SYNC] 同步成功，已加载规则 {len(global_rules)} 条")
        else:
            logger.error(f"[SYNC] 请求失败，状态码：{response.status_code}")
    except Exception as e:
        logger.error(f"[SYNC] 同步异常：{e}")