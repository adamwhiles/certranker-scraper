from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import EdgeOptions


# Make Edge Windows Headless
options = EdgeOptions()
options.add_argument("headless")
driver = webdriver.Edge(options = options)

# Microsoft Cert List URL
url = 'https://learn.microsoft.com/en-us/credentials/browse/?credential_types=certification'
driver.get(url)
# Setup array to hold certs
certs = []

has_next_page = True
# Loop through multiple pages if there are multiple
while has_next_page:
    # add a brief pause for subsequent pages to load
    driver.implicitly_wait(5)

    # locate the page element which has the exam code in it
    unfiltered_data = driver.find_elements(By.CLASS_NAME, 'is-comma-delimited')

    # loop through elements and store exam codes in certs array
    for span in unfiltered_data:
        text = span.get_attribute("textContent")
        certs.append(text.lstrip(" ")) # Remove leading space from scraped cert code

    # Find the next page button and go to next page
    try:
        next_page = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, 'pagination-next')))
        if next_page:
            next_page.click()
        else:
            has_next_page = False
            break
    except TimeoutException:
        has_next_page = False
        break
# print the identified cert codes
print(certs)