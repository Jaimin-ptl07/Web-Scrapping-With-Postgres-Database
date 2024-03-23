import os
import time
import openpyxl
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import psycopg2

def create_company_report_table(cursor):
    try:
        # Updated SQL statement to create the 'company_report' table
        sql = """
        CREATE TABLE IF NOT EXISTS company_report (
            id SERIAL PRIMARY KEY,
            company_name VARCHAR(255),
            pdf_location VARCHAR(255)
        );
        """
        cursor.execute(sql)
    except Exception as e:
        print(f"Error creating 'company_report' table: {e}")

def insert_into_postgres(cursor, company_name, pdf_location):
    try:
        # Updated SQL statement to insert data into 'company_report' table
        sql = "INSERT INTO company_report (company_name, pdf_location) VALUES (%s, %s);"
        cursor.execute(sql, (company_name, pdf_location))
    except Exception as e:
        print(f"Error inserting into 'company_report' table: {e}")

def extract_pdf_links(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.pdf')]
        return pdf_links
    else:
        print(f"Failed to fetch HTML content for {url}. Status code: {response.status_code}")
        return []

def search_and_extract(company_name, cursor):
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://www.google.com/")
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(f"private equity research {company_name}")
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)

        search_results = driver.find_elements(By.CSS_SELECTOR, "div.tF2Cxc")

        for result in search_results:
            link = result.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            print(link)

            # Extract PDF links from the search result page
            pdf_links = extract_pdf_links(link)

            for pdf_link in pdf_links:
                pdf_filename = pdf_link.split("/")[-1]
                response = requests.get(pdf_link, stream=True)

                # Specify the directory where you want to store the downloaded PDFs
                download_directory = 'C:/Users/JAIMIN/Desktop/WorldEconomicEngine/reports/'
                pdf_location = os.path.join(download_directory, pdf_filename)

                with open(pdf_location, 'wb') as pdf_file:
                    for chunk in response.iter_content(chunk_size=128):
                        pdf_file.write(chunk)
                print(f"Downloaded: {pdf_filename}")

                # Insert PDF information into 'company_report' table with location
                insert_into_postgres(cursor, company_name, pdf_location)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()

# Connect to PostgreSQL
connection = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="jaimin07"
)

cursor = connection.cursor()

# Create 'company_report' table if it doesn't exist
create_company_report_table(cursor)

# Load the Excel file
excel_file_path = 'test_company_list.xlsx'
workbook = openpyxl.load_workbook(excel_file_path)
sheet = workbook.active

# Iterate through each row in the Excel file
for row in sheet.iter_rows(min_row=2, values_only=True):
    company_name = row[2]
    search_and_extract(company_name, cursor)

# Commit changes and close the connection
connection.commit()
cursor.close()
connection.close()
