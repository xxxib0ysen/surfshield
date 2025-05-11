import json
from datetime import datetime

import requests
from PyQt5.QtCore import QTimer

from client.agent.proxy.pac_generator import generate_pac_file
from client.agent.proxy.proxy_config import set_pac_config, is_pac_config_correct
from client.config import config
from client.agent.control import rule_matcher
from client.gui.intercept_info import update_rule_sync, refresh_all_ui
from client.config.logger import logger
from client.config.config import get_runtime_path  # ✅ 用于拼接 rules.json

global_rules = []

# 保存规则到 JSON 文件（供 mitmproxy 使用）
def save_rules_to_file(rules):
    try:
        rule_path = get_runtime_path("rules.json")
        with open(rule_path, "w", encoding="utf-8") as f:
            json.dump(rules, f, ensure_ascii=False)
        logger.info(f"[规则同步] 已保存规则到 {rule_path}")
    except Exception as e:
        logger.error(f"[规则保存失败] {e}", exc_info=True)

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

            rule_matcher.set_rules(new_rules)
            save_rules_to_file(new_rules)  # ✅ 保存到 JSON

            pac_path = generate_pac_file(new_rules)
            if pac_path and not is_pac_config_correct(pac_path):
                logger.warning("[PAC] 系统未正确设置 AutoConfigURL，正在修复...")
                set_pac_config(pac_path)

            if set(new_rules) != set(global_rules):
                global_rules = new_rules
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