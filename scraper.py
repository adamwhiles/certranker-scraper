import os
import time
import re
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import EdgeOptions
from openai import OpenAI
from azure.cosmos import CosmosClient

# Configuration
load_dotenv()
# Initialize OpenAI client
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API"))

# Azure Cosmos DB setup
connection_string = os.environ.get("CONNECTION_STRING")
cosmos_client = CosmosClient.from_connection_string(conn_str=connection_string)
database = cosmos_client.get_database_client(os.environ.get("DB_NAME"))
container = database.get_container_client(os.environ.get("CONTAINER_NAME"))

# Sections of interest in the README
SECTIONS_OF_INTEREST = {
    "AI exams",
    "AZ exams",
    "DP exams",
    "MB exams",
    "MD exams",
    "MO exams",
    "MS exams",
    "PL exams",
    "SC exams"
}

# Selenium Setup
options = EdgeOptions()
options.add_argument("headless")
driver = webdriver.Edge(options=options)

print("Accessing page...")
driver.get("https://github.com/JurgenOnAzure/all-the-exams")
time.sleep(3)  # Simple wait for page load

# Data Extraction
exams_data = {}

markdown_body = driver.find_element(By.CSS_SELECTOR, "article.markdown-body")
all_elements = markdown_body.find_elements(By.XPATH, "./*")

current_section = None
current_certification = None

# Regex for lines like: "Exam AZ-900: Microsoft Azure Fundamentals"
exam_line_pattern = re.compile(r"^Exam\s+([A-Z]{2,3}-\d{2,4})\s*:\s*(.+)$", re.IGNORECASE)

for elem in all_elements:
    tag_name = elem.tag_name.lower()
    text = elem.text.strip()
    
    if tag_name == "div":
        # Check if this <div> is a recognized section
        if text in SECTIONS_OF_INTEREST:
            current_section = text
            exams_data.setdefault(current_section, [])
            current_certification = None
            continue
        
        # If already in a recognized section, this may be the certification name
        if current_section is not None:
            # Typically ends with a colon (e.g. "Microsoft Certified: Azure Administrator Associate:")
            if text.endswith(":"):
                text = text[:-1].strip()
            else:
                # If not a normal cert line, we assume a new or unrelated heading => stop tracking
                current_section = None
                current_certification = None
                continue
            
            current_certification = text

    elif tag_name == "ul" and current_section is not None and current_certification is not None:
        # Each <li> might contain "Exam <code>: <exam title>"
        lis = elem.find_elements(By.TAG_NAME, "li")
        for li in lis:
            line = li.text.strip()
            match = exam_line_pattern.match(line)
            if match:
                exam_code = match.group(1)
                # We store the code and the certification name as a tuple
                exams_data[current_section].append((exam_code, current_certification))

# Exam Class
class Exam:
    def __init__(self, code, name, description, url):
        self.id = code
        self.name = name
        self.description = description
        self.url = url
        self.resources = []

# Helper Functions
def getDescription(cert_code):
    prompt = f"Give me a short description of the {cert_code} Microsoft exam, including its cost."
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return ' '.join(response.choices[0].message.content.splitlines())

def add_exam(exam):
    container.upsert_item(exam.__dict__)

# Add to Cosmos DB
for section, items in exams_data.items():
    for code, cert_name in items:
        description = getDescription(code)
        exam_obj = Exam(code, cert_name, description, "https://learn.microsoft.com")
        add_exam(exam_obj)

driver.quit()

