import tabula
import pandas as pd
import psycopg2
import os

def is_valid_table(table, min_non_null=1, max_null_percentage=0.8):
    # Check if the table has at least 'min_non_null' non-null values
    # and the percentage of null values is below 'max_null_percentage'
    non_null_count = table.count().sum()
    total_cells = table.size
    null_percentage = (total_cells - non_null_count) / total_cells

    return non_null_count >= min_non_null and null_percentage <= max_null_percentage

def extract_tables_from_pdf(pdf_path, min_non_null=1, max_null_percentage=0.8):
    # Read PDF and extract tables
    tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)

    # Display the valid extracted tables
    for i, table in enumerate(tables, start=1):
        if is_valid_table(table, min_non_null=min_non_null, max_null_percentage=max_null_percentage):
            print(f"Table {i}:")
            df = pd.DataFrame(table)
            print(df)
            print("\n" + "-"*30 + "\n")  # Separator between tables

def get_pdf_location_from_database():
    # Connect to PostgreSQL database
    connection = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="jaimin07"
    )

    # Create a cursor object
    cursor = connection.cursor()

    try:
        # Execute SQL query to retrieve PDF location from company_report table
        cursor.execute("SELECT pdf_location FROM company_report;")

        # Fetch the PDF location from the result
        pdf_location = cursor.fetchone()

        return pdf_location
    finally:
        # Close cursor and connection
        cursor.close()
        connection.close()

def store_table_in_database(table, table_number):
    # Connect to PostgreSQL database
    connection = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="jaimin07"
    )

    # Create a cursor object
    cursor = connection.cursor()

    try:
        # Create a table in the database to store the extracted data
        create_table_query = f"CREATE TABLE IF NOT EXISTS extracted_table_{table_number} (id SERIAL PRIMARY KEY, {', '.join(['col{} TEXT'.format(idx) for idx, col in enumerate(table.columns)])});"
        cursor.execute(create_table_query)

        # Insert data into the table
        for index, row in table.iterrows():
            insert_data_query = f"INSERT INTO extracted_table_{table_number} ({', '.join(['col{}'.format(idx) for idx in range(len(table.columns))])}) VALUES ({', '.join(['%s' for _ in range(len(table.columns))])});"
            cursor.execute(insert_data_query, tuple(row))

        # Commit the changes
        connection.commit()
    finally:
        # Close cursor and connection
        cursor.close()
        connection.close()

if __name__ == "__main__":
    # Set the minimum number of non-null values required in a table
    min_non_null_values = 5
    # Set the maximum percentage of null values allowed in a table
    max_null_percentage = 0.8

    # Get the PDF location from the database
    try:
        pdf_location = get_pdf_location_from_database()

        if pdf_location is not None:
            # Access the value of pdf_location directly
            pdf_location_value = pdf_location[0]

            # Use os.path to create a full path
            full_pdf_path = os.path.join("C:/Users/JAIMIN/Desktop/WorldEconomicEngine/reports", pdf_location_value)

            print("PDF Location Value (Full Path):", full_pdf_path)

            # Extract tables from the PDF file
            tables = tabula.read_pdf(full_pdf_path, pages='all', multiple_tables=True)

            # Store the valid extracted tables in the database
            for i, table in enumerate(tables, start=1):
                if is_valid_table(table, min_non_null=min_non_null_values, max_null_percentage=max_null_percentage):
                    print(f"Storing Table {i} in the database:")
                    df = pd.DataFrame(table)
                    print(df)

                    # Store the table in the database
                    try:
                        store_table_in_database(df, i)
                        print(f"Table {i} stored successfully in the database.")
                    except Exception as e:
                        print(f"Error storing table {i} in the database: {e}")

                    print("\n" + "-" * 30 + "\n")  # Separator between tables
        else:
            print("No PDF Location found.")
    except Exception as e:
        print(f"Error: {e}")