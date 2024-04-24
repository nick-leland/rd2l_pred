from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

driver.get("https://www.dotabuff.com/esports/leagues/15578-rd2l-season-31")

title = driver.title

driver.implicitly_wait(0.5)

text = driver.find_element(by=By.ID, value="viewport").text

driver.quit()

print(text)


