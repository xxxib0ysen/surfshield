# 统一保存全局 main_window_instance
main_window_instance = None
import time
from threading import Thread

def safe_update_module_status(label_attr: str, success: bool = True, name: str = "模块"):
    """
    :param label_attr: 主窗口中 QLabel 属性名
    :param success: 启动是否成功
    :param name: 显示名称
    """
    def try_update():
        for _ in range(30):  # 最多等待 3 秒
            from client.gui.context import main_window_instance
            if main_window_instance:
                label = getattr(main_window_instance, label_attr, None)
                if label:
                    if success:
                        label.setText(f"{name}已启动 ✅")
                    else:
                        label.setText(f"{name}启动失败 ❌")
                        label.setStyleSheet("color: red; font-weight: bold;")
                    return
            time.sleep(0.1)

    Thread(target=try_update, daemon=True).start()