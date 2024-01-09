from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import EdgeOptions
import os
from dotenv import load_dotenv
from openai import OpenAI
from azure.cosmos import CosmosClient, exceptions

load_dotenv()

# Make Edge Windows Headless
options = EdgeOptions()
options.add_argument("headless")
driver = webdriver.Edge(options = options)

# OpenAI API key
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API"))

# Exam Objects Array
exams_objects = []

# Azure CosmosDB Setup
connection_string = os.environ.get("CONNECTION_STRING")
cosmos_client = CosmosClient.from_connection_string(conn_str=connection_string)
database = cosmos_client.get_database_client(os.environ.get("DB_NAME"))
container = database.get_container_client(os.environ.get("CONTAINER_NAME"))

# Exam Class
class Exam:
    def __init__(self, code, name, description, url):
        self.id = code
        self.name = name
        self.description = description
        self.url = url
        self.resources = []

# Send prompt to OpenAI API to get description for the certification, returns a formatted prompt response
def getDescription(cert_code):
    prompt = f"Give me a short description of the {cert_code} Microsoft exam, including its cost."
    response = openai_client.chat.completions.create(
        model = "gpt-4-1106-preview",
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    return ' '.join(response.choices[0].message.content.splitlines())

# Scrape the Microsoft Exam site and return an array of exam codes
def getExams():
    # Microsoft Exam List URL
    url = 'https://learn.microsoft.com/en-us/credentials/browse/?credential_types=examination'
    driver.get(url)

    has_next_page = True
    # Loop through multiple pages if there are multiple
    while has_next_page:
        # add a brief pause for subsequent pages to load
        driver.implicitly_wait(1)

        # locate the page element which has the exam code in it
        unfiltered_data = driver.find_elements(By.CLASS_NAME, 'card-title')

        # loop through elements and store exam codes in exams array
        if unfiltered_data:
            for element in unfiltered_data:
                text = element.text
                exam_name = text.split(": ")[1]
                href_link = element.get_attribute("href")
                exam_code = text.replace("Exam", "").split(":")[0]

                # Generate description from ChatGPT
                description = getDescription(exam_code)

                # Create Exam object and add to array
                exams_objects.append(Exam(exam_code, exam_name, description, href_link))

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
        else:
            break
def add_exam(exam):
    if exam:
        container.upsert_item(exam.__dict__)

getExams()
if exams_objects:
    for exam in exams_objects:
        add_exam(exam)
