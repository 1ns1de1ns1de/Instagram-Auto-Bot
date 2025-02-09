import csv
import os
import time
import random
import pickle
import traceback
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import chromedriver_autoinstaller
from tqdm import tqdm
from colorama import Fore, Style, init

# Initialize Colorama
init(autoreset=True)

# Install ChromeDriver if necessary
chromedriver_autoinstaller.install()

# Folders and Files
COOKIES_FOLDER = 'cookies'
DATA_FILE = 'data.txt'
MESSAGE_FILE = 'message.txt'
COMMENT_FILE = 'comment.txt'
CSV_LOG_FILE = 'dm_log.csv'
FOLLOW_LOG_FILE = 'follow_log.csv'
LIKE_COMMENT_LOG_FILE = 'like_comment_log.csv'

# Global variables
global default_delay_range
default_delay_range = (20, 50)  # Delay range in seconds

# =============================================================
# FUNCTION: init_chrome_driver
# =============================================================
def init_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")
    return webdriver.Chrome(options=chrome_options)

# =============================================================
# FUNCTION: load_cookies
# =============================================================
def load_cookies(driver, account_name):
    cookies_file = os.path.join(COOKIES_FOLDER, f"instagram_{account_name}.pkl")
    if os.path.exists(cookies_file):
        with open(cookies_file, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print(Fore.GREEN + f"Cookies loaded for Instagram account {account_name}.")
        time.sleep(5)
    else:
        print(Fore.YELLOW + f"Cookies not found for Instagram account {account_name}. Manual login required.")

# =============================================================
# FUNCTION: save_cookies
# =============================================================
def save_cookies(driver, account_name):
    cookies = driver.get_cookies()
    cookies_file = os.path.join(COOKIES_FOLDER, f"instagram_{account_name}.pkl")
    with open(cookies_file, 'wb') as file:
        pickle.dump(cookies, file)
    print(Fore.GREEN + f"Cookies saved for Instagram account {account_name}.")

# =============================================================
# FUNCTION: read_usernames
# =============================================================
def read_usernames(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(Fore.RED + f"File {file_path} not found.")
        return []

# =============================================================
# FUNCTION: read_usernames_and_messages
# =============================================================
def read_usernames_and_messages(data_file, message_file):
    try:
        with open(data_file, 'r', encoding='utf-8') as data:
            usernames = [line.strip() for line in data if line.strip()]
        with open(message_file, 'r', encoding='utf-8') as msg:
            messages = [line.strip() for line in msg if line.strip()]
        if len(messages) < len(usernames):
            messages = messages * (len(usernames) // len(messages) + 1)
        return list(zip(usernames, messages[:len(usernames)]))
    except FileNotFoundError as e:
        print(Fore.RED + f"File not found: {e}")
        return []

# =============================================================
# FUNCTION: read_comments
# =============================================================
def read_comments(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(Fore.RED + f"File {file_path} not found.")
        return []

# =============================================================
# FUNCTION: log_dm_result
# =============================================================
def log_dm_result(csv_file, username, status):
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Username', 'Status', 'Date'])
        writer.writerow([username, status, datetime.now().strftime("%Y-%m-%d")])

# =============================================================
# FUNCTION: log_follow_result
# =============================================================
def log_follow_result(csv_file, username, status):
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Username', 'Follow_Status', 'Date'])
        writer.writerow([username, status, datetime.now().strftime("%Y-%m-%d")])

# =============================================================
# FUNCTION: log_like_comment_result
# =============================================================
def log_like_comment_result(csv_file, username, like_status, comment_status):
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Username', 'Like_Status', 'Comment_Status', 'Date'])
        writer.writerow([username, like_status, comment_status, datetime.now().strftime("%Y-%m-%d")])

# =============================================================
# FUNCTION: format_message
# =============================================================
def format_message(message, username):
    username_clean = username.strip().lstrip("@").replace("\r", "").replace("\n", "")
    return message.replace("{username}", f"@{username_clean}")

# =============================================================
# FUNCTION: open_latest_post
# =============================================================
def open_latest_post(driver, username, debug=False):
    try:
        driver.get("https://www.instagram.com/" + username + "/")
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
        time.sleep(2)

        latest_post_selectors = [
            "//article//a[contains(@href, '/p/')]",
            "//article/div[1]//a[contains(@href, '/p/')]",
            "//div[contains(@class, '_aagv')]//a[contains(@href, '/p/')]",
            "//div[@class='_aabd _aa8k _aanf']",
            "//div[@class='_aagu']//a",
            "//div[contains(@style, 'flex-direction: column')]//a[contains(@href, '/p/')]"
        ]

        latest_post = None
        for selector in latest_post_selectors:
            try:
                posts = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.XPATH, selector))
                )
                if posts and len(posts) > 0:
                    latest_post = posts[0]
                    if latest_post.is_displayed():
                        break
            except:
                continue

        if not latest_post:
            raise Exception("No posts found")

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", latest_post)
        time.sleep(1)
        
        try:
            latest_post.click()
        except:
            try:
                driver.execute_script("arguments[0].click();", latest_post)
            except:
                ActionChains(driver).move_to_element(latest_post).click().perform()
        
        time.sleep(3)

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
        )

        if debug:
            print(Fore.GREEN + f"Opened latest post for {username} and overlay is visible.")
            
    except Exception as e:
        if debug:
            print(Fore.RED + "Error in open_latest_post: " + traceback.format_exc())
        raise e

# =============================================================
# FUNCTION: send_dm
# =============================================================
def send_dm(driver, username, message, debug=True):
    try:
        driver.get("https://www.instagram.com")
        time.sleep(3)
        try:
            search_selectors = [
                "svg[aria-label='Search']",
                "a[href='#'][role='link'] svg[aria-label='Search']",
                "//svg[@aria-label='Search']",
                "//span[text()='Search']",
                "//a[@role='link']//span[contains(text(), 'Search')]"
            ]
            search_button = None
            for selector in search_selectors:
                try:
                    if selector.startswith("//"):
                        element = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        element = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    if element.is_displayed():
                        search_button = element
                        if debug:
                            print(Fore.GREEN + f"Found search button using: {selector}")
                        break
                except:
                    continue
            if not search_button:
                print(Fore.RED + "Could not find search button")
                return "Failed to find search"
            search_button.click()
            time.sleep(2)
            search_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Search input']"))
            )
            search_input.clear()
            search_input.send_keys(username)
            time.sleep(3)
            user_element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{username}')]"))
            )
            user_element.click()
            time.sleep(3)
            message_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='button'][contains(text(), 'Message')]"))
            )
            message_button.click()
            time.sleep(2)
            message_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true'][aria-label='Message']"))
            )
            message_input.clear()
            message_input.send_keys(message)
            time.sleep(1)
            message_input.send_keys(Keys.ENTER)
            time.sleep(2)
            print(Fore.GREEN + f"DM sent to {username}")
            return "Sent"
        except Exception as e:
            if debug:
                print(Fore.RED + f"Error in sending process: {str(e)}")
            return "Failed to send DM"
    except Exception as e:
        if debug:
            print(Fore.RED + f"General error: {str(e)}")
        return "Error"

# =============================================================
# FUNCTION: like_latest_post
# =============================================================
def like_latest_post(driver, username, debug=False):
    try:
        open_latest_post(driver, username, debug)
        time.sleep(2)
        
        like_status_selectors = [
            "//article//div[@role='button']//span[.//*[@aria-label='Like' or @aria-label='Unlike']]/.."
        ]
        
        like_button = None
        button_status = None
        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, like_status_selectors[0]))
            )
            if element.is_displayed():
                svg = element.find_element(By.TAG_NAME, "svg")
                button_status = svg.get_attribute('aria-label')
                like_button = element
                if debug:
                    print(Fore.YELLOW + f"Found button with status: {button_status}")
        except Exception as e:
            if debug:
                print(Fore.YELLOW + f"Error finding like button: {str(e)}")

        if button_status == 'Unlike':
            print(Fore.YELLOW + f"Post already liked for {username}")
            return "Already Liked"
            
        if not like_button:
            return "Failed to find like button"

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", like_button)
        time.sleep(1)
        
        try:
            actions = ActionChains(driver)
            actions.move_to_element(like_button)
            actions.click()
            actions.perform()
        except Exception as e:
            if debug:
                print(Fore.RED + f"Error clicking like button: {str(e)}")
            return "Failed to click like"
            
        time.sleep(2)
        print(Fore.GREEN + f"Liked latest post of {username}")
        return "Liked"
        
    except Exception as e:
        if debug:
            print(Fore.RED + f"Error in like_latest_post: {str(e)}")
        return "Error"

# =============================================================
# FUNCTION: comment_latest_post
# =============================================================
def comment_latest_post(driver, username, comment, debug=False):
    try:
        formatted_comment = format_message(comment, username)
        open_latest_post(driver, username, debug)
        time.sleep(3)
        
        textarea_selector = "//form//textarea[@placeholder='Add a comment…']"
        
        def find_and_input_comment():
            textarea = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, textarea_selector))
            )
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", textarea)
            time.sleep(2)
            
            textarea = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, textarea_selector))
            )
            
            actions = ActionChains(driver)
            actions.move_to_element(textarea)
            actions.click()
            actions.send_keys(formatted_comment)
            actions.perform()
            
            return True

        max_retries = 3
        for attempt in range(max_retries):
            try:
                if find_and_input_comment():
                    break
            except Exception as e:
                if debug:
                    print(Fore.YELLOW + f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise e
                time.sleep(2)
                continue

        time.sleep(2)

        post_button_xpath = "//div[text()='Post']"
        post_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, post_button_xpath))
        )
        
        actions = ActionChains(driver)
        actions.move_to_element(post_button)
        actions.click()
        actions.perform()
        
        time.sleep(2)
        print(Fore.GREEN + f"Commented on latest post of {username}")
        return "Commented"
        
    except Exception as e:
        if debug:
            print(Fore.RED + f"Error commenting: {str(e)}")
        return "Error"

# =============================================================
# FUNCTION: follow_user_instagram
# =============================================================
def follow_user_instagram(driver, username, debug=False):
    try:
        driver.get("https://www.instagram.com/" + username + "/")
        time.sleep(3)

        follow_button_selectors = [
            "button._acan._acap._acas._aj1-",
            "//button[contains(@class, '_acan') and contains(@class, '_acap')]",
            "//button//div[contains(@class, '_ap3a')]//div[text()='Follow']/..",
            "//section[contains(@class, 'x1xdureb')]//button[.//div[text()='Follow']]",
            "button[type='button']:has(div:contains('Follow'))"
        ]

        following_check = "//button[.//div[text()='Following']]"
        try:
            if driver.find_elements(By.XPATH, following_check):
                print(Fore.YELLOW + f"Already following {username}")
                return "Already Following"
        except:
            pass

        follow_button = None
        for selector in follow_button_selectors:
            try:
                if selector.startswith("//"):
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                else:
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                if element.is_displayed():
                    follow_button = element
                    if debug:
                        print(Fore.GREEN + f"Found follow button using: {selector}")
                    break
            except:
                if debug:
                    print(Fore.YELLOW + f"Failed with selector: {selector}")
                continue

        if not follow_button:
            if debug:
                print(Fore.YELLOW + f"Follow button not found for {username}")
            return "Failed to find follow button"

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", follow_button)
        time.sleep(1)

        actions = ActionChains(driver)
        actions.move_to_element(follow_button)
        actions.click()
        actions.perform()
        time.sleep(2)

        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, following_check))
            )
            print(Fore.GREEN + f"Successfully followed {username}")
            return "Followed"
        except:
            if debug:
                print(Fore.RED + f"Failed to verify follow status for {username}")
            return "Failed to verify follow"

    except Exception as e:
        if debug:
            print(Fore.RED + f"Error following {username}: {str(e)}")
        return "Error"

# =============================================================
# FUNCTION: start_interaction_instagram
# =============================================================
def start_interaction_instagram():
    account_name = input(Fore.LIGHTYELLOW_EX + "Enter Instagram account name: ").strip()
    driver = init_chrome_driver()
    
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)
    load_cookies(driver, account_name)
    if not any(cookie['name'] == 'sessionid' for cookie in driver.get_cookies()):
        print(Fore.LIGHTYELLOW_EX + "Manual login required.")
        input(Fore.LIGHTMAGENTA_EX + "Press Enter after logging in...")
        save_cookies(driver, account_name)
    
    usernames = read_usernames(DATA_FILE)
    comments = read_comments(COMMENT_FILE)
    if not usernames:
        print(Fore.LIGHTRED_EX + "Username list is empty. Script stopped.")
        driver.quit()
        return
    if not comments:
        print(Fore.LIGHTRED_EX + "Comment list is empty. Script stopped.")
        driver.quit()
        return
    if len(comments) < len(usernames):
        comments = comments * (len(usernames) // len(comments) + 1)
    
    print(Fore.CYAN + f"Starting Like & Comment process with delay range: {default_delay_range[0]}-{default_delay_range[1]} seconds")
    for username, comment in tqdm(zip(usernames, comments[:len(usernames)]), total=len(usernames), desc="Processing", unit="user"):
        like_status = like_latest_post(driver, username, debug=True)
        time.sleep(2)
        comment_status = comment_latest_post(driver, username, comment, debug=True)
        log_like_comment_result(LIKE_COMMENT_LOG_FILE, username, like_status, comment_status)
        delay = random.randint(*default_delay_range)
        print(Fore.LIGHTMAGENTA_EX + f"Waiting for {delay} seconds before next interaction...")
        time.sleep(delay)
    print(Fore.GREEN + "\nLike & Comment process completed!")
    driver.quit()

# =============================================================
# FUNCTION: start_follow_instagram
# =============================================================
def start_follow_instagram():
    account_name = input(Fore.LIGHTYELLOW_EX + "Enter Instagram account name: ").strip()
    driver = init_chrome_driver()
    
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)
    load_cookies(driver, account_name)
    if not any(cookie['name'] == 'sessionid' for cookie in driver.get_cookies()):
        print(Fore.LIGHTYELLOW_EX + "Manual login required.")
        input(Fore.LIGHTMAGENTA_EX + "Press Enter after logging in...")
        save_cookies(driver, account_name)
    
    usernames = read_usernames(DATA_FILE)
    if not usernames:
        print(Fore.LIGHTRED_EX + "Username list is empty. Script stopped.")
        driver.quit()
        return
    
    print(Fore.CYAN + "Starting Follow process...")
    for username in tqdm(usernames, desc="Following", unit="user"):
        status = follow_user_instagram(driver, username, debug=True)
        print(f"Follow status for {username}: {status}")
        log_follow_result(FOLLOW_LOG_FILE, username, status)
        delay = random.randint(*default_delay_range)
        print(Fore.LIGHTMAGENTA_EX + f"Waiting for {delay} seconds before next follow...")
        time.sleep(delay)
    print(Fore.GREEN + "Follow process completed!")
    driver.quit()

# =============================================================
# FUNCTION: start_selenium_instagram
# =============================================================
def start_selenium_instagram():
    account_name = input(Fore.LIGHTYELLOW_EX + "Enter Instagram account name: ").strip()
    driver = init_chrome_driver()
    
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)
    load_cookies(driver, account_name)
    if not any(cookie['name'] == 'sessionid' for cookie in driver.get_cookies()):
        print(Fore.LIGHTYELLOW_EX + "Manual login required.")
        input(Fore.LIGHTMAGENTA_EX + "Press Enter after logging in...")
        save_cookies(driver, account_name)
    
    print(Fore.GREEN + f"Selenium ready for Instagram account {account_name}.")
    driver.quit()

# =============================================================
# FUNCTION: start_auto_dm
# =============================================================
def start_auto_dm():
    global default_delay_range
    account_name = input(Fore.LIGHTYELLOW_EX + "Enter Instagram account name: ").strip()
    driver = init_chrome_driver()
    
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)
    load_cookies(driver, account_name)
    if not any(cookie['name'] == 'sessionid' for cookie in driver.get_cookies()):
        print(Fore.LIGHTYELLOW_EX + "Manual login required.")
        input(Fore.LIGHTMAGENTA_EX + "Press Enter after logging in...")
        save_cookies(driver, account_name)
    
    user_messages = read_usernames_and_messages(DATA_FILE, MESSAGE_FILE)
    if not user_messages:
        print(Fore.LIGHTRED_EX + "Username list or message list is empty. Script stopped.")
        driver.quit()
        return
    
    print(Fore.CYAN + f"Starting to send DMs with delay range: {default_delay_range[0]}-{default_delay_range[1]} seconds")
    for username, message in tqdm(user_messages, desc="Sending DMs", unit="user"):
        status = send_dm(driver, username, message, debug=False)
        log_dm_result(CSV_LOG_FILE, username, status)
        delay = random.randint(*default_delay_range)
        print(Fore.LIGHTMAGENTA_EX + f"Waiting for {delay} seconds before next DM...")
        time.sleep(delay)
    print(Fore.GREEN + "\nDM sending process completed!")
    driver.quit()

# =============================================================
# FUNCTION: update_delay_settings
# =============================================================
def update_delay_settings():
    global default_delay_range
    try:
        print(Fore.CYAN + "\nCurrent delay range:", default_delay_range)
        min_delay = int(input(Fore.LIGHTYELLOW_EX + "Enter minimum delay (in seconds): "))
        max_delay = int(input(Fore.LIGHTYELLOW_EX + "Enter maximum delay (in seconds): "))
        if min_delay > 0 and max_delay > min_delay:
            default_delay_range = (min_delay, max_delay)
            print(Fore.GREEN + f"Delay range updated to: {default_delay_range} seconds")
        else:
            print(Fore.RED + "Invalid input. Max delay must be greater than min delay and both must be positive.")
    except ValueError:
        print(Fore.RED + "Invalid input. Please enter numbers only.")

# =============================================================
# FUNCTION: main_menu
# =============================================================
def main_menu():
    print(Fore.MAGENTA + """
     ██╗███╗   ██╗███████╗ ██╗██████╗ ███████╗
     ██║████╗  ██║██╔════╝███║██╔══██╗██╔════╝
     ██║██╔██╗ ██║███████╗╚██║██║  ██║█████╗  
     ██║██║╚██╗██║╚════██║ ██║██║  ██║██╔══╝  
     ██║██║ ╚████║███████║ ██║██████╔╝███████╗
     ╚═╝╚═╝  ╚═══╝╚══════╝ ╚═╝╚═════╝ ╚══════╝
           Instagram Auto Bot v1.4                      
═══════════════════════════════════════════════
"""+Style.RESET_ALL)
    while True:
        print(Fore.LIGHTMAGENTA_EX + "\nChoose an option:")
        print(Fore.LIGHTCYAN_EX + "1. Start Selenium (manual login and save cookies)")
        print(Fore.LIGHTCYAN_EX + "2. Update Delay Settings")
        print(Fore.LIGHTCYAN_EX + "3. Start Auto DM Instagram")
        print(Fore.LIGHTCYAN_EX + "4. Like & Comment Latest Posts")
        print(Fore.LIGHTCYAN_EX + "5. Follow Users")
        print(Fore.LIGHTCYAN_EX + "6. Exit")
        choice = input(Fore.LIGHTYELLOW_EX + "Enter your choice (1/2/3/4/5/6): ")
        if choice == '1':
            start_selenium_instagram()
        elif choice == '2':
            update_delay_settings()
        elif choice == '3':
            start_auto_dm()
        elif choice == '4':
            start_interaction_instagram()
        elif choice == '5':
            start_follow_instagram()
        elif choice == '6':
            print(Fore.LIGHTRED_EX + "Exiting the program.")
            break
        else:
            print(Fore.LIGHTRED_EX + "Invalid choice. Please try again.")

if __name__ == "__main__":
    if not os.path.exists(COOKIES_FOLDER):
        os.makedirs(COOKIES_FOLDER)
    
    # Ensure all CSV log files exist
    for csv_file in [CSV_LOG_FILE, FOLLOW_LOG_FILE, LIKE_COMMENT_LOG_FILE]:
        if not os.path.exists(csv_file):
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if csv_file == CSV_LOG_FILE:
                    writer.writerow(['Username', 'Status', 'Date'])
                elif csv_file == FOLLOW_LOG_FILE:
                    writer.writerow(['Username', 'Follow_Status', 'Date'])
                elif csv_file == LIKE_COMMENT_LOG_FILE:
                    writer.writerow(['Username', 'Like_Status', 'Comment_Status', 'Date'])
    
    main_menu()
                    
