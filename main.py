# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime
import time
import pandas as pd
import git
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 获取根目录
root_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

# 将根目录添加到sys.path
sys.path.append(root_dir)

# 现在可以引用config.py
try:
    from config import DRIVER_PATH
except ImportError as e:
    print(f"Error importing DRIVER_PATH from config.py: {e}")
    sys.exit(1)

# 测试引用
print(DRIVER_PATH)  # 应输出在config.py中定义的路径

# 设置ChromeDriver路径
chromedriver_path = DRIVER_PATH  # 使用从config导入的路径

# 初始化Chrome浏览器
def open_browser():
    try:
        service = Service(chromedriver_path)
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")  # 启动浏览器最大化
        options.add_argument('--ignore-certificate-errors')  # 忽略证书错误
        # options.add_argument('--disable-gpu')
        # options.add_argument('headless' )
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"Error initializing ChromeDriver: {e}")
        sys.exit(1)
    return driver

# 打开指定链接
def open_url(driver, url):    
    try:
        driver.get(url)
    except Exception as e:
        print(f"Error navigating to URL: {e}")
        driver.quit()
        sys.exit(1)

    # 等待页面加载
    time.sleep(5)  # 可以根据实际情况调整等待时间

# 获取数据并保存到CSV
def get_data(driver):
    data = []

    # 查找所有包含class="result card"的标签
    elements = driver.find_elements(By.CSS_SELECTOR, '.result.card')
    for element in elements:
        try:
            data_id = element.get_attribute('data-id')
            vin = data_id.split('-')[0]  # 提取第一个 '-' 之前的内容
            model = element.find_element(By.CSS_SELECTOR, '.tds-text--h4').text
            series = element.find_element(By.CSS_SELECTOR, '.tds-text_color--10').text
            
            # 使用显式等待确保元素加载
            mileage_element = WebDriverWait(element, 10).until(
                EC.presence_of_element_located((By.XPATH, ".//span[contains(text(),'公里里程')]"))
            )
            mileage_text = mileage_element.text
            mileage = ''.join(filter(str.isdigit, mileage_text))  # 只保留数字
            
            city = element.find_elements(By.XPATH, ".//div")[3].text  # 修改索引以匹配正确的div
            price = element.find_element(By.CSS_SELECTOR, '.result-purchase-price.tds-text--h4').text
            price = ''.join(filter(str.isdigit, price))  # 只保留数字

            # 使用显式等待来确保 .result-highlights 元素加载
            highlights = WebDriverWait(element, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.result-highlights'))
            )
            highlights_lis = highlights.find_elements(By.TAG_NAME, 'li')

            endurance = highlights_lis[0].find_element(By.CSS_SELECTOR, '.tds-text--h4').text
            speed = highlights_lis[1].find_element(By.CSS_SELECTOR, '.tds-text--h4').text
            acceleration = highlights_lis[2].find_element(By.CSS_SELECTOR, '.tds-text--h4').text

            data.append({
                "日期": datetime.today().strftime('%Y-%m-%d'),
                "车架号": vin,
                "型号": model,
                "系列": series,
                "公里数": mileage,
                "城市": city,
                "价格": price,
                "续航": endurance,
                "时速": speed,
                "百公里加速": acceleration
            })
        except Exception as e:
            print(f"Error extracting data from element: {e}")

    return data

# 保存数据到CSV
def save_data_to_csv(data, filename='result.csv'):
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        try:
            existing_data = pd.read_csv(filename)
            new_data = pd.DataFrame(data)
            combined_data = pd.concat([existing_data, new_data], ignore_index=True)
            combined_data.to_csv(filename, index=False)
        except pd.errors.EmptyDataError:
            print(f"{filename} is empty. Creating a new file.")
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
    else:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
    print(f"Data has been saved to {filename}")

# 推送数据到Git
def push_to_git(repo_path, filename):
    try:
        repo = git.Repo(repo_path)
        repo.index.add([filename])
        repo.index.commit(f"Update data on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        origin = repo.remote(name='origin')
        origin.push()
        print("Data has been pushed to Git.")
    except Exception as e:
        print(f"Error pushing to Git: {e}")

# 主函数
def main():
    tsl_url = "https://www.tesla.cn/inventory/used"
    tsl_car = ['ms','m3','mx','my']  # 可以扩展这个列表以包含更多车型
    all_data = []

    driver = open_browser()
    for car in tsl_car:
        open_url(driver, f"{tsl_url}/{car}")
        data = get_data(driver)
        all_data.extend(data)

    driver.quit()
    filename = 'result.csv'
    save_data_to_csv(all_data, filename)
    
    # 推送到Git
    repo_path = os.path.dirname(os.path.abspath(__file__))  # 假设Git仓库在当前目录
    push_to_git(repo_path, filename)

if __name__ == "__main__":
    main()
