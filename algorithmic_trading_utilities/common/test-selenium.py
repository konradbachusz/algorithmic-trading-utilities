#TODO remove once working
from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument("--incognito")

driver = webdriver.Chrome(options=options)
driver.get('https://www.ft.com/content/ece272c3-de7e-47ac-ae1e-2d125d6ada80')
print(driver.title)
print(driver.get_cookies())
driver.quit()
