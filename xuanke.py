import selenium
import time
import pyautogui
from selenium import webdriver

def get_driver(is_headless=0, is_eager=0, load_images=1):
    options = webdriver.ChromeOptions()
    prefs={
        'profile.default_content_setting_values': {
            'images': load_images,
            #'video':2
        }
    }
    #options.add_argument("--user-data-dir="+r"C:/Users/xgs0117/AppData/Local/Google/Chrome/User Data/Default")
    options.add_experimental_option('prefs', prefs)
    if is_eager:
        #desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略
        #desired_capabilities["pageLoadStrategy"] = "eager"
        pass
    else:
        pass
    driver = webdriver.Chrome(executable_path=r"H:\Github\Crawler-blackout\chromedriver.exe",chrome_options=options)
    return driver

def switch_window(driver, now):
    all_handles = driver.window_handles                #得到当前开启的所有窗口的句柄
    for handle in all_handles:
        if handle != now:                              #获取到与当前窗口不一样的窗口
            driver.switch_to_window(handle)            #切换


driver = get_driver(0, 0, 0)
driver.get("http://classes.tju.edu.cn/eams/")
x = input("sa ")
switch_window(driver, driver.current_window_handle)
course_id_list = ['05442',"05443"]
for i in range(100000):
    for course_id in course_id_list:
        try:
            a = driver.find_element_by_xpath('/html/body/div[9]/div[3]/div[1]/table[1]/thead/tr[1]/th[2]/div/input')
            a.clear()
            a.send_keys(course_id)
            driver.find_element_by_xpath('//*[@id="electableLessonList_filter_submit"]').click()
            time.sleep(1)
            if driver.find_element_by_class_name("stdCount").text != "0":
                driver.find_element_by_xpath("//*[text()='选课']").click()
                time.sleep(1)
                pyautogui.typewrite('\n')
                time.sleep(1)
            else:
                time.sleep(1)
                pyautogui.typewrite('\n')
                continue
        except Exception as e:
            print(e)
