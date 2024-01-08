# Microsoft Certification Scraper

This Python script uses Selenium and the Edge driver to scrape information about Microsoft certifications and uploads it into a Cosmos DB.

- Cosmos DB portion is still in progress

## Prerequisites

Before you run this project you will need the following:
- Browser driver, in this case Edge: [https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH)
- A Cosmos DB account with SQL API, a database and container.
- Connetion details for the Cosmos DB
- Environmental variables for Cosmos DB Connection
- Python 3

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