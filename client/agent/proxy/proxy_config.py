import winreg
from client.config.logger import logger

def set_pac_config(pac_file_path):
    """
    设置系统使用 PAC 自动代理
    """
    try:
        pac_url = "file:///" + pac_file_path.replace("\\", "/")
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "AutoConfigURL", 0, winreg.REG_SZ, pac_url)
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        logger.info(f"[PAC] 设置系统 AutoConfigURL 成功：{pac_url}")
    except Exception as e:
        logger.error(f"[PAC] 设置 AutoConfigURL 失败: {e}", exc_info=True)

def clear_pac_config():
    """
    清除系统 PAC 设置
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
            0, winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, "AutoConfigURL")
        winreg.CloseKey(key)
        logger.info("[PAC] 系统 AutoConfigURL 已清除")
    except FileNotFoundError:
        pass
    except Exception as e:
        logger.error(f"[PAC] 清除 AutoConfigURL 失败: {e}", exc_info=True)

def is_pac_config_correct(pac_file_path):
    """
    检查注册表中 AutoConfigURL 是否等于我们期望的 PAC 文件路径
    """
    try:
        expected = "file:///" + pac_file_path.replace("\\", "/")
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
            0, winreg.KEY_READ
        )
        value, regtype = winreg.QueryValueEx(key, "AutoConfigURL")
        winreg.CloseKey(key)
        return value.strip().lower() == expected.strip().lower()
    except FileNotFoundError:
        return False
    except Exception as e:
        logger.warning(f"[PAC] 检查 AutoConfigURL 失败: {e}")
        return False
