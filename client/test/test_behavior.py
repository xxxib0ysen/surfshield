from client.agent.terminal.behavior import record_website_visit, record_search_behavior


def test_website_visit():
    print("测试网页访问记录：")
    test_url = "https://www.zhihu.com/question/614893968"
    record_website_visit(test_url)

def test_search_behavior():
    print("测试搜索行为记录：")
    test_search_url_1 = "https://www.baidu.com/s?wd=SQL注入原理"
    test_search_url_2 = "https://www.google.com/search?q=firewall绕过"
    test_search_url_3 = "https://cn.bing.com/search?q=网站监管系统"

    record_search_behavior(test_search_url_1)
    record_search_behavior(test_search_url_2)
    record_search_behavior(test_search_url_3)

if __name__ == '__main__':
    test_website_visit()
    test_search_behavior()
