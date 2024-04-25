from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
import pandas as pd

# This will change for each individual user
# driver = webdriver.Chrome("/home/spiffy/Downloads/chromedriver-linux64")
driver = webdriver.Chrome()

driver.get("https://www.dotabuff.com/esports/leagues/15578-rd2l-season-31/series")

# title = driver.title
# Both excluded in medium article for some reason
# driver.implicitly_wait(2.5)

# text = driver.find_element(by=By.ID, value="viewport").text

# pages = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[3]/div[5]/section[2]/div/article/div[2]')
pages = driver.find_element(By.CLASS_NAME, "viewport")

driver.close()

print(type(pages))
print("\n")
# print(pages.is_displayed())
# Any . command after the pages variable results in an error.
print("\n")
# For some reason this outputs an error, no text associated?
print(pages)


