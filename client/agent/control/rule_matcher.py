import re
import tldextract

# 预编译后的正则规则列表（提高效率）
compiled_pattern_rules = []

# 主域名匹配规则集合
main_domain_rules = set()


# 设置规则列表（支持通配符与主域混合）
def set_rules(rule_list):
    global compiled_pattern_rules, main_domain_rules
    compiled_pattern_rules = []
    main_domain_rules = set()

    for rule in rule_list:
        rule = rule.strip().lower()
        if not rule:
            continue

        if "*" in rule or ">" in rule:
            # 通配符规则：转为正则并预编译
            regex = re.escape(rule)
            regex = regex.replace(r'\*', '.*').replace(r'\>', '.+')
            try:
                compiled = re.compile(f"^{regex}$")  # fullmatch 等价写法
                compiled_pattern_rules.append(compiled)
            except re.error:
                print(f"[RULE] 无效正则规则跳过: {rule}")
        else:
            # 主域规则直接存
            main_domain_rules.add(rule)


# 判断是否命中规则（域名）
def is_blocked(host):
    if not host:
        return False

    host = host.lower()

    # 正则规则匹配
    for pattern in compiled_pattern_rules:
        if pattern.fullmatch(host):
            return True

    # 主域名提取匹配
    ext = tldextract.extract(host)
    if not ext.domain or not ext.suffix:
        return False

    main_domain = f"{ext.domain}.{ext.suffix}"
    return main_domain in main_domain_rules
