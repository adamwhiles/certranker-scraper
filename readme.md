# Microsoft Certification Scraper

This Python script uses Selenium and the Edge driver to scrape information about Microsoft exams and then use the OpenAI API to generate a short description for each exam. Once everything is collected it is uploaded into Cosmos DB.

## Prerequisites

Before you run this project you will need the following:

- Browser driver, in this case Edge: [https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH)
- Python ODBC Driver [https://learn.microsoft.com/en-us/sql/connect/python/pyodbc/step-1-configure-development-environment-for-pyodbc-python-development?view=sql-server-ver16&tabs=linux#install-the-odbc-driver](https://learn.microsoft.com/en-us/sql/connect/python/pyodbc/step-1-configure-development-environment-for-pyodbc-python-development?view=sql-server-ver16&tabs=linux#install-the-odbc-driver)
- An Azure SQL Database (Serverless is what I used)
- Python 3
- OpenAI API Account and Credits

Necessary Environment Variables

```
OPENAI_API - OpenAI API Key
AZURE_SQL_CONNECTIONSTRING='Driver={ODBC Driver 18 for SQL Server};Server=tcp:SERVERNAME.database.windows.net,1433;Database=DBNAME;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'
```

## Installation

Create a Python Virtual Environment, clone this repository and install dependencies:

```
pip install venv
git clone https://github.com/adamwhiles/msvote-scraper.git
cd msvote-scraper
python3 -m venv my_env
source my_env/bin/activate
pip install -r requirements.txt

```

## Usage

```
python3 scraper.py
```
