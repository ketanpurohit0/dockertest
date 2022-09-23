from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
opts = Options()
#opts.headless = True
opts.binary_location = "C:\\Program Files (x86)\\Google\\Chrome\Application\\chrome.exe"
#assert opts.headless  # Operating in headless mode
#chrome_driver_path = Path(r'C:\MyInstalled\chromedriver\chromedriver.exe')
driver = Chrome(ChromeDriverManager(version = '105.0.5195.52').install(), options=opts)
driver.get('https://duckduckgo.com')

search_form = driver.find_element_by_id('search_form_input_homepage')
search_form.send_keys('real python')
search_form.submit()
results = driver.find_elements_by_class_name('result')
print(results[0].text)
driver.close()
driver.quit()

