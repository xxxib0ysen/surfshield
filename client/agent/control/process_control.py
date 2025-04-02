import psutil
import time
import requests
import logging
from client.config import config

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
                return [
                    r['process_name'].lower()
                    for r in json_data['data']
                    if r.get('status') == 1
                ]
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
                    break
        except Exception:
            continue

def run_process_guard():
    print(f"每 {scan_interval} 秒扫描进程")
    while True:
        rules = get_active_rules()
        if rules:
            print(f"获取到 {len(rules)} 条启用规则：{rules}")
            logging.info(f"获取到 {len(rules)} 条启用规则")
            scan_and_kill(rules)
        else:
            print("未获取到有效规则，跳过本轮扫描")
            logging.warning("未获取到有效规则")
        time.sleep(scan_interval)


