import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime, timezone,timedelta
# Step 1: 获取重定向后的URL
def get_redirected_url():
    login_url = "https://jicanvas.com/login/openid_connect"

    # 发送GET请求
    response = requests.get(login_url, allow_redirects=False)

    # 如果服务器返回302重定向，获取重定向的URL
    if response.status_code == 302:
        redirected_url = response.headers['Location']
        return redirected_url
    else:
        raise Exception(f"未预期的状态码: {response.status_code}")

# Step 2: 使用 selenium 打开重定向后的 URL
def open_login_page(redirected_url):
    # 设置 Chrome 浏览器选项
    chrome_options = Options()
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # 启动 Chrome 浏览器
    driver_path = './chromedriver.exe'  # 替换为你的 chromedriver 路径
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # 打开重定向后的 URL
        driver.get(redirected_url)
        time.sleep(3)  # 等待页面加载

        # 展示登录页面给用户进行手动操作
        input("请在浏览器中输入用户名、密码和验证码，登录后按回车继续...")

        # 获取登录后的 cookies
        cookies = driver.get_cookies()
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}

        return cookie_dict

    finally:
        driver.quit()

# 得到重定向到交大统一登录平台，step1
redirected_url = get_redirected_url()
# 使用selenium和chromedriver打开网页界面, step2
cookies = open_login_page(redirected_url)

# 获取信息的url
data_url1 = "https://jicanvas.com/api/v1/planner/items"

# 负载参数

# 添加user-agent防止网站反爬
dic = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
}

notes_announcement = []
notes_assignment = []
# 获取当前UTC时间
current_time = datetime.now(timezone.utc)

para = {
    "end_date":current_time.strftime("%Y-%m-%dT%H:%M:%SZ") ,
    "order": "desc"
}

resp = requests.get(url=data_url1, params=para, headers=dic,cookies=cookies)
for i1 in resp.json():
    if i1["plannable_type"]=="assignment":
        parsed_time = datetime.strptime(i1['plannable']["due_at"], "%Y-%m-%dT%H:%M:%SZ")
        time_in_east_8 = parsed_time + timedelta(hours=8)
        # 格式化为ISO 8601格式（东八区时间）
        formatted_time = time_in_east_8.strftime("%Y-%m-%dT%H:%M:%S+08:00")
        notes_assignment.append(formatted_time + "  " + i1['context_name'] + '  ' + i1['plannable']['title'] + '  ' + str(i1['submissions']["submitted"]) + "\n")
    if i1["plannable_type"]=="announcement":
        parsed_time = datetime.strptime(i1['plannable_date'], "%Y-%m-%dT%H:%M:%SZ")
        time_in_east_8 = parsed_time + timedelta(hours=8)
        # 格式化为ISO 8601格式（东八区时间）
        formatted_time = time_in_east_8.strftime("%Y-%m-%dT%H:%M:%S+08:00")
        notes_announcement.append(i1['plannable_date'] + "  " + i1['context_name'] + '  ' + i1['plannable']['title'] + "\n")
resp.close()


para2 = {
    "start_date":current_time.strftime("%Y-%m-%dT%H:%M:%SZ")
}
resp = requests.get(url=data_url1, params=para2, headers=dic,cookies=cookies)
for i1 in resp.json():
    if i1["plannable_type"]=="assignment":
        parsed_time = datetime.strptime(i1['plannable']["due_at"], "%Y-%m-%dT%H:%M:%SZ")
        time_in_east_8 = parsed_time + timedelta(hours=8)
        # 格式化为ISO 8601格式（东八区时间）
        formatted_time = time_in_east_8.strftime("%Y-%m-%dT%H:%M:%S+08:00")
        notes_assignment.append(formatted_time + "  " + i1['context_name'] + '  ' + i1['plannable']['title'] + '  ' + str(i1['submissions']["submitted"]) + "\n")
    if i1["plannable_type"]=="announcement":
        parsed_time = datetime.strptime(i1['plannable_date'], "%Y-%m-%dT%H:%M:%SZ")
        time_in_east_8 = parsed_time + timedelta(hours=8)
        # 格式化为ISO 8601格式（东八区时间）
        formatted_time = time_in_east_8.strftime("%Y-%m-%dT%H:%M:%S+08:00")
        notes_announcement.append(i1['plannable_date'] + "  " + i1['context_name'] + '  ' + i1['plannable']['title'] + "\n")
resp.close()

with open("announcement.txt","w",encoding="utf-8") as file:
    file.writelines(notes_announcement)
file.close()
with open("assignment.txt","w",encoding="utf-8") as file:
    file.writelines(notes_assignment)
file.close()
