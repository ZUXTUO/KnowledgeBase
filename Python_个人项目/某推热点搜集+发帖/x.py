import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, ElementClickInterceptedException
import shutil # 导入 shutil 模块用于目录清理
import re # 导入 re 模块用于正则表达式

# 配置选项
# 为了避免 'session not created' 错误，我们使用一个基于时间戳的唯一用户数据目录。
# 这样每次运行脚本时都会创建一个新的临时浏览器配置文件。
# 如果你需要保持登录状态或特定设置，可以手动指定一个固定的目录，
# 但要确保在运行脚本前没有其他 Chrome 进程在使用该目录。
USER_DATA_BASE_DIR = '~/.config/google-chrome/Default'
# 根据用户提供的日志，将 URL 更新为实际访问的 x.com 域名，而不是 ssa.com
TRENDING_URL = 'https://x.com/explore/tabs/trending'
COMPOSE_URL = 'https://x.com/compose/post'
INTERVAL_MINUTES = 1

def setup_driver():
    """
    配置并启动一个带有用户数据的Chrome浏览器实例。
    使用一个唯一的临时目录来避免会话创建问题。
    """
    options = webdriver.ChromeOptions()
    
    # 创建一个基于当前时间戳的唯一用户数据目录
    # 注意：确保这个目录是临时的，或者在每次运行前手动清理，以避免权限问题或冲突。
    # 这里我们将其定义在函数内部，并在 finally 块中尝试清理。
    global unique_user_data_dir # 声明为全局变量以便在 finally 块中访问
    unique_user_data_dir = os.path.join(USER_DATA_BASE_DIR, f'profile_{int(time.time())}')
    os.makedirs(unique_user_data_dir, exist_ok=True) # 确保目录存在
    options.add_argument(f"user-data-dir={unique_user_data_dir}")
    
    options.add_argument("--disable-notifications") # 禁用浏览器通知
    options.add_argument("--lang=en-US") # 设置浏览器语言为美式英语
    options.add_argument("--start-maximized") # 启动时最大化浏览器窗口，有时有助于元素可见性
    
    # 尝试创建 WebDriver 实例
    try:
        driver = webdriver.Chrome(options=options)
        print(f"Chrome 浏览器已成功启动，使用用户数据目录: {unique_user_data_dir}")
        return driver
    except WebDriverException as e:
        print(f"启动Chrome浏览器失败: {e}")
        print("请检查:")
        print("1. ChromeDriver 是否已安装且版本与您的Chrome浏览器兼容。")
        print("2. ChromeDriver 的路径是否已添加到系统 PATH 环境变量中。")
        print("3. 是否有其他Chrome实例正在使用相同的数据目录 (如果禁用了临时目录)。")
        exit() # 终止程序

def get_trending_tags(driver):
    """
    获取当前趋势标签。
    使用 WebDriverWait 来等待页面加载和特定元素出现，提高稳定性。
    针对SSA平台（类似Twitter/X）的结构，尝试更可靠的定位器。
    """
    print(f"尝试导航到趋势页面: {TRENDING_URL}")
    driver.get(TRENDING_URL)
    
    try:
        # 显式等待直到页面标题包含特定文本，或直到页面加载完成的某个指示器出现
        WebDriverWait(driver, 20).until(
            EC.url_contains("explore/tabs/trending") # 确保URL正确加载
        )
        print("已成功导航到趋势页面。")

        # 等待趋势模块加载。这里根据SSA（假设是类似Twitter的平台）的结构，
        # 等待带有 'aria-labelledby^="accessible-list"' 的 section 元素出现。
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'section[aria-labelledby^="accessible-list"]'))
        )
        print("趋势模块已加载。")
        
        # 尝试使用更通用的 CSS 选择器。在类似 Twitter/X 的平台上，趋势标签通常是可点击的链接 (<a> 标签)。
        # 我们寻找 data-testid="trend" 容器内的任何 <a> 标签，然后过滤其文本是否以 '#' 开头。
        # 如果这种方式仍旧失败，可以尝试使用 XPath 匹配文本内容。

        trending_tags = []
        try:
            # 尝试查找 data-testid="trend" 容器内的所有 <a> 标签
            trends_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="trend"] a')
            if not trends_elements: # 如果没有找到 <a> 标签，尝试查找所有 span 标签
                trends_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="trend"] span')
                print("未找到趋势链接，尝试查找趋势文本（span 标签）。")

            for element in trends_elements:
                tag_text = element.text.strip()
                if tag_text.startswith('#'):
                    # 过滤非标准或过长的标签，只保留常用语言字符 (字母、数字、下划线、日文假名/汉字)
                    # 避免类似 'б' 的异常字符导致显示问题
                    # \u3040-\u30ff (Hiragana/Katakana), \u4e00-\u9fff (Common CJK Unified Ideographs)
                    # re.sub 将不符合要求的字符替换为空
                    filtered_tag = re.sub(r'[^\w#\u3040-\u30ff\u4e00-\u9fff]+', '', tag_text)
                    
                    # 确保过滤后标签仍然以 # 开头且有内容，且长度合理（避免过长标签）
                    if filtered_tag.startswith('#') and len(filtered_tag) > 1 and len(filtered_tag) < 100: # 限制标签长度在100字符以内
                        trending_tags.append(filtered_tag)
                    else:
                        print(f"过滤掉异常或过长标签: 原始: '{tag_text}' -> 过滤后: '{filtered_tag}'")
            
            if not trending_tags: # 如果通过 CSS 仍未找到，尝试使用 XPath
                print("通过 CSS 选择器未能找到趋势标签，尝试使用 XPath。")
                # XPath 寻找任何文本以 '#' 开头的元素，位于 data-testid="trend" 内部
                xpath_trends = driver.find_elements(By.XPATH, '//div[@data-testid="trend"]//*[starts-with(normalize-space(text()), "#")]')
                for tag in xpath_trends:
                    tag_text = tag.text.strip()
                    filtered_tag = re.sub(r'[^\w#\u3040-\u30ff\u4e00-\u9fff]+', '', tag_text)
                    if filtered_tag.startswith('#') and len(filtered_tag) > 1 and len(filtered_tag) < 100:
                        trending_tags.append(filtered_tag)
                    else:
                        print(f"过滤掉异常或过长标签 (XPath): 原始: '{tag_text}' -> 过滤后: '{filtered_tag}'")

        except NoSuchElementException:
            print("未能通过 CSS 或 XPath 定位到趋势标签元素。")
            
        return trending_tags
    
    except TimeoutException:
        print("获取趋势标签超时，请检查网络连接或页面结构是否发生变化。")
        # 可以选择截图或保存页面源码以便调试
        # driver.save_screenshot("trending_page_timeout.png")
        # with open("trending_page_source.html", "w", encoding="utf-8") as f:
        #    f.write(driver.page_source)
        return []
    except Exception as e:
        print(f"获取趋势标签时发生未知错误: {e}")
        return []

def post_tweet(driver, tags):
    """
    发送带趋势标签的推文。
    同样使用 WebDriverWait 来确保输入框和发帖按钮可用。
    """
    if not tags:
        print("未获取到趋势标签，跳过发布推文。")
        return
    
    print(f"尝试导航到发布页面: {COMPOSE_URL}")
    driver.get(COMPOSE_URL)
    
    try:
        # --- 优化推文编辑器的定位：直接使用 'contenteditable="true"' ---
        editor = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[contenteditable="true"]'))
        )
        print("通过 CSS 选择器找到推文编辑器 (contenteditable='true')。")

        print("推文编辑器已加载。")
        
        # 随机选择一个趋势标签
        selected_tag = random.choice(tags)
        # 组合推文内容
        tweet_text = f"参与当前热点讨论 {selected_tag} 大家有什么看法？\n\n#热点话题 #趋势追踪"
        
        # 输入内容到文本框
        editor.send_keys(tweet_text)
        print(f"已输入推文内容: {tweet_text}")
        
        # --- 优化发帖按钮的定位和点击策略：直接使用 XPath 并强制点击 ---
        post_button = None
        try:
            # 直接使用 XPath 查找发帖按钮，并等待其可点击
            # 增加超时时间以提高稳定性，包含 data-testid="tweetButton"
            post_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="tweetButton"] | //button[contains(., "Post")] | //button[contains(., "发帖")] | //div[contains(@role, "button") and (contains(., "Post") or contains(., "发帖"))]'))
            )
            print(f"发帖按钮已通过 XPath 找到并可点击。")
            
            # 尝试滚动到视图内，确保按钮完全可见，并给时间让可能的覆盖元素消失
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_button)
            time.sleep(1) 

            # 始终使用 JavaScript 强制点击，因为这种方式更稳定，能绕过拦截问题
            driver.execute_script("arguments[0].click();", post_button)
            print("已通过 JavaScript 强制点击发帖按钮。")

        except TimeoutException as e:
            print(f"发帖按钮定位超时或不可点击: {e}。可能页面结构再次变化，请检查。")
            raise NoSuchElementException("未能成功定位或点击发帖按钮（超时）。")
        except Exception as e:
            # 捕获其他未知异常，包括 ElementClickInterceptedException 等
            print(f"点击发帖按钮时发生未知错误: {e}")
            raise NoSuchElementException(f"未能成功点击发帖按钮：{e}")
        
        # --- 增加发布成功后的等待条件 ---
        try:
            # 等待URL从COMPOSE_URL改变，这通常表示发布成功或页面已跳转
            # 将超时时间增加到 20 秒
            WebDriverWait(driver, 20).until(
                EC.url_changes(COMPOSE_URL) 
            )
            print("推文发布流程完成：URL已改变。")
        except TimeoutException:
            print("推文发布流程完成：URL未在预期时间内改变，但可能已发送。")
            # 此时可以尝试再次检查当前URL或是否有错误消息，以便进一步调试

    except TimeoutException:
        print("发布推文超时：未能找到关键元素或页面未按预期响应。")
    except NoSuchElementException as e: # 捕获更具体的异常，便于识别是哪个元素未找到
        print(f"发布推文失败：{e} 页面结构可能已更改。")
    except Exception as e:
        print(f"发布推文时发生未知错误: {e}")

def main():
    driver = None # 初始化 driver 为 None
    # 定义 unique_user_data_dir 在 main 函数范围内，以便 setup_driver 可以对其进行修改
    # 并在 finally 块中访问。
    global unique_user_data_dir 
    unique_user_data_dir = None

    try:
        driver = setup_driver()
        while True:
            print(f"\n{time.ctime()} - 开始获取趋势数据...")
            trending_tags = get_trending_tags(driver)
            
            if trending_tags:
                print(f"发现 {len(trending_tags)} 个趋势标签:")
                # 仅打印前5个标签，避免输出过长
                print('\n'.join(trending_tags[:5])) 
                
                print("\n准备发布推文...")
                post_tweet(driver, trending_tags)
            else:
                print("当前未获取到趋势标签。")
            
            print(f"\n等待 {INTERVAL_MINUTES} 分钟后继续下一次循环...")
            time.sleep(INTERVAL_MINUTES * 60)
            
    except KeyboardInterrupt:
        print("\n程序已终止。")
    except Exception as e:
        print(f"主程序发生未捕获的错误: {e}")
    finally:
        if driver: # 确保 driver 存在时才执行 quit()
            print("正在关闭浏览器...")
            driver.quit()
            # 尝试清理临时用户数据目录
            if unique_user_data_dir and os.path.exists(unique_user_data_dir): # 检查变量是否存在且目录存在
                try:
                    shutil.rmtree(unique_user_data_dir, ignore_errors=True)
                    print(f"已清理临时用户数据目录: {unique_user_data_dir}")
                except Exception as e:
                    print(f"清理临时用户数据目录失败: {e}")

if __name__ == "__main__":
    main()
