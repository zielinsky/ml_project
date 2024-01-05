from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
import time



chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True) #Browser stays opened after executing commands

service = Service(executable_path="ML_Project/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.maximize_window()

# driver.get("https://op.gg")
USER_NAME = "DBicek"
USER_HASH = "EUNE"
driver.get(f"https://www.op.gg/summoners/eune/{USER_NAME}-{USER_HASH}")


# search_bar = driver.find_element(By.ID, "searchHome")
# search_bar.send_keys("DBicek #EUNE" + Keys.ENTER)

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "css-47sehv"))
)

cookies = driver.find_element(By.CLASS_NAME, "css-47sehv")
cookies.click()


select = Select(driver.find_element("id", 'queueType'))
select.select_by_value("ARAM")


game_info_class_name = "css-j7qwjs e17hr80g0"

WebDriverWait(driver, 10).until(
    lambda driver: all(element.text == "ARAM" for element in driver.find_elements(By.CLASS_NAME, "game-type"))
)

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//div[@class="' + game_info_class_name + '"]'))
)


games = driver.find_elements(By.XPATH, '//div[@class="' + game_info_class_name + '"]')

games_count = 0

dict_array = []

for game in games:
    game = game.text.split("\n")
    dict_array.append({})
    dict_array[games_count]["kills"] = int(game[5].split(" / ")[0])
    dict_array[games_count]["assists"] = int(game[5].split(" / ")[1])
    dict_array[games_count]["deaths"] = int(game[5].split(" / ")[2])

    games_count += 1

print(dict_array[0])
