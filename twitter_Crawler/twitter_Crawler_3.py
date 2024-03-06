import json
import time
import os
import shutil
try:
    from twitter_Crawler.download_pic import *
    from twitter_Crawler.json_process import *
except :
    from download_pic import *
    from json_process import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.common.exceptions import TimeoutException

# driver = None
# string_list = []
# url_list = []
# 
# def download_new(folder):
#     while len(driver.find_elements(By.CSS_SELECTOR, "div[data-testid='cellInnerDiv']")):
#         try:
#             for data in driver.find_elements(By.CSS_SELECTOR, "div[data-testid='cellInnerDiv']")[0:7]:
#                 for img in data.find_elements(By.TAG_NAME, "img"):
#                     src = img.get_attribute('src')
#                     if "profile_images" not in src and 'media' in src:
#                         # Get the rate image and remove dup
#                         if img.size['height'] == 466 and img.size['width'] == 516 and src[:src.find('?')] + "?format=png&name=large" not in string_list:
#                             string_list.append(src[:src.find('?')] + "?format=png&name=large")  # &name=large
#                             get_url_pic(string_list, len(string_list), folder)
#                             print(f'图片下载完成')
#                             return
#                 driver.execute_script(
#                     """
#                     var dataElements = document.querySelectorAll("div[data-testid='cellInnerDiv']");
#                     if(dataElements.length > 0) {
#                         dataElements[0].remove();
#                     }
#                     """)
#                 time.sleep(0.5)
#                 if len(driver.find_elements(By.CSS_SELECTOR, "div[data-testid='cellInnerDiv']")) == 0:
#                     time.sleep(2)
#         except BaseException as error:
#             print(str(error))
#             continue



def download_rate():
    # 初始化
    chrome_options = ChromeOptions()
    chrome_options.set_capability(
        "goog:loggingPrefs", {"performance": "ALL"}
    )
    chrome_options.add_argument("window-position=660,0")  # 控制浏览器相对于屏幕的启动位置,便于运行时查看终端输出调试。x,y(0,0)在最左侧,可以根据屏幕调节。
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(5)
    string_list = []
    url_list = []

    try:
        driver.get('https://twitter.com/i/flow/login')
    except TimeoutException:
        driver.execute_script('window.stop()')
    driver.set_page_load_timeout(60)

    # 设置cookie
    # print("设置cookie中.....")
    try:
        cookies = json.load(open("./twitter_Crawler/twitter_cookie.json", 'r'))
    except:
        cookies = json.load(open("./twitter_cookie.json", 'r'))
    for cookie in cookies:
        driver.add_cookie(cookie)

    # print("访问推特页面中.....")
    driver.get("https://twitter.com/tenohirasize")  # 此处修改爬取推文
    # print("准备获取图片和视频中.....")
    time.sleep(1)
    name = driver.find_elements(By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div[2]/div[1]/div/div[1]/div/div/span/span[1]')
    # folder = name[0].text.replace('/', '-')  # 防止斜杠视作创建多级文件夹
    folder = "images/rate_image"
    # 创建twitter名称文件夹
    if not os.path.exists(folder):
        os.makedirs(folder)
    elif len(os.listdir(folder)) > 0:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
            
    # download_new(folder)
    while len(driver.find_elements(By.CSS_SELECTOR, "div[data-testid='cellInnerDiv']")):
        try:
            for data in driver.find_elements(By.CSS_SELECTOR, "div[data-testid='cellInnerDiv']")[0:7]:
                for img in data.find_elements(By.TAG_NAME, "img"):
                    src = img.get_attribute('src')
                    if "profile_images" not in src and 'media' in src:
                        # Get the rate image and remove dup
                        if img.size['height'] == 466 and img.size['width'] == 516 and src[:src.find('?')] + "?format=png&name=large" not in string_list:
                            string_list.append(src[:src.find('?')] + "?format=png&name=large")  # &name=large
                            get_url_pic(string_list, len(string_list), folder)
                            return "./"+ folder +'/1_'+ src[:src.find('?')].split("/")[-1] + ".png"
                driver.execute_script(
                    """
                    var dataElements = document.querySelectorAll("div[data-testid='cellInnerDiv']");
                    if(dataElements.length > 0) {
                        dataElements[0].remove();
                    }
                    """)
                time.sleep(0.5)
                if len(driver.find_elements(By.CSS_SELECTOR, "div[data-testid='cellInnerDiv']")) == 0:
                    time.sleep(2)
        except BaseException as error:
            print(str(error))
            continue
