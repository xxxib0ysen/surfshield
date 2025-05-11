import re
import tldextract
from client.config.logger import logger

compiled_pattern_rules = []
main_domain_rules = set()

def set_rules(rule_list):
    global compiled_pattern_rules, main_domain_rules
    compiled_pattern_rules = []
    main_domain_rules = set()

    for rule in rule_list:
        rule = rule.strip().lower()
        if not rule:
            continue

        if "*" in rule or ">" in rule:
            regex = re.escape(rule)
            regex = regex.replace(r'\*', '.*').replace(r'\>', '.+')
            try:
                compiled_pattern_rules.append(re.compile(f"^{regex}$"))
            except re.error:
                logger.error(f"[RULE] 无效正则规则跳过: {rule}")
        else:
            main_domain_rules.add(rule)

def is_blocked(host):
    if not host:
        return False

    host = host.lower()

    # 正则规则匹配
    for pattern in compiled_pattern_rules:
        if pattern.fullmatch(host):
            return True

    # 明确域名本体匹配（如 example.com）
    if host in main_domain_rules:
        return True

    # 主域提取匹配（如 x.y.example.com → example.com）
    ext = tldextract.extract(host)
    if ext.domain and ext.suffix:
        main_domain = f"{ext.domain}.{ext.suffix}"
        if main_domain in main_domain_rules:
            return True

    return False
