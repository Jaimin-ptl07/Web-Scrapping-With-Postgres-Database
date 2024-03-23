import os
import pandas as pd
import wikipediaapi
import psycopg2


def create_table_if_not_exists(connection):
    # Creating a table if it doesn't exist
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_wikipedia_info (
                company_name VARCHAR(255) PRIMARY KEY,
                wikipedia_info TEXT
            )
        """)
    connection.commit()


def insert_into_table(connection, company_name, wikipedia_info):
    # Inserting data into the table
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO company_wikipedia_info (company_name, wikipedia_info)
            VALUES (%s, %s)
            ON CONFLICT (company_name) DO NOTHING
        """, (company_name, wikipedia_info))
    connection.commit()


def scrape_wikipedia(company_name):
    user_agent = 'MyCompanyScraper/1.0 pateljaimin1707@gmail.com'
    wiki_wiki = wikipediaapi.Wikipedia(user_agent)
    page_py = wiki_wiki.page(company_name)

    if not page_py.exists():
        return f"No information found for {company_name}"

    # Create a directory to store text files if it doesn't exist
    if not os.path.exists('company_files'):
        os.makedirs('company_files')

    # Create a text file for each company
    file_path = os.path.join('company_files', f"{company_name}.txt")
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(page_py.text)

    return file_path


def read_text_file(file_path):
    # Read the contents of the text file
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def main():
    # Replace 'your_file.xlsx' with the actual path to your XLS file
    xls_file_path = 'test_company_list.xlsx'

    # Replace these with your PostgreSQL connection details
    db_params = {
        'dbname': 'postgres',
        'user': 'postgres',
        'password': 'jaimin07',
        'host': 'localhost',
        'port': '5432'
    }

    connection = psycopg2.connect(**db_params)

    create_table_if_not_exists(connection)

    # Read the XLS file into a DataFrame
    df = pd.read_excel(xls_file_path)

    # Assuming that the column containing company names is named 'Company'
    company_names = df['Company Name'].tolist()

    for company_name in company_names:
        file_path = scrape_wikipedia(company_name)
        wikipedia_info = read_text_file(file_path)
        insert_into_table(connection, company_name, wikipedia_info)
        print(f"Information for {company_name} stored in the database.")

    connection.close()


if __name__ == "__main__":
    main()
