from threading import Thread
from client.agent.proxy.start_proxy import start_proxy
from client.gui.context import safe_update_module_status
from client.config.logger import logger

# 全局拦截状态
intercept_status = {"proxy": False}

# 更新网站拦截模块状态显示
def update_web_block_status():
    if intercept_status["proxy"]:
        safe_update_module_status("label_web_block", True, "网站拦截")
    else:
        safe_update_module_status("label_web_block", False, "网站拦截")

# 启动网站拦截线程（代理模式）
def start_network_intercept():
    def run():
        try:
            logger.info("[网站拦截] 启动 mitmproxy 代理模块中...")
            success = start_proxy()
            intercept_status["proxy"] = success
        except Exception as e:
            logger.error(f"[网站拦截异常] {e}", exc_info=True)
            intercept_status["proxy"] = False
        update_web_block_status()
    Thread(target=run, daemon=True).start()
