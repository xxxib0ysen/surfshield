from datetime import datetime

import psutil
import time
import requests
import logging
from client.config import config
from client.config.logger import logger
from client.gui.context import main_window_instance, safe_update_module_status
from client.gui.intercept_info import update_rule_sync, record_process_block

full_url = config.server_url.rstrip("/") + config.process_sync_endpoint
scan_interval = config.process_scan_interval

logging.basicConfig(
    filename=config.process_log_path,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

last_process_rules = []

# 获取规则
def get_active_rules():
    global last_process_rules
    try:
        resp = requests.get(full_url, timeout=5)
        if resp.status_code == 200:
            json_data = resp.json()
            if isinstance(json_data, dict) and isinstance(json_data.get('data'), list):
                rules = [
                    r['process_name'].lower()
                    for r in json_data['data']
                    if r.get('status') == 1
                ]
                if set(rules) != set(last_process_rules):
                    last_process_rules = rules.copy()
                    sync_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    update_rule_sync(process_rule_count=len(rules), sync_time=sync_time)
                    logger.info(f"[进程规则] 已更新，共 {len(rules)} 条")
                else:
                    logger.info("[进程规则] 无变化，跳过更新时间")
            return rules
    except Exception as e:
        logger.warning(f"[进程规则获取失败] {e}")
    return []



def scan_and_kill(rules: list):
    logger.info(f"[进程拦截] 当前规则列表：{rules}")
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            pname = (proc.info['name'] or '').lower()
            pexe = (proc.info['exe'] or '').lower()

            for rule in rules:
                if rule in pname or rule in pexe:
                    logger.info(f"[拦截进程] 命中规则：{rule}，终止：{pname} (PID: {proc.pid})")
                    proc.terminate()

                    # 拦截记录 + UI 更新
                    record_process_block()
                    break
        except Exception as e:
            logger.warning(f"[进程终止异常] 无法终止进程 {proc.pid}: {e}")


def run_process_guard():
    logger.info("[进程拦截] 模块启动")
    try:
        safe_update_module_status("label_process_block", True, "进程拦截")
        while True:
            rules = get_active_rules()
            if rules:
                scan_and_kill(rules)
            time.sleep(scan_interval)
    except Exception as e:
        logger.error(f"[进程拦截异常] {e}")
        safe_update_module_status("label_process_block", False, "进程拦截")



