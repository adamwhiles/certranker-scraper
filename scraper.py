import os
import time
import re
import pyodbc, struct
from azure import identity
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import EdgeOptions
from openai import OpenAI

# Configuration
load_dotenv()
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API"))
connection_string = os.environ.get("AZURE_SQL_CONNECTIONSTRING")

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

def get_default_edge_options():
    options = webdriver.EdgeOptions()
    options.add_argument("--headless=new")
    return options

# Selenium Setup
options = get_default_edge_options()
driver = webdriver.Edge(options=options)


print("Accessing page...")
driver.get("https://github.com/JurgenOnAzure/all-the-exams")
time.sleep(3)  # Allow page to load

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
        if text in SECTIONS_OF_INTEREST:
            current_section = text
            exams_data.setdefault(current_section, [])
            current_certification = None
            continue
        
        if current_section is not None:
            if text.endswith(":"):
                text = text[:-1].strip()
            else:
                current_section = None
                current_certification = None
                continue
            
            current_certification = text

    elif tag_name == "ul" and current_section is not None and current_certification is not None:
        lis = elem.find_elements(By.TAG_NAME, "li")
        for li in lis:
            anchor = li.find_element(By.TAG_NAME, "a")  # Find the link inside <li>
            line = anchor.text.strip()
            url = anchor.get_attribute("href")  # Extract the URL
            
            match = exam_line_pattern.match(line)
            if match:
                exam_code = match.group(1)
                exams_data[current_section].append((exam_code, current_certification, url))

# Exam Class
class Exam:
    def __init__(self, code, name, description, url):
        self.short_name = code
        self.name = name
        self.description = description
        self.url = url

# Helper Functions
def getDescription(cert_code):
    prompt = f"Give me a short description of the {cert_code} Microsoft exam, including its objectives and target audience."
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return ' '.join(response.choices[0].message.content.splitlines())

# Set up SQL Connection
def get_conn():
    credential = identity.DefaultAzureCredential(exclude_interactive_browser_credential=False)
    token_bytes = credential.get_token("https://database.windows.net/.default").token.encode('UTF-16-LE')
    token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
    SQL_COPT_SS_ACCESS_TOKEN = 1256
    conn = pyodbc.connect(connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
    return conn

def add_exam(exam):
    with get_conn() as conn:
        cursor = conn.cursor()
        # Check if the certification already exists by short_name or name
        cursor.execute("SELECT COUNT(*) FROM Certifications WHERE short_name = ? OR name = ?", exam.short_name, exam.name)
        if cursor.fetchone()[0] > 0:
            print(f"Certification with short_name {exam.short_name} or name {exam.name} already exists. Skipping insertion.")
            return
        
        # Insert the new certification
        cursor.execute(
            "INSERT INTO Certifications (short_name, name, description, url, vendor, submitted_by) VALUES (?, ?, ?, ?, ?, ?)",
            exam.short_name, exam.name, exam.description, exam.url, "Microsoft", "80314c8f-0471-4ece-9bbb-4442cc156730"
        )
        conn.commit()
    print(f"Exam Code: {exam.short_name}, Name: {exam.name}, URL: {exam.url}")

# Add to SQL Database
for section, items in exams_data.items():
    for code, cert_name, url in items:
        description = getDescription(code)
        exam_obj = Exam(code, cert_name, description, url)  # Use extracted URL
        add_exam(exam_obj)

driver.quit()