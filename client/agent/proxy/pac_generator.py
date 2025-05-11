import os
from client.config.config import get_runtime_path
from client.config.logger import logger

def generate_pac_file(rule_domains, proxy_host="127.0.0.1", proxy_port=8888):
    """
    生成 PAC 文件：黑名单域名通过代理，其余直连
    支持通配符、主域名、类型校验、调试输出
    """
    try:
        print("[DEBUG] PAC 规则原始列表：", rule_domains)
        valid_domains = []

        for domain in rule_domains:
            if not isinstance(domain, str):
                logger.warning(f"[PAC] 非字符串规则跳过：{domain}")
                continue
            domain = domain.strip().lower()
            if not domain:
                continue
            valid_domains.append(domain)

        print("[DEBUG] 最终有效规则数：", len(valid_domains))

        pac_lines = ["function FindProxyForURL(url, host) {"]
        for domain in valid_domains:
            if domain.startswith("*."):
                pac_lines.append(f'  if (shExpMatch(host, "{domain}")) return "PROXY {proxy_host}:{proxy_port}";')
            elif domain.startswith(">"):
                pac_lines.append(f'  if (shExpMatch(host, "*{domain[1:]}")) return "PROXY {proxy_host}:{proxy_port}";')
            else:
                pac_lines.append(f'  if (shExpMatch(host, "{domain}")) return "PROXY {proxy_host}:{proxy_port}";')

        pac_lines.append('  return "DIRECT";')
        pac_lines.append("}")

        pac_path = get_runtime_path("proxy.pac")
        with open(pac_path, "w", encoding="utf-8") as f:
            f.write("\n".join(pac_lines))

        logger.info(f"[PAC] 已生成 PAC 文件：{pac_path}")

        # 打印最终 PAC 内容（调试用）
        with open(pac_path, "r", encoding="utf-8") as f:
            print("[DEBUG] 最终 PAC 内容：\n", f.read())

        return pac_path

    except Exception as e:
        logger.error(f"[PAC] 生成 PAC 文件失败：{e}", exc_info=True)
        return None
