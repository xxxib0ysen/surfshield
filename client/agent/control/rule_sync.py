import json
from datetime import datetime

import requests
from PyQt5.QtCore import QTimer

from client.config import config
from client.agent.control import rule_matcher
from client.gui.intercept_info import update_rule_sync, refresh_all_ui
from client.config.logger import logger

global_rules = []

# 同步网站规则（启用状态的规则）
def sync_rules():
    from client.gui.context import main_window_instance
    global global_rules
    try:
        url = config.server_url + config.rule_sync_endpoint
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()

            new_rules = []

            for group in data.get("data", []):
                if group.get("type_status") == 1:
                    for rule in group.get("rules", []):
                        if rule.get("status") == 1:
                            new_rules.append(rule.get("website_url"))
            if set(new_rules) != set(global_rules):
                global_rules = new_rules
                rule_matcher.set_rules(global_rules)
                sync_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                update_rule_sync(web_rule_count=len(global_rules), sync_time=sync_time)
                logger.info(f"[规则同步] 网站规则已更新：{len(global_rules)} 条")
            else:
                logger.info("[规则同步] 网站规则无变化，跳过更新时间")

            if main_window_instance:
                QTimer.singleShot(0, lambda: refresh_all_ui(main_window_instance))

        else:
            logger.error(f"[规则同步] 请求失败，状态码：{response.status_code}")
    except Exception as e:
        logger.error(f"[规则同步异常] {e}")
