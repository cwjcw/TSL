import requests
from bs4 import BeautifulSoup
import time

# 目标URL
url = "https://www.tesla.cn/inventory/used/ms?Province=CN&FleetSalesRegions=CN&arrangeby=plh&zip=&range=0"

# 请求头信息
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
}

# 使用Session保持会话
session = requests.Session()

# 发送HTTP GET请求，并禁用代理
try:
    response = session.get(url, headers=headers, proxies={"http": None, "https": None})
    response.raise_for_status()  # 如果响应状态码不是200，引发HTTPError异常
except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")
else:
    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找所有的车辆信息卡片
    cars = soup.find_all('article', class_='result card')
    
    for car in cars:
        # 获取车辆所在区域
        location = car.find('div', class_='tds-text_color--10').text.strip()
        
        # 获取价格信息
        price = car.find('span', class_='result-purchase-price tds-text--h4').text.strip()
        
        # 获取公里数信息
        mileage = car.find('div', text='公里里程表读数').find_next_sibling('div').text.strip()
        
        # 打印信息
        print(f"所在地: {location}")
        print(f"价格: {price}")
        print(f"公里数: {mileage}")
        print('-' * 20)
    
    # 添加延时，避免频繁请求
    time.sleep(1)
