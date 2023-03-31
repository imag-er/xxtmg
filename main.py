from time import sleep
import sys
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
import os


def driver_init() -> None:
    try:
        options = webdriver.EdgeOptions()

        UA = 'user-agent=Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.29 Safari/525.13'
        options.add_argument(UA)
        options.add_experimental_option('detach', True)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        edge_service = Service(r"msedgedriver.exe")
        global driver
        driver = webdriver.Edge(service=edge_service, options=options)

        os.system('chcp 65001')
        # 找不到元素就等着 timeout = 5
        driver.implicitly_wait(10)

    except:
        print("On driver_init error")
        sys.exit()

    print(f"成功启动Edge驱动\n\ntimeout = 10s\n\nUser Agent:\n{UA}\n\n")


def login() -> None:
    driver.get("http://i.mooc.chaoxing.com/")

    account_box = driver.find_element(By.ID, 'phone')

    account = 0
    password = 0

    with open(r'aandp.txt', 'r+', encoding='utf-8') as pf:
        account, password = pf.readlines()

    print(f'读取账户信息:\n账号:{account}密码:{password}\n\n')

    account_box.click()
    account_box.send_keys(account)
    print(f'填入账号:{account}', end='')

    password_box = driver.find_element(By.ID, 'pwd')
    password_box.click()
    password_box.send_keys(password)
    print(f'填入密码:{password}', end='')

    driver.execute_script('loginByPhoneAndPwd();')

    print('登录成功\n')


def choose_course() -> None:

    # 傻逼学习通开发者套了一层iframe 害老子debug半天不知道为啥找不到dom
    driver.switch_to.frame('frame_content')
    print('current url:{}'.format(driver.current_url))

    # 此处获取的是<a>
    # 他的儿子是<span>course name</span>
    classBtn = driver.find_elements(By.CSS_SELECTOR, 'a.color1')
    if len(classBtn) == 0:
        print("无法找到<a>标签")
        return
    i = 0
    course_name_list = []
    for btn in classBtn:
        course_name_list.append(
            btn.find_element(By.CSS_SELECTOR, 'span')
            .get_property('title')
        )
        print(f'{i} : {course_name_list[i]}')
        i += 1

    course_choose = int(input('请输入课程序号：'))
    global course_name
    if course_choose > -1 and course_choose < len(classBtn):
        course_name = course_name_list[course_choose]
        print(f"已找到课程\'{course_choose}:{course_name}\'对应的<a>标签")

        class_choose_btn = classBtn[course_choose]
        driver.execute_script('arguments[0].click();', class_choose_btn)

    driver.switch_to.default_content()


def choose_stage() -> None:
    # 先选择课程
    choose_course()

    # 切换到章节列表
    hWindows = driver.window_handles
    driver.switch_to.window(hWindows[1])

    # 点击左侧章节按钮
    driver.find_element(By.XPATH, '//i[@class=\'zj\']/..').click()

    # 点章节按钮会产生好多iframe sbxxt相当离谱
    driver.switch_to.frame(
        driver.find_elements(By.CSS_SELECTOR, 'iframe#frame_content-zj')[-1]
    )

    # 获取章节<li>标签对象
    stage_list = \
        driver.find_elements(
            By.CSS_SELECTOR,
            'div.chapter_unit > div.catalog_level > ul > li'
        )

    if len(stage_list) == 0:
        print('无法找到课程<li>')
        return
    print(f'已找到课程\'{course_name}\'对应的<li>列表')

    # 获取章节信息并向用户展示
    index = 0
    for lis in stage_list:
        # 向下滑动直到元素可见
        driver.execute_script("arguments[0].scrollIntoView(true);", lis)

        course_title = lis.find_element(
            By.CSS_SELECTOR, 'div.chapter_item').get_attribute('title')

        status = lis.find_element(
            By.CSS_SELECTOR, 'span.bntHoverTips').get_attribute('textContent')

        print(f'{index} : 当前章节：{course_title} 状态：{status}')
        index += 1

    index = int(input('请输入开始章节序号'))
    stage_list[index].click()


    while True:
        index += 1
        onplay()
        inner_stage_list = driver.find_elements(
            By.CSS_SELECTOR, "span.posCatalog_name")
        driver.execute_script(
            "arguments[0].scrollIntoView(true);", inner_stage_list[index])
        inner_stage_list[index].click()


def onplay() -> None:

    # 切换到SB iframe
    driver.switch_to.frame(
        driver.find_element(
            By.CSS_SELECTOR,
            'iframe#iframe'
        )
    )
    driver.switch_to.frame(
        driver.find_element(
            By.CSS_SELECTOR,
            'iframe.ans-attach-online.ans-insertvideo-online'
        )
    )

    # 获取中心播放按钮
    play_btn = driver.find_element(
        By.CSS_SELECTOR,
        'button.vjs-big-play-button'
    ).click()
    print('开始播放')

    # 获取小箭头
    pause_btn = driver.find_element(
        By.CSS_SELECTOR,
        '.vjs-control-bar > button'
    )
    print('播放')

    # 点击之后开始等待课程播放完毕

    # 获取时间<span>
    currenttime_span = driver.find_element(
        By.CLASS_NAME, 'vjs-current-time-display')
    durationtime_span = driver.find_element(
        By.CLASS_NAME, 'vjs-duration-display')

    # 获取时间str
    ctime_str = currenttime_span.get_attribute('textContent')

    # 延迟获取总时长 因为需要加载时间
    dtime_str = '0:00'
    while dtime_str == '0:00':
        dtime_str = durationtime_span.get_attribute('textContent')
        sleep(0.5)

    # 把时间str转为int
    ctime = int(ctime_str[:-3]) * 60 + int(ctime_str[-2:])
    dtime = int(dtime_str[:-3]) * 60 + int(dtime_str[-2:])

    vdo = driver.find_element(By.CSS_SELECTOR, 'video#video_html5_api')

    driver.execute_script('arguments[0].pause = false;', vdo)
    driver.execute_script('arguments[0].playbackRate = 2;', vdo)

    # js_str = \
    '''
    const frameObj = $("iframe").eq(0).contents().find("iframe.ans-insertvideo-online");
    var v = frameObj.contents().eq(0).find("video#video_html5_api").get(0);
    v.pause = false; v.playbackRate = 2;
    '''
    while ctime != dtime:
        print(
            '------已观看 {} // {} 当前进度{:.2f}%------'.format(
                ctime, dtime,
                100 * ctime / dtime
            ),
            end='\r'
        )

        ctime_str = currenttime_span.get_attribute('textContent')
        dtime_str = durationtime_span.get_attribute('textContent')

        ctime = int(ctime_str[:-3]) * 60 + int(ctime_str[-2:])
        dtime = int(dtime_str[:-3]) * 60 + int(dtime_str[-2:])

        sleep(1)
    driver.switch_to.default_content()

    return


def main() -> None:
    driver_init()
    login()
    choose_stage()


if __name__ == '__main__':
    main()
