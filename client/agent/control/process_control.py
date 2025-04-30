from datetime import datetime

import psutil
import time
import requests
import logging
from client.config import config
from client.config.logger import logger
from client.gui.context import main_window_instance, safe_update_module_status
from client.gui.intercept_info import record_process_block, update_rule_info

full_rul = config.server_url.rstrip("/") + config.process_sync_endpoint
scan_interval = config.process_scan_interval

logging.basicConfig(
    filename=config.process_log_path,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 获取规则
def get_active_rules():
    try:
        resp = requests.get(full_rul, timeout=5)
        if resp.status_code == 200:
            json_data = resp.json()
            if isinstance(json_data, dict) and isinstance(json_data.get('data'), list):
                rules = [
                    r['process_name'].lower()
                    for r in json_data['data']
                    if r.get('status') == 1
                ]
                # 更新界面
                if main_window_instance:
                    update_rule_info(main_window_instance, process_rule_count=len(rules))
                return rules
    except Exception as e:
        logging.warning(f"[规则获取失败] {str(e)}")
    return []


def scan_and_kill(rules: list):
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            pname = (proc.info['name'] or '').lower()
            pexe = (proc.info['exe'] or '').lower()

            for rule in rules:
                if rule in pname or rule in pexe:
                    logging.info(f"[拦截] 命中规则：{rule}，终止进程：{pname} (PID: {proc.pid})")
                    proc.terminate()

                    # 更新界面拦截次数
                    try:
                        if main_window_instance:
                            record_process_block(main_window_instance)
                    except Exception as e:
                        print(f"[进程拦截统计失败] {e}")

                    break
        except Exception:
            continue

def run_process_guard():
    logger.info("[进程拦截] 启动中...")
    try:
        safe_update_module_status("label_process_block", True, "进程拦截")
        while True:
            rules = get_active_rules()
            if rules:
                logging.info(f"获取到 {len(rules)} 条启用规则：{rules}")
                scan_and_kill(rules)
            else:
                logging.warning("未获取到有效规则")
            time.sleep(scan_interval)
    except Exception as e:
        logging.error(f"[进程拦截异常] {e}")
        safe_update_module_status("label_process_block", False, "进程拦截")



